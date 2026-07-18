from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.retrieval.query_trace import QueryTrace

class BaseRecommendationClient(ABC):
    """
    Interface contract for the Recommendation SDK client.
    Ensures zero coupling from other sub-modules directly to recommendation algorithms.
    """
    @abstractmethod
    async def get_recommendations(
        self,
        user_id: str,
        limit: int,
        region: Optional[str],
        subscription_tier: Optional[str],
        is_child_profile: bool,
        db: Session
    ) -> Dict[str, Any]:
        """
        Retrieves personalized recommendation candidates for a user, processed through A/B experiment
        allocations, multi-objective ranking, policy chains, bubble breakers, and explainers.
        """
        pass

    @abstractmethod
    async def record_feedback(
        self,
        user_id: str,
        movie_id: int,
        interaction_type: str,
        rating: Optional[float],
        db: Session
    ) -> None:
        """
        Logs explicit/implicit user interactions, invalidates recommendation caches, and rebuilds profiles.
        """
        pass

    @abstractmethod
    async def get_user_taste_coordinates(
        self,
        user_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Retrieves computed preference vectors and favorite entities.
        """
        pass
