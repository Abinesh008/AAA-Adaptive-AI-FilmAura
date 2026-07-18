from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from app.api import deps
from app.recommendation.sdk import recommendation_client
from app.recommendation.model_registry import model_registry
from app.recommendation.schemas import (
    RecommendationResponse, 
    FeedbackRequest, 
    UserTasteProfileResponse, 
    ModelPromotionRequest
)

router = APIRouter()

@router.post("/retrieve", response_model=RecommendationResponse)
async def retrieve_recommendations(
    limit: int = Query(default=10, ge=1, le=50),
    region: Optional[str] = Query(default=None),
    subscription_tier: str = Query(default="free"),
    is_child_profile: bool = Query(default=False),
    user_id: Optional[str] = Header(default="guest_user"),
    db: Session = Depends(deps.get_db)
):
    """
    Fetch personalized movie recommendations balanced across multiple scoring metrics.
    """
    try:
        response = await recommendation_client.get_recommendations(
            user_id=user_id,
            limit=limit,
            region=region,
            subscription_tier=subscription_tier,
            is_child_profile=is_child_profile,
            db=db
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation retrieval failed: {str(e)}"
        )

@router.post("/feedback", status_code=status.HTTP_204_NO_CONTENT)
async def submit_feedback(
    feedback: FeedbackRequest,
    user_id: Optional[str] = Header(default="guest_user"),
    db: Session = Depends(deps.get_db)
):
    """
    Log explicit ratings, clicks, bookmarks, or skips to rebuild user taste profiles.
    """
    try:
        await recommendation_client.record_feedback(
            user_id=user_id,
            movie_id=feedback.movie_id,
            interaction_type=feedback.interaction_type,
            rating=feedback.rating,
            db=db
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ingesting interaction feedback failed: {str(e)}"
        )

@router.get("/profile/{user_id}", response_model=UserTasteProfileResponse)
async def get_user_profile(
    user_id: str,
    db: Session = Depends(deps.get_db)
):
    """
    Retrieve taste profile weight aggregates and favorited directors.
    """
    try:
        profile = await recommendation_client.get_user_taste_coordinates(user_id, db)
        return {
            "user_id": user_id,
            "genre_weights": profile.get("genre_weights", {}),
            "favorite_directors": profile.get("favorite_directors", []),
            "favorite_actors": profile.get("favorite_actors", []),
            "interaction_count": profile.get("interaction_count", 0)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile retrieval failed: {str(e)}"
        )

@router.post("/model/promote", status_code=status.HTTP_200_OK)
async def promote_model_version(
    request: ModelPromotionRequest
):
    """
    Promote a model version config in the registry dynamically.
    """
    try:
        model_registry.promote_model(request.model_version, request.stage)
        return {"status": "success", "message": f"Version {request.model_version} promoted to {request.stage}"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Promotion failed: {str(e)}"
        )

@router.post("/model/rollback", status_code=status.HTTP_200_OK)
async def rollback_model_version(
    fallback_version: str = Query(default="v1.0.0")
):
    """
    Emergency rollback of active production model versions.
    """
    try:
        model_registry.rollback_production(fallback_version)
        return {"status": "success", "message": f"Active version rolled back to {fallback_version}"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rollback failed: {str(e)}"
        )
