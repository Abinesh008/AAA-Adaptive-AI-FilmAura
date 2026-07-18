from typing import List, Dict, Any
from app.retrieval.query_trace import QueryTrace
from app.retrieval.session_store import session_store
from app.core.logging import get_logger

logger = get_logger("app.recommendation.telemetry")

class RecommendationTelemetry:
    """
    Observability logger tracking latency and score breakdowns per recommendation request.
    """
    def record_recommendation_trace(
        self,
        user_id: str,
        group: str,
        trace: QueryTrace,
        final_list: List[Dict[str, Any]]
    ) -> None:
        # Latency breakdown calculation
        timeline = trace.timeline
        total_time = timeline.get("recommendation_total_end", 0.0) - timeline.get("recommendation_total_start", 0.0)
        
        # Candidate score statistics
        avg_score = 0.0
        if final_list:
            avg_score = sum(c.get("final_score", 0.0) for c in final_list) / len(final_list)

        logger.info(
            f"[RECOMMENDATION TELEMETRY] User: {user_id} | Group: {group} | "
            f"Trace ID: {trace.trace_id} | Total latency: {total_time * 1000.0:.2f}ms | "
            f"Returned count: {len(final_list)} | Average score: {avg_score:.3f}"
        )
        
        # Save trace to session store
        trace.planner_decisions["experiment_group"] = group
        trace.planner_decisions["recommendation_count"] = len(final_list)
        session_store.save_session(trace)

# Export telemetry singleton
recommendation_telemetry = RecommendationTelemetry()
