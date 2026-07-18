import math
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.movie import Movie
from app.core.logging import get_logger

logger = get_logger("app.recommendation.scorer")

class MultiStageScorer:
    """
    Stateless candidate scorer balancing multiple objectives: relevance, popularity, freshness, novelty, and serendipity.
    Applies Maximal Marginal Relevance (MMR) for genre diversification.
    """
    def __init__(
        self,
        w_relevance: float = 0.5,
        w_popularity: float = 0.1,
        w_freshness: float = 0.1,
        w_novelty: float = 0.1,
        w_serendipity: float = 0.2
    ):
        self.w_relevance = w_relevance
        self.w_popularity = w_popularity
        self.w_freshness = w_freshness
        self.w_novelty = w_novelty
        self.w_serendipity = w_serendipity

    def score_candidates(
        self,
        candidates: List[Dict[str, Any]],
        user_features: Dict[str, Any],
        db: Session
    ) -> List[Dict[str, Any]]:
        """
        Calculates a multi-objective score for all candidate movies.
        """
        logger.info(f"Scoring {len(candidates)} candidates for user {user_features.get('user_id')}")
        
        scored_list: List[Dict[str, Any]] = []
        current_year = datetime.utcnow().year

        # Fetch candidate metadata from db for scoring metrics
        movie_ids = [c["movie_id"] for c in candidates]
        movies = db.query(Movie).filter(Movie.tmdb_id.in_([str(mid) for mid in movie_ids])).all()
        movie_map = {int(m.tmdb_id): m for m in movies}

        user_genres = user_features.get("genre_weights", {})

        for candidate in candidates:
            m_id = candidate["movie_id"]
            base_relevance = candidate["score"]
            movie = movie_map.get(m_id)
            
            if not movie:
                # Fallback scores if movie metadata is missing
                scored_list.append({**candidate, "final_score": base_relevance})
                continue

            # 1. Popularity Score: normalize tmdb popularity [0.0, 1.0]
            pop_raw = movie.popularity or 0.0
            popularity_score = min(1.0, pop_raw / 200.0)

            # 2. Freshness Score: boost newer movies
            release_yr = movie.release_year or (current_year - 20)
            age = max(0, current_year - release_yr)
            freshness_score = math.exp(-0.05 * age)  # Exponential decay over age

            # 3. Novelty Score: inverse of popularity
            novelty_score = 1.0 - popularity_score

            # 4. Serendipity Score: high relevance, but genre is NOT heavily watched by user
            movie_genres = [g.name for g in movie.genres]
            avg_genre_affinity = 0.0
            if movie_genres:
                avg_genre_affinity = sum(user_genres.get(g, 0.0) for g in movie_genres) / len(movie_genres)
            
            # Serendipity favors movies outside user's primary high-weight genres
            serendipity_score = base_relevance * (1.0 - max(0.0, avg_genre_affinity))

            # Combine scores with weights
            final_score = (
                self.w_relevance * base_relevance +
                self.w_popularity * popularity_score +
                self.w_freshness * freshness_score +
                self.w_novelty * novelty_score +
                self.w_serendipity * serendipity_score
            )

            scored_list.append({
                "movie_id": m_id,
                "title": movie.title,
                "base_relevance": base_relevance,
                "popularity_score": round(popularity_score, 3),
                "freshness_score": round(freshness_score, 3),
                "novelty_score": round(novelty_score, 3),
                "serendipity_score": round(serendipity_score, 3),
                "genres": movie_genres,
                "final_score": round(final_score, 4),
                "provenance_reason": candidate.get("provenance_reason", "Recommended based on user preferences")
            })

        # Sort by final score descending
        scored_list.sort(key=lambda x: x["final_score"], reverse=True)
        return scored_list

    def diversify_candidates(
        self,
        scored_candidates: List[Dict[str, Any]],
        limit: int,
        lambda_factor: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Maximal Marginal Relevance (MMR) implementation to diversify candidates list.
        Balances final_score and genre overlap penalties.
        """
        if not scored_candidates:
            return []
            
        selected: List[Dict[str, Any]] = [scored_candidates[0]]
        remaining = scored_candidates[1:]
        selected_genres = set(scored_candidates[0]["genres"])

        while len(selected) < limit and remaining:
            best_mmr = -100.0
            best_cand = None

            for cand in remaining:
                # Calculate maximum similarity overlap with already selected set
                cand_genres = cand["genres"]
                overlap = len(selected_genres.intersection(cand_genres))
                sim_penalty = overlap / max(1, len(cand_genres))

                # MMR score = lambda * score - (1 - lambda) * similarity_penalty
                mmr_score = lambda_factor * cand["final_score"] - (1.0 - lambda_factor) * sim_penalty
                if mmr_score > best_mmr:
                    best_mmr = mmr_score
                    best_cand = cand

            if best_cand:
                selected.append(best_cand)
                remaining.remove(best_cand)
                selected_genres.update(best_cand["genres"])
            else:
                break

        return selected

# Instantiate scorer singleton
multi_stage_scorer = MultiStageScorer()
