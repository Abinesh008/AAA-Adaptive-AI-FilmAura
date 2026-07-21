from sqlalchemy.orm import Session
from app.services.base import BaseService
from app.recommendation.sdk import recommendation_client
from app.recommendation.model_registry import model_registry

class RecommendationService(BaseService):
    """
    Orchestrates user recommendation feeds, feedback records, profile weights, and model promotions.
    """
    async def get_recommendations(
        self, user_id: str, limit: int, region: str | None, subscription_tier: str, is_child_profile: bool, db: Session
    ):
        with self.time_block("recommendation_retrieve"):
            return await recommendation_client.get_recommendations(
                user_id=user_id,
                limit=limit,
                region=region,
                subscription_tier=subscription_tier,
                is_child_profile=is_child_profile,
                db=db
            )

    async def record_feedback(self, user_id: str, movie_id: int, interaction_type: str, rating: float | None, db: Session):
        with self.time_block("recommendation_feedback"):
            await recommendation_client.record_feedback(
                user_id=user_id,
                movie_id=movie_id,
                interaction_type=interaction_type,
                rating=rating,
                db=db
            )

    async def get_user_taste_profile(self, user_id: str, db: Session):
        with self.time_block("recommendation_user_profile"):
            profile = await recommendation_client.get_user_taste_coordinates(user_id, db)
            return {
                "user_id": user_id,
                "genre_weights": profile.get("genre_weights", {}),
                "favorite_directors": profile.get("favorite_directors", []),
                "favorite_actors": profile.get("favorite_actors", []),
                "interaction_count": profile.get("interaction_count", 0)
            }

    def promote_model(self, model_version: str, stage: str):
        model_registry.promote_model(model_version, stage)

    def rollback_model(self, fallback_version: str):
        model_registry.rollback_production(fallback_version)
