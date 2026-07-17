from typing import Dict, Any
from app.agent.memory import conversation_memory
from app.retrieval.session_store import session_store
from app.core.logging import get_logger

logger = get_logger("app.agent.diagnostics")

class AgentDiagnostics:
    """
    Diagnostics collector tracking active agent threads, conversational telemetry, and session stats.
    """
    def get_agent_stats(self) -> Dict[str, Any]:
        # Count total session logs we hold
        history_map = conversation_memory._history
        total_sessions = len(history_map)
        
        # Collect active taste profiles
        taste_profiles = {
            s_id: conversation_memory.get_user_profile(s_id)
            for s_id in history_map.keys()
        }
        
        # Calculate active timelines from session traces
        recent_sessions = session_store.get_recent_sessions(limit=10)
        agent_latencies = []
        for s in recent_sessions:
            if "agent_total" in s.latencies:
                agent_latencies.append(s.latencies["agent_total"])
                
        avg_latency = round(sum(agent_latencies) / len(agent_latencies), 2) if agent_latencies else 0.0
        
        return {
            "total_conversational_sessions": total_sessions,
            "average_agent_latency_ms": avg_latency,
            "active_taste_profiles": taste_profiles,
            "recent_traces": [s.trace_id for s in recent_sessions]
        }

# Export diagnostics singleton instance
agent_diagnostics = AgentDiagnostics()
