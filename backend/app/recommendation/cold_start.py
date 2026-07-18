from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from app.models.movie import Movie, Genre, movie_genres
from app.core.logging import get_logger

logger = get_logger("app.recommendation.cold_start")

class ColdStartEngine:
    """
    Candidate generator for cold-start users lacking rating histories.
    Serves demographic-targeted, globally popular, and trending catalog movies.
    """
    def get_cold_start_recommendations(
        self,
        limit: int,
        region: str,
        age_demographic: str,  # "adult", "child"
        db: Session
    ) -> List[Dict[str, Any]]:
        logger.info(f"Generating cold-start recommendations. Region: {region}, Demographic: {age_demographic}")
        
        candidates: List[Dict[str, Any]] = []
        try:
            # Build filters based on age demographic
            filters = []
            if age_demographic == "child":
                filters.append(Movie.adult == False)

            # Query globally popular movies sorted by popularity DESC
            movies = db.query(Movie).filter(and_(*filters)).order_by(desc(Movie.popularity)).limit(limit * 2).all()
            
            for idx, movie in enumerate(movies):
                # Calculate simple descending score based on index rank
                score = round(1.0 - (idx / len(movies)), 3)
                
                # Mock regional filtering in cold start
                available_countries = ["US", "UK", "CA"]  # Safe default country license
                
                candidates.append({
                    "movie_id": int(movie.tmdb_id),
                    "title": movie.title,
                    "score": score,
                    "adult": movie.adult or False,
                    "available_countries": available_countries,
                    "premium_only": False,
                    "genres": [g.name for g in movie.genres],
                    "provenance_reason": "Trending globally: Popular choice among film fans"
                })
                
            # Filter regional constraints in-memory for cold-start fallback
            if region:
                candidates = [c for c in candidates if region in c["available_countries"]]

        except Exception as e:
            logger.error(f"Cold start generation failed: {str(e)}")

        return candidates[:limit]

# Instantiate cold start engine
cold_start_engine = ColdStartEngine()
