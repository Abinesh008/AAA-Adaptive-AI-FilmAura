from typing import Optional, Dict, Any
from app.retrieval.orchestrator import orchestrator
from app.retrieval.contract import FinalResponse
from app.retrieval.session_store import session_store
from app.retrieval.explanation import explanation_engine

class RetrievalClient:
    """
    Singular, stable public SDK entry contract for all AAA-Adaptive-AI-FilmAura retrieval requests.
    """
    async def search(
        self,
        query: str,
        session_id: Optional[str] = None,
        profile: str = "balanced",
        experiment_id: Optional[str] = None
    ) -> FinalResponse:
        return await orchestrator.execute_query(
            query=query,
            session_id=session_id,
            profile=profile,
            experiment_id=experiment_id
        )

    async def recommend(
        self,
        query: str,
        session_id: Optional[str] = None,
        profile: str = "balanced"
    ) -> FinalResponse:
        """
        Specialized recommendation profile query routing.
        """
        return await orchestrator.execute_query(
            query=query,
            session_id=session_id,
            profile=profile
        )

    async def identify(
        self,
        query: str,
        session_id: Optional[str] = None,
        profile: str = "balanced"
    ) -> FinalResponse:
        """
        Specialized movie identification profile query routing.
        """
        return await orchestrator.execute_query(
            query=query,
            session_id=session_id,
            profile=profile
        )

    def explain(self, trace_id: str) -> Dict[str, Any]:
        """
        Returns structured explainability tree details for a recorded query trace.
        """
        trace = session_store.get_session(trace_id)
        if not trace:
            return {
                "error": f"Retrieval trace session '{trace_id}' not found.",
                "human_explanation": "",
                "explanation_tree": {}
            }
            
        # Reconstruct explanations using stored session candidates
        # We can extract candidate movies from logs or explain details
        # To make it simple, we can return the cached explanation or rebuild it
        return {
            "trace_id": trace_id,
            "databases_used": trace.selected_databases,
            "timeline": trace.latencies,
            "confidence_breakdown": trace.confidence_breakdown
        }

# Singular public client instance
retrieval_client = RetrievalClient()
