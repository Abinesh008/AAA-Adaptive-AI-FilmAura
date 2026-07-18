import math
import sqlalchemy as sa
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.movie import UserPreferenceProfile, UserInteractionHistory, Movie
from app.core.logging import get_logger

logger = get_logger("app.recommendation.profile")

class ProfileLearningEngine:
    """
    Profile engine learning user taste weights (genres, directors) from historical interactions with decay.
    """
    def __init__(self, half_life_days: float = 30.0):
        self.half_life_days = half_life_days
        # Compute decay constant lambda
        self.decay_lambda = math.log(2) / self.half_life_days

    def calculate_decay_weight(self, interaction_date: datetime) -> float:
        """
        Calculate decay coefficient where older items hold less weight.
        """
        delta = datetime.utcnow() - interaction_date
        days = max(0.0, delta.total_seconds() / 86400.0)
        return math.exp(-self.decay_lambda * days)

    def rebuild_profile(self, user_id: str, db: Session) -> None:
        """
        Aggregate user interaction signals, apply decay weights, and save preference profile.
        """
        logger.info(f"Rebuilding preference profile for user: {user_id}")
        
        interactions = db.query(UserInteractionHistory).filter(UserInteractionHistory.user_id == user_id).all()
        if not interactions:
            logger.info("No interaction history found. Skipping taste profile update.")
            return

        genre_scores: Dict[str, float] = {}
        director_scores: Dict[str, float] = {}
        actor_scores: Dict[str, float] = {}
        
        for interaction in interactions:
            movie = db.query(Movie).filter(sa.cast(Movie.tmdb_id, sa.Integer) == interaction.movie_id).first()
            if not movie:
                continue
                
            # Calculate decay factor
            weight = self.calculate_decay_weight(interaction.created_at)
            
            # Determine interaction coefficient
            coeff = 1.0
            if interaction.interaction_type == "skip":
                coeff = -1.5
            elif interaction.interaction_type == "rating":
                # Scale coefficient by rating (3.0 is neutral)
                rating_val = interaction.rating or 3.0
                coeff = (rating_val - 3.0) / 2.0
            elif interaction.interaction_type == "bookmark":
                coeff = 1.2
                
            val_to_add = coeff * weight
            
            # 1. Update Genre weights
            for genre in movie.genres:
                g_name = genre.name
                genre_scores[g_name] = genre_scores.get(g_name, 0.0) + val_to_add
                
            # 2. Update Director weights
            # Parse director from movie crew list
            for crew in movie.crew:
                if crew.job == "Director" and crew.person:
                    d_name = crew.person.name
                    director_scores[d_name] = director_scores.get(d_name, 0.0) + val_to_add

            # 3. Update Actor weights
            for cast in movie.cast[:5]:  # Primary top 5 cast
                if cast.person:
                    a_name = cast.person.name
                    actor_scores[a_name] = actor_scores.get(a_name, 0.0) + val_to_add

        # Calibrate weights (normalize to 0.0 - 1.0 scale, keeping negative bounds if skipped)
        final_genres = self._normalize_scores(genre_scores)
        
        # Sort and select top directors/actors (e.g. positive scores only)
        top_directors = [d for d, s in sorted(director_scores.items(), key=lambda x: x[1], reverse=True)[:5] if s > 0.0]
        top_actors = [a for a, s in sorted(actor_scores.items(), key=lambda x: x[1], reverse=True)[:10] if s > 0.0]

        # Save to database
        profile = db.query(UserPreferenceProfile).filter(UserPreferenceProfile.user_id == user_id).first()
        if not profile:
            profile = UserPreferenceProfile(user_id=user_id)
            db.add(profile)
            
        profile.genre_weights = final_genres
        profile.favorite_directors = top_directors
        profile.favorite_actors = top_actors
        profile.updated_at = datetime.utcnow()
        
        db.commit()
        logger.info(f"Taste profile rebuilt successfully for user {user_id}")

    def _normalize_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        if not scores:
            return {}
        max_val = max(abs(s) for s in scores.values())
        if max_val == 0.0:
            return {k: 0.0 for k in scores.keys()}
        # Map values to [-1.0, 1.0] range
        return {k: round(v / max_val, 3) for k, v in scores.items()}

# Export singleton engine instance
profile_learning_engine = ProfileLearningEngine()
