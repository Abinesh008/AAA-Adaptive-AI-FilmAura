import hashlib
from typing import Dict, Any
from app.core.logging import get_logger

logger = get_logger("app.recommendation.experimentation")

class ExperimentationEngine:
    """
    A/B testing and Canary rollout coordinator.
    Deterministically routes users to experiment groups using ID string hashes.
    """
    def __init__(self):
        # Default recommendation scorer weights
        self.default_weights = {
            "w_relevance": 0.5,
            "w_popularity": 0.1,
            "w_freshness": 0.1,
            "w_novelty": 0.1,
            "w_serendipity": 0.2
        }

    def assign_experiment_group(self, user_id: str) -> Dict[str, Any]:
        """
        Hashes user ID to assign stable A/B test groups and associated weights configs.
        """
        if not user_id:
            return {
                "group": "control",
                "weights": self.default_weights
            }

        # Deterministic MD5 hash to float value in [0.0, 1.0] range
        hasher = hashlib.md5(user_id.encode("utf-8"))
        hash_hex = hasher.hexdigest()
        hash_val = int(hash_hex[:8], 16) / 0xffffffff

        # 1. Canary rollout bucket (10% of users)
        if hash_val < 0.1:
            group = "canary_variant"
            weights = {
                "w_relevance": 0.3,
                "w_popularity": 0.3,
                "w_freshness": 0.2,
                "w_novelty": 0.1,
                "w_serendipity": 0.1
            }
        # 2. Variant B bucket (30% of users)
        elif hash_val < 0.4:
            group = "variant_b_serendipity"
            weights = {
                "w_relevance": 0.3,
                "w_popularity": 0.1,
                "w_freshness": 0.1,
                "w_novelty": 0.1,
                "w_serendipity": 0.4  # Focus heavily on surprise matches
            }
        # 3. Control bucket (60% of users)
        else:
            group = "control"
            weights = self.default_weights

        logger.info(f"User {user_id} assigned to group '{group}' with hash value {hash_val:.3f}")
        return {
            "group": group,
            "hash_value": hash_val,
            "weights": weights
        }

# Export experimentation engine singleton
experimentation_engine = ExperimentationEngine()
