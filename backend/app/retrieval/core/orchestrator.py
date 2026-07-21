import time
import asyncio
from enum import Enum
from typing import Dict, Any, List, Optional
from app.core.logging import get_logger
from app.retrieval.query.query_trace import QueryTrace
from app.retrieval.contracts.contract import (
    QueryIntent, ExecutionPlan, RetrievalResult, CandidateMovie,
    ReasoningContext, FinalResponse
)
from app.retrieval.core.guardrails import guardrail_engine
from app.retrieval.reasoning.context_memory import context_memory_engine, ContextMemoryState
from app.retrieval.query.query_normalize import query_normalizer
from app.retrieval.query.query_expansion import query_expansion_engine
from app.retrieval.core.planner import planner
from app.retrieval.core.supervisor import supervisor
from app.retrieval.ranking.calibration import score_calibrator
from app.retrieval.ranking.fusion import hybrid_coordinator
from app.retrieval.ranking.diversity import diversity_engine
from app.retrieval.ranking.reranker import reranker
from app.retrieval.reasoning.context_builder import context_builder
from app.retrieval.reasoning.reasoning import reasoning_engine
from app.retrieval.ranking.confidence import confidence_engine
from app.retrieval.ranking.quality import quality_scorer
from app.retrieval.reasoning.explanation import explanation_engine
from app.retrieval.cache.retrieval_cache import retrieval_cache
from app.retrieval.cache.session_store import session_store
from app.retrieval.analytics.analytics import retrieval_analytics
from app.retrieval.hooks.event_bus import event_bus
from app.retrieval.hooks.hooks import hooks
from app.retrieval.analytics.versioning import get_version_manifest, get_configuration_hash
from app.retrieval.core.features import features
from app.core.config import settings

logger = get_logger("app.retrieval.orchestrator")

