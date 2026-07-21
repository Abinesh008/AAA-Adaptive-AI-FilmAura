from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, Dict, Any
from app.api import deps
from app.services.retrieval import RetrievalService

router = APIRouter()

@router.post("/search", response_model=Dict[str, Any])
async def search_query(
    query: str = Query(..., description="The user query string"),
    session_id: Optional[str] = Query(None, description="Optional conversation session ID"),
    profile: str = Query("balanced", description="Fast, Balanced, Quality execution profiles"),
    experiment_id: Optional[str] = Query(None, description="Optional A/B testing experiment ID"),
    service: RetrievalService = Depends(deps.get_retrieval_service)
):
    try:
        response = await service.search_query(
            query=query,
            session_id=session_id,
            profile=profile,
            experiment_id=experiment_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval execution failed: {str(e)}")

@router.post("/recommend", response_model=Dict[str, Any])
async def recommend_query(
    query: str = Query(...),
    session_id: Optional[str] = Query(None),
    profile: str = Query("balanced"),
    service: RetrievalService = Depends(deps.get_retrieval_service)
):
    try:
        response = await service.recommend_query(query, session_id, profile)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/identify", response_model=Dict[str, Any])
async def identify_query(
    query: str = Query(...),
    session_id: Optional[str] = Query(None),
    profile: str = Query("balanced"),
    service: RetrievalService = Depends(deps.get_retrieval_service)
):
    try:
        response = await service.identify_query(query, session_id, profile)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/explain/{trace_id}", response_model=Dict[str, Any])
def explain_query(
    trace_id: str,
    service: RetrievalService = Depends(deps.get_retrieval_service)
):
    explanation = service.explain_query(trace_id)
    if "error" in explanation:
        raise HTTPException(status_code=404, detail=explanation["error"])
    return {"status": "success", "data": explanation}
