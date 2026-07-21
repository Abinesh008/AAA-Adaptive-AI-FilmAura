from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.retrieval.contracts.contract import RetrievalResult, QueryIntent

class BaseMemoryProvider(ABC):
    """
    Placeholder contract interface for future User Memory and conversational memory systems.
    """
    @abstractmethod
    async def get_user_context(self, user_id: str) -> Dict[str, Any]:
        pass

class BasePreferenceProvider(ABC):
    """
    Placeholder contract interface for future User Preferences profile models.
    """
    @abstractmethod
    async def get_preferences(self, user_id: str) -> Dict[str, Any]:
        pass

class BaseRecommendationProvider(ABC):
    """
    Placeholder contract interface for recommendation generation.
    """
    @abstractmethod
    async def get_recommendations(self, user_id: str, limit: int = 10) -> List[RetrievalResult]:
        pass

class BaseWatchHistoryProvider(ABC):
    """
    Placeholder contract interface for user watch logs.
    """
    @abstractmethod
    async def get_watch_history(self, user_id: str) -> List[str]:
        pass

class BaseFeedbackProvider(ABC):
    """
    Placeholder contract interface for retrieval analytics and feedback collections.
    """
    @abstractmethod
    async def record_feedback(self, query_id: str, rating: int, comments: Optional[str] = None) -> None:
        pass

class BaseMultimodalProvider(ABC):
    """
    Placeholder contract interface for future voice, trailer video, and subtitle searches.
    """
    @abstractmethod
    async def search_multimodal(self, payload: Any) -> List[RetrievalResult]:
        pass

class BaseAgentProvider(ABC):
    """
    Placeholder contract interface for Multi-Agent planners and reasoning agents.
    """
    @abstractmethod
    async def run_agent_loop(self, intent: QueryIntent) -> Dict[str, Any]:
        pass

class BaseConversationProvider(ABC):
    """
    Placeholder contract interface for Chat conversation trackers.
    """
    @abstractmethod
    async def get_chat_history(self, session_id: str) -> List[Dict[str, str]]:
        pass
