from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.movie import UserPreferenceProfile, UserInteractionHistory, Movie
from app.core.logging import get_logger

logger = get_logger("app.recommendation.feature_store")

class BaseFeatureStore(ABC):
    @abstractmethod
    def get_user_features(self, user_id: str, db: Session) -> Dict[str, Any]:
        """
        Fetch real-time user preference weights and session interaction stats.
        """
        pass

    @abstractmethod
    def get_movie_features(self, movie_id: int, db: Session) -> Dict[str, Any]:
        """
        Fetch static attributes and popularity scores of a movie candidate.
        """
        pass

    @abstractmethod
    def sync_offline_features(self, user_id: str, offline_data: Dict[str, Any], db: Session) -> None:
        """
        Sync online profiles with batch offline feature computations.
        """
        pass

class RecommendationFeatureStore(BaseFeatureStore):
    """
    Central user and movie feature store ensuring consistency across recommendation steps.
    """
    def get_user_features(self, user_id: str, db: Session) -> Dict[str, Any]:
        logger.info(f"Retrieving user features for: {user_id}")
        
        # 1. Fetch Preference Profile
        profile = db.query(UserPreferenceProfile).filter(UserPreferenceProfile.user_id == user_id).first()
        genre_weights = profile.genre_weights if profile else {}
        fav_directors = profile.favorite_directors if profile else []
        fav_actors = profile.favorite_actors if profile else []
        excluded_kws = profile.excluded_keywords if profile else []
        
        # 2. Fetch Interaction aggregates
        interactions = db.query(UserInteractionHistory).filter(UserInteractionHistory.user_id == user_id).all()
        
        total_clicks = sum(1 for i in interactions if i.interaction_type == "click")
        total_skips = sum(1 for i in interactions if i.interaction_type == "skip")
        ratings = [i.rating for i in interactions if i.rating is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
        
        # Return merged features
        return {
            "user_id": user_id,
            "genre_weights": genre_weights,
            "favorite_directors": fav_directors,
            "favorite_actors": fav_actors,
            "excluded_keywords": excluded_kws,
            "total_clicks": total_clicks,
            "total_skips": total_skips,
            "average_rating": avg_rating,
            "interaction_count": len(interactions),
            "updated_at": profile.updated_at.isoformat() if profile else datetime.utcnow().isoformat()
        }

    def get_movie_features(self, movie_id: int, db: Session) -> Dict[str, Any]:
        logger.debug(f"Retrieving movie features for ID: {movie_id}")
        movie = db.query(Movie).filter(Movie.tmdb_id == movie_id).first()
        if not movie:
            return {
                "movie_id": movie_id,
                "popularity": 0.0,
                "genres": [],
                "release_year": 0,
                "vote_average": 0.0
            }
            
        return {
            "movie_id": movie_id,
            "popularity": movie.popularity or 0.0,
            "genres": [g.name for g in movie.genres],
            "release_year": movie.release_year or 0,
            "vote_average": float(movie.vote_average) if movie.vote_average else 0.0
        }

    def sync_offline_features(self, user_id: str, offline_data: Dict[str, Any], db: Session) -> None:
        logger.info(f"Syncing offline features for: {user_id}")
        profile = db.query(UserPreferenceProfile).filter(UserPreferenceProfile.user_id == user_id).first()
        if not profile:
            profile = UserPreferenceProfile(user_id=user_id)
            db.add(profile)
            
        # Update weights from batch updates
        if "genre_weights" in offline_data:
            profile.genre_weights = offline_data["genre_weights"]
        if "favorite_directors" in offline_data:
            profile.favorite_directors = offline_data["favorite_directors"]
        if "favorite_actors" in offline_data:
            profile.favorite_actors = offline_data["favorite_actors"]
            
        profile.updated_at = datetime.utcnow()
        db.commit()

# Export singleton feature store instance
feature_store = RecommendationFeatureStore()
