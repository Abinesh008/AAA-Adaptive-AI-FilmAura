from abc import ABC, abstractmethod
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.retrieval.query_trace import QueryTrace

class BaseRecommendationPlugin(ABC):
    """
    Interface contract defining capabilities of recommendation candidate generation plugins.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique identifier of the recommendation plugin.
        """
        pass

    @abstractmethod
    async def generate_candidates(
        self, 
        user_id: str, 
        limit: int, 
        db: Session, 
        trace: QueryTrace
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations matching the plugin's logic.
        
        Returns:
            List[Dict[str, Any]]: List of dictionary structures representing candidate recommendations:
                {
                    "movie_id": int,
                    "score": float,  # calibrated score scale [0.0, 1.0]
                    "provenance_reason": str
                }
        """
        pass
