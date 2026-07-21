from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Optional, Dict, Any
from pydantic import BaseModel
from app.api import deps
from app.services.agent import AgentService

router = APIRouter()

class AgentChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

@router.post("/chat", response_model=Dict[str, Any])
async def chat_message(
    request: AgentChatRequest = Body(...),
    service: AgentService = Depends(deps.get_agent_service)
):
    try:
        response = await service.chat(
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
def get_session_history(
    session_id: str,
    service: AgentService = Depends(deps.get_agent_service)
):
    history = service.get_history(session_id)
    return {
        "status": "success",
        "session_id": session_id,
        "history": [{"role": m.role, "content": m.content} for m in history]
    }

@router.delete("/history/{session_id}", response_model=Dict[str, Any])
def clear_session_history(
    session_id: str,
    service: AgentService = Depends(deps.get_agent_service)
):
    service.clear_history(session_id)
    return {
        "status": "success",
        "message": f"Cleared history for session ID: {session_id}"
    }

@router.get("/diagnostics/stats", response_model=Dict[str, Any])
def get_agent_diagnostics_stats(
    service: AgentService = Depends(deps.get_agent_service)
):
    return {
        "status": "success",
        "data": service.get_agent_stats()
    }
