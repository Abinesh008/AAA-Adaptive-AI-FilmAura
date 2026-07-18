import asyncio
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.recommendation.interfaces.client import BaseRecommendationClient
from app.recommendation.feature_store import feature_store
from app.recommendation.cold_start import cold_start_engine
from app.recommendation.experimentation import experimentation_engine
from app.recommendation.plugins import plugin_registry
from app.recommendation.scorer import multi_stage_scorer
from app.recommendation.policies import policy_chain
from app.recommendation.guardrails import recommendation_guardrails
from app.recommendation.explainability import recommendation_explainer
from app.recommendation.cache import recommendation_cache
from app.recommendation.telemetry import recommendation_telemetry
from app.recommendation.feedback import feedback_pipeline
from app.retrieval.query_trace import QueryTrace
from app.core.logging import get_logger

logger = get_logger("app.recommendation.sdk")

class RecommendationClient(BaseRecommendationClient):
    """
    Production-grade Recommendation SDK client.
    The primary stable public entry point for all recommendation retrieval requests.
    """
    async def get_recommendations(
        self,
        user_id: str,
        limit: int = 10,
        region: Optional[str] = None,
        subscription_tier: Optional[str] = "free",
        is_child_profile: bool = False,
        db: Session = None
    ) -> Dict[str, Any]:
        logger.info(f"SDK get_recommendations called for user: {user_id}")
        
        # 1. Check recommendation cache
        cached_result = await recommendation_cache.get_cached_recommendations(user_id)
        if cached_result is not None:
            # Reconstruct response envelope with fresh trace
            trace = QueryTrace(session_id=user_id)
            return {
                "user_id": user_id,
                "experiment_group": "cached",
                "recommendations": cached_result[:limit],
                "trace_id": trace.trace_id
            }

        # Initialize Observability Trace
        trace = QueryTrace(session_id=user_id)
        trace.record_start("recommendation_total")

        # 2. Retrieve user features from Feature Store
        user_features = feature_store.get_user_features(user_id, db)
        interaction_count = user_features.get("interaction_count", 0)

        # 3. Handle Cold Start route
        if interaction_count == 0:
            logger.info("Cold-start path activated for new user.")
            trace.record_start("recommendation_cold_start")
            candidates = cold_start_engine.get_cold_start_recommendations(
                limit=limit,
                region=region,
                age_demographic="child" if is_child_profile else "adult",
                db=db
            )
            trace.record_end("recommendation_cold_start")
            
            # Format outputs with default justifications
            final_recs = []
            for c in candidates:
                final_recs.append({
                    "movie_id": c["movie_id"],
                    "title": c.get("title", f"Movie #{c['movie_id']}"),
                    "final_score": c["score"],
                    "explanation": c["provenance_reason"],
                    "genres": c.get("genres", [])
                })
                
            trace.record_end("recommendation_total")
            await recommendation_cache.cache_recommendations(user_id, final_recs)
            return {
                "user_id": user_id,
                "experiment_group": "cold_start",
                "recommendations": final_recs,
                "trace_id": trace.trace_id
            }

        # 4. Resolve Experiment allocations
        exp_alloc = experimentation_engine.assign_experiment_group(user_id)
        exp_group = exp_alloc["group"]
        exp_weights = exp_alloc["weights"]

        # Override multi_stage_scorer weights for A/B group config dynamically
        custom_scorer = multi_stage_scorer
        if exp_weights:
            from app.recommendation.scorer import MultiStageScorer
            custom_scorer = MultiStageScorer(**exp_weights)

        # 5. Load plugins and execute candidate generation towers concurrently
        plugins = plugin_registry.list_plugins()
        tasks = [plugin.generate_candidates(user_id, limit * 2, db, trace) for plugin in plugins]
        
        plugin_results = await asyncio.gather(*tasks)

        # Merge, de-duplicate, and take highest base score per candidate
        merged_candidates: Dict[int, Dict[str, Any]] = {}
        for result in plugin_results:
            for cand in result:
                m_id = cand["movie_id"]
                if m_id not in merged_candidates or cand["score"] > merged_candidates[m_id]["score"]:
                    merged_candidates[m_id] = cand

        candidates_list = list(merged_candidates.values())
        if not candidates_list:
            logger.info("No candidates generated by plugins. Falling back to cold-start trending list.")
            trace.record_start("recommendation_fallback")
            candidates_list = cold_start_engine.get_cold_start_recommendations(
                limit=limit, region=region, age_demographic="child" if is_child_profile else "adult", db=db
            )
            trace.record_end("recommendation_fallback")

        # 6. Execute multi-objective scoring
        scored_candidates = custom_scorer.score_candidates(candidates_list, user_features, db)

        # 7. Apply policy chain constraints
        policy_context = {
            "region": region,
            "subscription_tier": subscription_tier,
            "is_child_profile": is_child_profile
        }
        filtered_candidates = policy_chain.execute(scored_candidates, policy_context)

        # 8. Apply MMR diversification
        diversified_candidates = custom_scorer.diversify_candidates(filtered_candidates, limit=limit)

        # 9. Apply Bubble Breaker Guardrail
        guarded_candidates = recommendation_guardrails.validate_and_adjust(
            final_list=diversified_candidates,
            all_candidates=scored_candidates,
            user_features=user_features
        )

        # 10. Generate natural language explanations
        final_recs = []
        for cand in guarded_candidates:
            explained = recommendation_explainer.generate_explanation(cand, user_features)
            final_recs.append({
                "movie_id": explained["movie_id"],
                "title": explained["title"],
                "final_score": explained["final_score"],
                "explanation": explained["explanation"],
                "genres": cand.get("genres", [])
            })

        trace.record_end("recommendation_total")

        # 11. Write traces to telemetry
        recommendation_telemetry.record_recommendation_trace(user_id, exp_group, trace, final_recs)

        # 12. Save to cache
        await recommendation_cache.cache_recommendations(user_id, final_recs)

        return {
            "user_id": user_id,
            "experiment_group": exp_group,
            "recommendations": final_recs,
            "trace_id": trace.trace_id
        }

    async def record_feedback(
        self,
        user_id: str,
        movie_id: int,
        interaction_type: str,
        rating: Optional[float] = None,
        db: Session = None
    ) -> None:
        await feedback_pipeline.log_interaction(user_id, movie_id, interaction_type, rating, db)

    async def get_user_taste_coordinates(
        self,
        user_id: str,
        db: Session = None
    ) -> Dict[str, Any]:
        return feature_store.get_user_features(user_id, db)

# Export Recommendation SDK client singleton
recommendation_client = RecommendationClient()
