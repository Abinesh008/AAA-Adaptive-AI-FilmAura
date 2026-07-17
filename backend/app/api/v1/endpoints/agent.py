from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from app.agent.core import agent_coordinator
from app.agent.memory import conversation_memory
from app.agent.diagnostics import agent_diagnostics

router = APIRouter()

class AgentChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class MessageResponse(BaseModel):
    role: str
    content: str

@router.post("/chat", response_model=Dict[str, Any])
async def chat_message(request: AgentChatRequest = Body(...)):
    try:
        response = await agent_coordinator.chat(
            query=request.query,
            session_id=request.session_id
        )
        return {
            "status": "success",
            "data": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent loop error: {str(e)}")

@router.get("/history/{session_id}", response_model=Dict[str, Any])
def get_session_history(session_id: str):
    history = conversation_memory.get_history(session_id)
    return {
        "status": "success",
        "session_id": session_id,
        "history": [{"role": m.role, "content": m.content} for m in history]
    }

@router.delete("/history/{session_id}", response_model=Dict[str, Any])
def clear_session_history(session_id: str):
    conversation_memory.clear(session_id)
    return {
        "status": "success",
        "message": f"Cleared history for session ID: {session_id}"
    }

@router.get("/diagnostics/stats", response_model=Dict[str, Any])
def get_agent_diagnostics_stats():
    return {
        "status": "success",
        "data": agent_diagnostics.get_agent_stats()
    }
