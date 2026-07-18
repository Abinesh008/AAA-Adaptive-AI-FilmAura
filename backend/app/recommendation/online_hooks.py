from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.recommendation.feedback import feedback_pipeline
from app.core.logging import get_logger

logger = get_logger("app.recommendation.online_hooks")

class BaseOnlineLearningHook(ABC):
    """
    Interface defining stream event consumption capabilities for real-time model updates.
    """
    @abstractmethod
    async def process_stream_event(self, event_data: Dict[str, Any], db: Session) -> None:
        """
        Processes a streaming interaction event and updates models/profiles.
        """
        pass

class StreamingFeedbackHook(BaseOnlineLearningHook):
    """
    Processes incoming message payloads from queue events (e.g. Kafka, RabbitMQ) and triggers feedback logging.
    """
    async def process_stream_event(self, event_data: Dict[str, Any], db: Session) -> None:
        user_id = event_data.get("user_id")
        movie_id = event_data.get("movie_id")
        interaction_type = event_data.get("interaction_type")
        rating = event_data.get("rating")

        if not user_id or not movie_id or not interaction_type:
            logger.warn("Skipping malformed streaming learning event payload.")
            return

        logger.info(f"Processing streaming learning hook event for user: {user_id}")
        
        # Ingest feedback via coordinator pipeline
        await feedback_pipeline.log_interaction(
            user_id=user_id,
            movie_id=int(movie_id),
            interaction_type=interaction_type,
            rating=float(rating) if rating is not None else None,
            db=db
        )

# Export streaming hook singleton
streaming_feedback_hook = StreamingFeedbackHook()
