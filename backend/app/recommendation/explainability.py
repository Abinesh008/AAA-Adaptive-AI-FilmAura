from typing import List, Dict, Any
from app.core.logging import get_logger

logger = get_logger("app.recommendation.explainability")

class RecommendationExplainer:
    """
    Translates algorithm provenance scores and attributes into human-readable movie explanations.
    """
    def generate_explanation(
        self,
        candidate: Dict[str, Any],
        user_features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Appends or formats the explanation justification string for a candidate recommendation.
        """
        movie_id = candidate["movie_id"]
        genres = candidate.get("genres", [])
        prov_reason = candidate.get("provenance_reason", "")
        
        # User details for tailoring the message
        fav_directors = user_features.get("favorite_directors", [])
        fav_actors = user_features.get("favorite_actors", [])
        
        explanation = "Recommended based on your movie profile."
        
        # 1. Custom overrides (e.g. bubble breaker or exploration)
        if "exploration selection" in prov_reason:
            explanation = "Expanding your horizon: A highly-rated choice from genres you haven't explored much yet."
            
        # 2. Match directors
        elif any(director in prov_reason for director in fav_directors):
            matching_directors = [d for d in fav_directors if d in prov_reason]
            explanation = f"Recommended because you favor directors like {', '.join(matching_directors)}."
            
        # 3. Match genres or general watch profile overlaps
        elif genres:
            user_genres = user_features.get("genre_weights", {})
            # Find the strongest overlapping genre
            matching_genres = [g for g in genres if user_genres.get(g, 0.0) >= 0.5]
            if matching_genres:
                explanation = f"Recommended because you enjoy {', '.join(matching_genres)} films."
            else:
                explanation = f"Matches your general taste in {', '.join(genres[:2])} movies."
                
        # 4. Collaborative filtering explanation
        elif "similar watch profiles" in prov_reason:
            explanation = "A popular selection among movie fans with tastes similar to yours."

        return {
            "movie_id": movie_id,
            "title": candidate.get("title", f"Movie #{movie_id}"),
            "final_score": candidate.get("final_score", 0.0),
            "explanation": explanation,
            "provenance_metadata": {
                "base_relevance": candidate.get("base_relevance", 0.0),
                "popularity_score": candidate.get("popularity_score", 0.0),
                "freshness_score": candidate.get("freshness_score", 0.0),
                "novelty_score": candidate.get("novelty_score", 0.0),
                "serendipity_score": candidate.get("serendipity_score", 0.0),
                "raw_reason": prov_reason
            }
        }

# Export explainer instance
recommendation_explainer = RecommendationExplainer()
