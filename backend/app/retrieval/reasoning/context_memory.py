from typing import Dict, List, Any, Optional, Tuple
from pydantic import BaseModel, Field
import threading
from app.core.logging import get_logger

logger = get_logger("app.retrieval.context_memory")

class ContextMemoryState(BaseModel):
    session_id: str
    last_query: Optional[str] = None
    expanded_queries: List[str] = Field(default_factory=list)
    parsed_intent: Dict[str, Any] = Field(default_factory=dict)
    previous_results: List[int] = Field(default_factory=list)  # tmdb_ids
    selected_strategy: Optional[str] = None
    selected_filters: Dict[str, Any] = Field(default_factory=dict)
    referenced_movies: List[int] = Field(default_factory=list)  # tmdb_ids
    referenced_people: List[str] = Field(default_factory=list)

class ContextMemoryEngine:
    """
    Lightweight context engine to track and resolve conversational search state.
    """
    def __init__(self):
        self._store: Dict[str, ContextMemoryState] = {}
        self._lock = threading.Lock()

    def get_context(self, session_id: str) -> Optional[ContextMemoryState]:
        with self._lock:
            return self._store.get(session_id)

    def save_context(self, session_id: str, state: ContextMemoryState) -> None:
        with self._lock:
            self._store[session_id] = state
            logger.info(f"Saved conversational context for session: {session_id}")

    def clear_context(self, session_id: str) -> None:
        with self._lock:
            if session_id in self._store:
                del self._store[session_id]
                logger.info(f"Cleared conversational context for session: {session_id}")

    def resolve_follow_up(self, query: str, session_id: str) -> Tuple[str, Dict[str, Any]]:
        """
        Detects follow-up queries and merges them with previous state filters/queries.
        Returns: (resolved_query_string, merged_filters)
        """
        context = self.get_context(session_id)
        if not context:
            return query, {}

        normalized = query.lower().strip()
        merged_filters = context.selected_filters.copy()

        # Follow-up: "show similar ones" or "more like this"
        if normalized in ["show similar ones", "more like this", "similar movies", "recommend similar"]:
            if context.previous_results:
                target_id = context.previous_results[0]
                resolved_query = f"movies similar to movie ID {target_id}"
                merged_filters["similar_to"] = target_id
                logger.info(f"Resolved follow-up similar query for target: {target_id}")
                return resolved_query, merged_filters

        # Follow-up: "only nolan movies"
        if normalized == "only nolan movies" or normalized == "only nolan":
            merged_filters["director"] = "Christopher Nolan"
            resolved_query = f"{context.last_query or ''} directed by Christopher Nolan"
            logger.info("Injected director filter 'Christopher Nolan' from follow-up query.")
            return resolved_query, merged_filters

        # Follow-up: "make it darker"
        if normalized == "make it darker" or normalized == "darker":
            merged_filters["mood"] = "dark"
            resolved_query = f"{context.last_query or ''} with dark themes"
            logger.info("Injected mood filter 'dark' from follow-up query.")
            return resolved_query, merged_filters

        # Follow-up: "less emotional"
        if normalized == "less emotional":
            merged_filters["exclude_emotions"] = ["sadness", "grief", "melancholy"]
            resolved_query = context.last_query or query
            logger.info("Injected emotional exclusions from follow-up query.")
            return resolved_query, merged_filters

        # Follow-up: "the first one"
        if normalized in ["the first one", "first movie", "first candidate"]:
            if context.previous_results:
                first_id = context.previous_results[0]
                resolved_query = f"details for movie ID {first_id}"
                merged_filters["movie_id"] = first_id
                logger.info(f"Resolved follow-up details query for: {first_id}")
                return resolved_query, merged_filters

        return query, {}

context_memory_engine = ContextMemoryEngine()
