from typing import Dict, Any, Optional
from app.core.logging import get_logger

logger = get_logger("app.recommendation.model_registry")

class ModelRegistry:
    """
    Registry mapping recommendation model versions and weights.
    Supports atomic stage promotions and rollbacks.
    """
    def __init__(self):
        # Default in-memory model versions mappings
        self._registry: Dict[str, Dict[str, Any]] = {
            "v1.0.0": {
                "weights": {
                    "w_relevance": 0.5,
                    "w_popularity": 0.1,
                    "w_freshness": 0.1,
                    "w_novelty": 0.1,
                    "w_serendipity": 0.2
                },
                "stage": "production",
                "description": "Baseline recommendation weights"
            },
            "v1.1.0-beta": {
                "weights": {
                    "w_relevance": 0.3,
                    "w_popularity": 0.1,
                    "w_freshness": 0.1,
                    "w_novelty": 0.1,
                    "w_serendipity": 0.4
                },
                "stage": "staging",
                "description": "High serendipity exploration beta model"
            }
        }
        self.active_production_version = "v1.0.0"

    def get_active_weights(self) -> Dict[str, float]:
        """
        Returns model weights associated with the active production model version.
        """
        model_data = self._registry.get(self.active_production_version)
        if not model_data:
            raise RuntimeError(f"Active production model version {self.active_production_version} not found in registry.")
        return model_data["weights"]

    def promote_model(self, version: str, stage: str) -> None:
        """
        Promotes a model version to production, staging, or shadow-mode.
        """
        if version not in self._registry:
            # Register version with default weights if new
            logger.info(f"Registering new model version: {version}")
            self._registry[version] = {
                "weights": self._registry["v1.0.0"]["weights"].copy(),
                "stage": "draft",
                "description": "Auto-registered model slot"
            }

        self._registry[version]["stage"] = stage
        if stage == "production":
            self.active_production_version = version
            logger.info(f"Atomic production switch executed. Active model version is now: {version}")
        else:
            logger.info(f"Model version {version} promoted to stage: {stage}")

    def rollback_production(self, fallback_version: str = "v1.0.0") -> None:
        """
        Roll back active production version immediately to a fallback version.
        """
        if fallback_version not in self._registry:
            raise ValueError(f"Rollback target version {fallback_version} is not registered.")
        
        self.active_production_version = fallback_version
        self._registry[fallback_version]["stage"] = "production"
        logger.info(f"Rollback successfully executed. Active production version reset to: {fallback_version}")

    def list_models(self) -> Dict[str, Dict[str, Any]]:
        return self._registry

# Export model registry singleton
model_registry = ModelRegistry()
