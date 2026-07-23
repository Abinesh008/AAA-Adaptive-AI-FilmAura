from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logging import get_logger
from app.retrieval.contracts.contract import CandidateMovie
from app.retrieval.core.features import features

logger = get_logger("app.retrieval.reranker")


class BaseReranker(ABC):
    @abstractmethod
    def rerank(self, candidates: List[CandidateMovie], query: str, experiment_id: Optional[str] = None) -> List[CandidateMovie]:
        pass


class MultiStageReranker(BaseReranker):
    """
    Reranking engine implementing 6 independent candidate evaluation passes.
    """
    def rerank(self, candidates: List[CandidateMovie], query: str, experiment_id: Optional[str] = None) -> List[CandidateMovie]:
        if not candidates or not features.is_enabled("reranking"):
            return candidates

        logger.info(f"Reranking {len(candidates)} candidates. Experiment ID: {experiment_id}")

        # Load weights from settings configuration
        weights = settings.RERANKING_WEIGHTS.copy()

        # Adjust weights if specific experiment_id passed (A/B testing framework)
        if experiment_id == "exp_graph_heavy":
            weights = {"semantic": 0.2, "graph": 0.6, "keyword": 0.1, "popularity": 0.1}
        elif experiment_id == "exp_semantic_heavy":
            weights = {"semantic": 0.7, "graph": 0.1, "keyword": 0.1, "popularity": 0.1}

        reranked = []
        for cand in candidates:
            # 6-Pass Calculation
            score = 0.0

            # Pass 1: Database relevance alignment (Base score)
            base_relevance = cand.score

            # Pass 2: Semantic Similarity (Chroma score normalized)
            semantic_score = cand.metadata.get("distance", 0.5)
            # Map distance: lower is better
            semantic_factor = round(1.0 / (1.0 + semantic_score), 4)
            score += semantic_factor * weights.get("semantic", 0.4)

            # Pass 3: Keyword overlap match
            overlap_count = 0
            query_words = set(query.lower().split(" "))
            title_words = set(cand.title.lower().split(" "))
            overlap_count += len(query_words.intersection(title_words))
            keyword_factor = min(overlap_count / 3.0, 1.0)
            score += keyword_factor * weights.get("keyword", 0.1)

            # Pass 4: Knowledge Graph connectivity richness
            graph_factor = 0.0
            if "neo4j" in cand.matched_by_sources:
                # Give boost if verified in graph
                graph_factor = 1.0
            score += graph_factor * weights.get("graph", 0.3)

            # Pass 5: Popularity & rating metrics
            popularity = cand.metadata.get("popularity", 10.0)
            # Logarithmic mapping of popularity
            popularity_factor = min(popularity / 100.0, 1.0)
            score += popularity_factor * weights.get("popularity", 0.2)

            # Pass 6: Freshness recency
            year = cand.metadata.get("year", 2000)
            freshness_factor = min((year - 1980) / 46.0, 1.0) if year > 1980 else 0.0
            score += freshness_factor * 0.05  # minor freshness multiplier

            # Reconstruct candidate with updated reranked score
            cand_dict = cand.dict()
            cand_dict["score"] = round(score, 4)
            reranked.append(CandidateMovie(**cand_dict))

        # Re-sort candidates by final scores
        reranked.sort(key=lambda c: c.score, reverse=True)
        return reranked


# Export singleton reranker instance
reranker = MultiStageReranker()
