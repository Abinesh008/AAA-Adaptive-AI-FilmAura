from app.services.base import BaseService
from app.agent.core import agent_coordinator
from app.agent.memory import conversation_memory
from app.agent.diagnostics import agent_diagnostics

class AgentService(BaseService):
    """
    Orchestrates logic for AI Chat interactions, memory management, and diagnostics stats.
    """
    async def chat(self, query: str, session_id: str | None):
        with self.time_block("agent_chat"):
            return await agent_coordinator.chat(query=query, session_id=session_id)

    def get_history(self, session_id: str):
        return conversation_memory.get_history(session_id)

    def clear_history(self, session_id: str):
        conversation_memory.clear(session_id)

    def get_agent_stats(self):
        return agent_diagnostics.get_agent_stats()
