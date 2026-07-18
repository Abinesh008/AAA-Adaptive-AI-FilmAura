import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.models.movie import UserInteractionHistory
from app.recommendation.profile import profile_learning_engine
from app.recommendation.cache import recommendation_cache
from app.core.logging import get_logger

logger = get_logger("app.recommendation.feedback")

class FeedbackIngestionPipeline:
    """
    Ingests and persists interaction feedback (implicit clicks/skips and explicit ratings),
    updates the taste profile, and invalidates active cache segments.
    """
    async def log_interaction(
        self,
        user_id: str,
        movie_id: int,
        interaction_type: str,  # "click", "skip", "rating", "bookmark"
        rating: Optional[float],
        db: Session
    ) -> None:
        logger.info(f"Logging interaction '{interaction_type}' for user {user_id} on movie {movie_id}")
        
        # 1. Persist to PostgreSQL database
        interaction = UserInteractionHistory(
            user_id=user_id,
            movie_id=movie_id,
            interaction_type=interaction_type,
            rating=rating
        )
        db.add(interaction)
        db.commit()

        # 2. Rebuild user taste profile weights
        profile_learning_engine.rebuild_profile(user_id, db)

        # 3. Evict active recommendation caches
        await recommendation_cache.invalidate_user_cache(user_id)
        logger.info(f"Feedback ingested and cache invalidated successfully for user: {user_id}")

# Export feedback pipeline singleton
feedback_pipeline = FeedbackIngestionPipeline()
