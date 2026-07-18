from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Any, Optional

class RecommendationItem(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    movie_id: int
    title: str
    final_score: float
    explanation: str
    genres: List[str]

class RecommendationResponse(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    user_id: str
    experiment_group: str
    recommendations: List[RecommendationItem]
    trace_id: str

class FeedbackRequest(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    movie_id: int
    interaction_type: str = Field(description="click, skip, rating, bookmark")
    rating: Optional[float] = None

class UserTasteProfileResponse(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    user_id: str
    genre_weights: Dict[str, float]
    favorite_directors: List[str]
    favorite_actors: List[str]
    interaction_count: int

class ModelPromotionRequest(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    model_version: str
    stage: str = Field(description="production, shadow, staging")
