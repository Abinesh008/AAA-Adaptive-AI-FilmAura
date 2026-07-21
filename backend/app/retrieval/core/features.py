from enum import Enum
from typing import Dict, Any
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("app.retrieval.features")

class FeatureState(Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    EXPERIMENTAL = "experimental"
    DEPRECATED = "deprecated"

class FeatureRegistry:
    """
    Centralized registry of pipeline feature states, supporting dynamic overrides.
    """
    def __init__(self):
        # Default flags loaded from env/config settings
        self._states: Dict[str, FeatureState] = {
            "query_rewrite": FeatureState.ENABLED,
            "query_expansion": FeatureState.ENABLED,
            "graph_search": FeatureState.ENABLED,
            "vector_search": FeatureState.ENABLED,
            "sql_search": FeatureState.ENABLED,
            "reranking": FeatureState.ENABLED,
            "reasoning": FeatureState.ENABLED,
            "cache": FeatureState.ENABLED,
            "diversity": FeatureState.ENABLED,
            "explainability": FeatureState.ENABLED,
            "streaming": FeatureState.ENABLED
        }

    def is_enabled(self, feature_name: str) -> bool:
        """
        Check if a feature is active (either ENABLED or EXPERIMENTAL).
        """
        state = self._states.get(feature_name.lower())
        if not state:
            return False
        return state in (FeatureState.ENABLED, FeatureState.EXPERIMENTAL)

    def get_state(self, feature_name: str) -> FeatureState:
        return self._states.get(feature_name.lower(), FeatureState.DISABLED)

    def set_state(self, feature_name: str, state: FeatureState) -> None:
        logger.info(f"Setting feature state: {feature_name} -> {state.value}")
        self._states[feature_name.lower()] = state

# Singleton registry instance
features = FeatureRegistry()