class LifecycleState(Enum):
    INITIALIZED = "initialized"
    READY = "ready"
    PROCESSING = "processing"
    PARTIAL_SUCCESS = "partial_success"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class RetrievalOrchestrator:
    """
    Central state-machine coordinating query trace execution from normalizations to final reasoning.
    """
    async def execute_query(
        self,
        query: str,
        session_id: Optional[str] = None,
        profile: str = "balanced",
        experiment_id: Optional[str] = None
    ) -> FinalResponse:
        trace = QueryTrace(session_id=session_id, active_profile=profile)
        trace.configuration_hash = get_configuration_hash()
        
        # Enforce initial versions metadata
        manifest = get_version_manifest()
        trace.plugin_versions = {
            "retrieval": manifest["retrieval_version"],
            "planner": manifest["planner_version"],
            "fusion": manifest["fusion_version"],
            "reranker": manifest["ranking_version"],
            "reasoning": manifest["reasoning_version"]
        }
        
        state = LifecycleState.INITIALIZED
        trace.record_start("total")
        await event_bus.publish("queryreceived", {"trace_id": trace.trace_id, "query": query})
        
        try:
            # Step 1: Check Cache (answer key prefix)
            query_hash = retrieval_cache.get_hash(query, salt=f"{profile}:{experiment_id}")
            cached_res = await retrieval_cache.get_cached_item("answer", query_hash)
            if cached_res:
                trace.cache_status = "hit"
                trace.record_end("total")
                retrieval_analytics.record_query(trace)
                await event_bus.publish("retrievalcompleted", {"trace_id": trace.trace_id, "status": "cache_hit"})
                return FinalResponse(**cached_res)

            # Step 2: Guardrails & Security checks
            await hooks.trigger("before_guardrails", query, trace)
            is_safe, guard_err = guardrail_engine.validate_query(query, trace)
            if not is_safe:
                raise ValueError(f"Guardrail rejection: {guard_err}")
                
            # Step 3: Resolve follow-up query context
            resolved_query, filters = context_memory_engine.resolve_follow_up(query, session_id or "")
            
            # Step 4: Normalization
            await hooks.trigger("before_normalization", resolved_query, trace)
            normalized = query_normalizer.normalize(resolved_query)
            trace.record_end("query_normalize")
            await event_bus.publish("querynormalized", {"trace_id": trace.trace_id, "normalized": normalized})
            
            # Step 5: Expansion & Rewriting
            expanded_queries = query_expansion_engine.expand_query(normalized)
            trace.expanded_queries = expanded_queries
            await event_bus.publish("queryexpanded", {"trace_id": trace.trace_id, "expanded": expanded_queries})
            
            # Step 6: Intent parsing
            # Simple heuristic intent routing
            primary_intent = "recommend"
            if any(k in normalized for k in ["who directed", "actor", "director", "starring", "cast"]):
                primary_intent = "qa"
            elif any(k in normalized for k in ["similar to", "like"]):
                primary_intent = "recommend"
            elif any(k in normalized for k in ["what is the movie about", "which film", "find movie"]):
                primary_intent = "identify"
                
            intent = QueryIntent(
                query=query,
                normalized_query=normalized,
                primary_intent=primary_intent,
                filters=filters
            )
            trace.planner_decisions["intent"] = intent.dict()
            state = LifecycleState.READY
            
            # Step 7: Planning
            await hooks.trigger("before_planning", intent, trace)
            plan = planner.plan(intent, profile)
            trace.planner_decisions["plan"] = plan.dict()
            await event_bus.publish("plancreated", {"trace_id": trace.trace_id, "strategy": plan.strategy})
            
            # Step 8: Supervisor-led execution
            state = LifecycleState.PROCESSING
            await event_bus.publish("databaseexecutionstarted", {"trace_id": trace.trace_id})
            raw_results = await supervisor.execute_plan(plan, trace)
            
            # Check degraded errors
            is_partial = any("failed" in db or "timeout" in db for db in trace.selected_databases)
            if is_partial:
                state = LifecycleState.PARTIAL_SUCCESS
                
            # Step 9: Calibration
            calibrated_results = score_calibrator.calibrate_scores(raw_results)
            
            # Step 10: Pluggable Fusion
            await hooks.trigger("before_fusion", calibrated_results, trace)
            fusion_result = hybrid_coordinator.fuse_results(calibrated_results, strategy="rrf")
            await event_bus.publish("fusioncompleted", {"trace_id": trace.trace_id})
            
            # Step 11: Diversity balancing
            diversified = diversity_engine.diversify(fusion_result.candidates, max_results=10)
            
            # Step 12: Reranking
            await hooks.trigger("before_reranking", diversified, trace)
            ranked_result = reranker.rerank(diversified, query, experiment_id)
            await event_bus.publish("rankingcompleted", {"trace_id": trace.trace_id})
            
            # Step 13: Context Optimization
            context = context_builder.build_context(ranked_result, settings.TOKEN_BUDGET)
            
            # Step 14: Reasoning
            await hooks.trigger("before_reasoning", context, trace)
            answer = await reasoning_engine.generate_answer(context, trace)
            await event_bus.publish("reasoningcompleted", {"trace_id": trace.trace_id})
            
            # Step 15: Confidence calculations
            conf_breakdown = confidence_engine.calculate_confidence(ranked_result, trace.selected_databases)
            trace.confidence_breakdown = conf_breakdown
            
            # Step 16: Quality grades checks
            quality_details = quality_scorer.score_quality(ranked_result, trace.selected_databases, conf_breakdown)
            
            # Step 17: Structured Explanation trees
            explanation_data = explanation_engine.generate_explanation(ranked_result)
            explanation_data["quality_details"] = quality_details
            
            trace.record_end("total")
            state = LifecycleState.COMPLETED
            
            # Save follow-up context memory state
            mem_state = ContextMemoryState(
                session_id=session_id or trace.trace_id,
                last_query=query,
                expanded_queries=expanded_queries,
                parsed_intent=intent.dict(),
                previous_results=[c.tmdb_id for c in ranked_result],
                selected_strategy=plan.strategy,
                selected_filters=filters
            )
            context_memory_engine.save_context(session_id or trace.trace_id, mem_state)
            
            # Format Response
            response = FinalResponse(
                answer=answer,
                movies=ranked_result,
                trace_id=trace.trace_id,
                api_version="1.0.0",
                retrieval_version=manifest["retrieval_version"],
                confidence_score=conf_breakdown.get("final_confidence", 1.0),
                confidence_breakdown=conf_breakdown,
                explanation=explanation_data
            )
            
            # Update cache & session records
            linked_ids = [c.tmdb_id for c in ranked_result]
            await retrieval_cache.set_cached_item("answer", query_hash, response.dict(), settings.RETRIEVAL_CACHE_TTL, linked_ids)
            session_store.save_session(trace)
            retrieval_analytics.record_query(trace)
            
            await event_bus.publish("responsegenerated", {"trace_id": trace.trace_id})
            return response
            
        except Exception as e:
            logger.error(f"Retrieval Orchestrator failed to execute: {str(e)}")
            state = LifecycleState.FAILED
            trace.record_end("total")
            session_store.save_session(trace)
            await event_bus.publish("retrievalfailed", {"trace_id": trace.trace_id, "error": str(e)})
            raise e

# Export singleton orchestrator instance
orchestrator = RetrievalOrchestrator()
