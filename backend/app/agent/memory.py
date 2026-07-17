import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.api.deps import get_llm_provider
from app.agent.prompts import TASTE_EXTRACTOR_SYSTEM_PROMPT
from app.core.logging import get_logger

logger = get_logger("app.agent.memory")

class Message(BaseModel):
    role: str # user, assistant, system
    content: str
    timestamp: float = Field(default_factory=lambda: 0.0) # timestamp tracker

class ConversationMemory:
    """
    In-memory session history database with taste extraction capabilities.
    """
    def __init__(self):
        # session_id -> message lists
        self._history: Dict[str, List[Message]] = {}
        # session_id -> running user profiles
        self._profiles: Dict[str, Dict[str, Any]] = {}

    def add_message(self, session_id: str, role: str, content: str):
        if session_id not in self._history:
            self._history[session_id] = []
        
        self._history[session_id].append(Message(role=role, content=content))
        # Keep a rolling budget of maximum 20 messages to conserve LLM tokens
        if len(self._history[session_id]) > 20:
            self._history[session_id] = self._history[session_id][-20:]

    def get_history(self, session_id: str) -> List[Message]:
        return self._history.get(session_id, [])

    def get_history_as_string(self, session_id: str) -> str:
        messages = self.get_history(session_id)
        return "\n".join([f"{msg.role.upper()}: {msg.content}" for msg in messages])

    def clear(self, session_id: str):
        self._history[session_id] = []
        self._profiles[session_id] = {
            "favorite_directors": [],
            "favorite_genres": [],
            "favorite_actors": [],
            "disliked_genres": [],
            "preferred_keywords": [],
            "preferred_eras": []
        }
        logger.info(f"Cleared conversation history for session: {session_id}")

    def get_user_profile(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self._profiles:
            self._profiles[session_id] = {
                "favorite_directors": [],
                "favorite_genres": [],
                "favorite_actors": [],
                "disliked_genres": [],
                "preferred_keywords": [],
                "preferred_eras": []
            }
        return self._profiles[session_id]

    async def update_taste_profile(self, session_id: str, user_message: str):
        profile = self.get_user_profile(session_id)
        
        try:
            llm = get_llm_provider()
            prompt = TASTE_EXTRACTOR_SYSTEM_PROMPT.format(user_message=user_message)
            raw_response = await llm.generate_async(prompt)
            
            # Simple clean response parsing (look for JSON boundaries)
            import re
            json_match = re.search(r"(\{.*?\})", raw_response, re.DOTALL)
            if json_match:
                extracted = json.loads(json_match.group(1))
                
                # Merge extracted values into profile list fields
                for key in ["favorite_directors", "favorite_genres", "favorite_actors", "disliked_genres", "preferred_keywords", "preferred_eras"]:
                    if key in extracted and isinstance(extracted[key], list):
                        for val in extracted[key]:
                            if val not in profile[key]:
                                profile[key].append(val)
                                
                logger.info(f"Updated taste profile for session {session_id}: {profile}")
        except Exception as e:
            logger.error(f"Failed to extract tastes from message: {str(e)}")

# Export memory singleton instance
conversation_memory = ConversationMemory()
