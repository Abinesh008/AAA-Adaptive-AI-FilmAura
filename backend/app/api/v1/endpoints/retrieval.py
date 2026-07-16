from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, Dict, Any
from app.retrieval.sdk import retrieval_client
from app.retrieval.contract import FinalResponse
from app.retrieval.disambiguation import ambiguity_resolver

router = APIRouter()

@router.post("/search", response_model=Dict[str, Any])
async def search_query(
    query: str = Query(..., description="The user query string"),
    session_id: Optional[str] = Query(None, description="Optional conversation session ID"),
    profile: str = Query("balanced", description="Fast, Balanced, Quality execution profiles"),
    experiment_id: Optional[str] = Query(None, description="Optional A/B testing experiment ID")
):
    # Step 1: Check for Ambiguity before executing retrieval
    disambig = ambiguity_resolver.resolve_ambiguity(query)
    if disambig.is_ambiguous:
        return {
            "status": "ambiguous",
            "disambiguation": disambig.dict(),
            "answer": "Your query is ambiguous. Please select one of the clarification candidates.",
            "movies": []
        }
        
    try:
        response = await retrieval_client.search(
            query=query,
            session_id=session_id,
            profile=profile,
            experiment_id=experiment_id
        )
        return {
            "status": "success",
            "data": response.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval execution failed: {str(e)}")

@router.post("/recommend", response_model=Dict[str, Any])
async def recommend_query(
    query: str = Query(...),
    session_id: Optional[str] = Query(None),
    profile: str = Query("balanced")
):
    try:
        response = await retrieval_client.recommend(query, session_id, profile)
        return {"status": "success", "data": response.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/identify", response_model=Dict[str, Any])
async def identify_query(
    query: str = Query(...),
    session_id: Optional[str] = Query(None),
    profile: str = Query("balanced")
):
    try:
        response = await retrieval_client.identify(query, session_id, profile)
        return {"status": "success", "data": response.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/explain/{trace_id}", response_model=Dict[str, Any])
def explain_query(trace_id: str):
    explanation = retrieval_client.explain(trace_id)
    if "error" in explanation:
        raise HTTPException(status_code=404, detail=explanation["error"])
    return {"status": "success", "data": explanation}
