from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from app.recommendation.interfaces.plugin import BaseRecommendationPlugin
from app.models.movie import UserInteractionHistory, Movie
from app.retrieval.query_trace import QueryTrace
from app.core.logging import get_logger

logger = get_logger("app.recommendation.plugins.collaborative")

class CosineCFPlugin(BaseRecommendationPlugin):
    """
    User-User Collaborative Filtering candidate generator plugin.
    Identifies users with overlapping watch/rating history to suggest unviewed movies.
    """
    @property
    def name(self) -> str:
        return "collaborative_filtering"

    async def generate_candidates(
        self, 
        user_id: str, 
        limit: int, 
        db: Session, 
        trace: QueryTrace
    ) -> List[Dict[str, Any]]:
        logger.info(f"Generating collaborative filtering candidates for user: {user_id}")
        trace.record_start("plugin_collaborative")
        
        candidates: List[Dict[str, Any]] = []
        try:
            # 1. Get current user's liked movies (rating >= 4.0 or bookmark)
            user_likes = db.query(UserInteractionHistory.movie_id).filter(
                and_(
                    UserInteractionHistory.user_id == user_id,
                    UserInteractionHistory.interaction_type.in_(["rating", "bookmark"])
                )
            ).all()
            
            liked_movie_ids = [like[0] for like in user_likes]
            if not liked_movie_ids:
                logger.info("User has no liked movies recorded. Collaborative plugin returning zero candidates.")
                trace.record_end("plugin_collaborative")
                return []

            # 2. Find similar users who liked the same movies (excluding target user)
            similar_users_query = db.query(UserInteractionHistory.user_id).filter(
                and_(
                    UserInteractionHistory.movie_id.in_(liked_movie_ids),
                    UserInteractionHistory.user_id != user_id,
                    UserInteractionHistory.interaction_type.in_(["rating", "bookmark"])
                )
            ).distinct().limit(50).all()
            
            similar_user_ids = [su[0] for su in similar_users_query]
            if not similar_user_ids:
                logger.info("No similar users found in interaction history.")
                trace.record_end("plugin_collaborative")
                return []

            # 3. Find movies liked by similar users that the target user has not interacted with
            target_interacted_query = db.query(UserInteractionHistory.movie_id).filter(
                UserInteractionHistory.user_id == user_id
            ).all()
            interacted_movie_ids = {m[0] for m in target_interacted_query}

            recommendations = db.query(
                UserInteractionHistory.movie_id,
                UserInteractionHistory.rating
            ).filter(
                and_(
                    UserInteractionHistory.user_id.in_(similar_user_ids),
                    ~UserInteractionHistory.movie_id.in_(interacted_movie_ids),
                    UserInteractionHistory.interaction_type == "rating"
                )
            ).order_by(desc(UserInteractionHistory.rating)).limit(limit * 2).all()

            # 4. Group and compute normalized scores
            movie_ratings: Dict[int, List[float]] = {}
            for m_id, rating in recommendations:
                if rating is not None:
                    movie_ratings.setdefault(m_id, []).append(rating)

            for m_id, ratings in movie_ratings.items():
                avg_rating = sum(ratings) / len(ratings)
                # Calibrate score to [0.0, 1.0] range (assuming 5-star rating system)
                normalized_score = min(1.0, max(0.0, avg_rating / 5.0))
                candidates.append({
                    "movie_id": m_id,
                    "score": round(normalized_score, 3),
                    "provenance_reason": f"Highly rated by users with similar watch profiles (average rating: {avg_rating:.1f}/5)"
                })

            # Sort candidates by score descending and truncate to limit
            candidates.sort(key=lambda x: x["score"], reverse=True)
            candidates = candidates[:limit]

        except Exception as e:
            logger.error(f"Collaborative filtering plugin failed: {str(e)}")
            
        trace.record_end("plugin_collaborative")
        return candidates

# Instantiate plugin singleton
collaborative_plugin = CosineCFPlugin()
