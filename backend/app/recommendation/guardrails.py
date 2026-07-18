from typing import List, Dict, Any
from app.core.logging import get_logger

logger = get_logger("app.recommendation.guardrails")

class FilterBubbleBreaker:
    """
    Enforces catalog coverage diversity and prevents recommendation loops.
    Swaps lower ranking slots with exploration candidates outside user's top genre affinity.
    """
    def __init__(self, exploration_ratio: float = 0.15):
        self.exploration_ratio = exploration_ratio

    def break_bubble(
        self,
        final_list: List[Dict[str, Any]],
        all_candidates: List[Dict[str, Any]],
        user_features: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Injects a percentage of movies from genres the user has low affinity for.
        """
        if not final_list or not all_candidates:
            return final_list

        limit = len(final_list)
        exploration_count = max(1, int(limit * self.exploration_ratio))
        
        # 1. Identify user's favorite genres (weights >= 0.5)
        user_genres = user_features.get("genre_weights", {})
        favorite_genres = {g for g, w in user_genres.items() if w >= 0.5}
        
        # 2. Find exploration candidates (movies with genres outside favorite_genres)
        exploration_candidates: List[Dict[str, Any]] = []
        for cand in all_candidates:
            cand_genres = cand.get("genres", [])
            # If movie doesn't overlap with favorite genres, it is an exploration film
            if not favorite_genres.intersection(cand_genres):
                exploration_candidates.append(cand)

        if not exploration_candidates:
            logger.info("No suitable exploration candidates found outside user's favorite genres.")
            return final_list

        # Sort exploration candidates by relevance score descending
        exploration_candidates.sort(key=lambda x: x.get("final_score", 0.0), reverse=True)
        
        # 3. Swap the lowest ranking slots of the final list
        result = list(final_list)
        swapped_count = 0
        
        for exp_cand in exploration_candidates:
            if swapped_count >= exploration_count:
                break
            
            # Avoid duplicating movies already in the top section
            if exp_cand["movie_id"] not in {m["movie_id"] for m in result}:
                idx_to_swap = len(result) - 1 - swapped_count
                if idx_to_swap >= 0:
                    logger.info(f"Bubble breaker swapping slot {idx_to_swap} with exploration movie {exp_cand['movie_id']}.")
                    result[idx_to_swap] = {
                        **exp_cand,
                        "provenance_reason": "Suggested to expand your movie horizon (exploration selection)"
                    }
                    swapped_count += 1

        return result

class RecommendationGuardrailEngine:
    """
    Unified manager executing content protection and filter bubble breakers on final recommendations.
    """
    def __init__(self):
        self.bubble_breaker = FilterBubbleBreaker()

    def validate_and_adjust(
        self,
        final_list: List[Dict[str, Any]],
        all_candidates: List[Dict[str, Any]],
        user_features: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        # Enforce bubble breaking
        adjusted = self.bubble_breaker.break_bubble(final_list, all_candidates, user_features)
        return adjusted

# Export guardrail instance
recommendation_guardrails = RecommendationGuardrailEngine()
