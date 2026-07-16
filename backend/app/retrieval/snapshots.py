from typing import Dict, Any
from app.core.config import settings
from app.retrieval.features import features
from app.retrieval.versioning import get_version_manifest
from app.core.logging import get_logger

logger = get_logger("app.retrieval.snapshots")

class SnapshotManager:
    """
    Snapshot manager saving and restoring active retrieval profile parameters.
    """
    def take_snapshot(self) -> Dict[str, Any]:
        manifest = get_version_manifest()
        snapshot = {
            "version_manifest": manifest,
            "weights": {
                "reranker": settings.RERANKING_WEIGHTS.copy(),
                "planner_cost": settings.PLANNER_COST_WEIGHTS.copy()
            },
            "features": {f: features.get_state(f).value for f in ["query_rewrite", "query_expansion", "graph_search", "vector_search", "sql_search", "reranking", "reasoning", "cache", "diversity", "explainability", "streaming"]}
        }
        logger.info("Created system configuration snapshot.")
        return snapshot

    def restore_snapshot(self, snapshot: Dict[str, Any]) -> None:
        # Restore reranking weights
        weights = snapshot.get("weights", {})
        if "reranker" in weights:
            settings.RERANKING_WEIGHTS = weights["reranker"]
        if "planner_cost" in weights:
            settings.PLANNER_COST_WEIGHTS = weights["planner_cost"]
            
        # Restore feature flags
        feat_states = snapshot.get("features", {})
        for f, val in feat_states.items():
            try:
                from app.retrieval.features import FeatureState
                features.set_state(f, FeatureState(val))
            except Exception as e:
                logger.error(f"Failed to restore feature state for {f}: {e}")
                
        logger.info("Restored system configuration from snapshot.")

# Export singleton snapshot manager instance
snapshot_manager = SnapshotManager()
