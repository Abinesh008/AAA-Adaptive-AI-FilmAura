from typing import Dict, Any, Optional
from app.retrieval.cache.session_store import session_store
from app.retrieval.contracts.contract import FinalResponse, CandidateMovie, ProvenanceChain
from app.core.logging import get_logger

logger = get_logger("app.retrieval.replay")

class ReplayEngine:
    """
    Replay engine executing dry-runs using stored session traces without live db queries.
    """
    def replay_session(self, trace_id: str) -> Optional[FinalResponse]:
        trace = session_store.get_session(trace_id)
        if not trace:
            logger.warning(f"Failed to replay session: trace ID '{trace_id}' not found.")
            return None
            
        logger.info(f"Replaying search trace: {trace_id}")
        
        # Build mock Candidates from trace logs to emulate candidates list
        candidates = []
        for tmdb_id, score_dict in trace.fusion_scores.items():
            candidates.append(CandidateMovie(
                tmdb_id=int(tmdb_id),
                title=f"Replayed Movie {tmdb_id}",
                score=score_dict.get("rrf_score", 1.0),
                confidence=trace.confidence_breakdown.get("final_confidence", 0.9),
                matched_by_sources=trace.selected_databases,
                provenance_details=[
                    ProvenanceChain(database=db, table_or_label="Movie", node_id_or_vector_id=str(tmdb_id))
                    for db in trace.selected_databases if "failed" not in db
                ]
            ))
            
        return FinalResponse(
            answer=trace.reasoning_metadata.get("answer_summary", "Replayed mock response."),
            movies=candidates,
            trace_id=trace.trace_id,
            api_version="1.0.0",
            retrieval_version=trace.plugin_versions.get("retrieval", "1.0.0"),
            confidence_score=trace.confidence_breakdown.get("final_confidence", 1.0),
            confidence_breakdown=trace.confidence_breakdown,
            explanation={"replayed": True, "trace_id": trace_id}
        )

# Export singleton replay instance
replay_engine = ReplayEngine()
