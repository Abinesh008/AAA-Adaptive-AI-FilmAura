from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base_class import Base
from app.models.base import JSON_TYPE

class UserPreferenceProfile(Base):
    """UserPreferenceProfile storing calculated taste weightings, favorite actors/directors, and exclusions."""
    __tablename__ = "user_preference_profiles"
    
    user_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    genre_weights: Mapped[dict] = mapped_column(JSON_TYPE, default=dict, nullable=False)
    favorite_directors: Mapped[list] = mapped_column(JSON_TYPE, default=list, nullable=False)
    favorite_actors: Mapped[list] = mapped_column(JSON_TYPE, default=list, nullable=False)
    excluded_keywords: Mapped[list] = mapped_column(JSON_TYPE, default=list, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class UserInteractionHistory(Base):
    """UserInteractionHistory logging explicit feedback interactions (bookmarks, ratings, etc.) for taste updates."""
    __tablename__ = "user_interaction_histories"
    
    user_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    movie_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    interaction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_watched_sec: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
