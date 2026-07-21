from typing import Dict, List, Any
from app.retrieval.contracts.contract import CandidateMovie
from app.core.logging import get_logger

logger = get_logger("app.retrieval.quality")

class RetrievalQualityScorer:
    """
    Computes diagnostic quality metrics for finished queries.
    """
    def score_quality(
        self,
        candidates: List[CandidateMovie],
        databases_used: List[str],
        confidence_breakdown: Dict[str, float]
    ) -> Dict[str, Any]:
        if not candidates:
            return {
                "quality_score": 0.0,
                "completeness_score": 0.0,
                "agreement_score": 0.0,
                "retrieval_grade": "D"
            }

        # 1. Completeness score: checking database sources queried
        completeness = len(databases_used) / 3.0 # maximum 3 plugins
        completeness = min(completeness, 1.0)
        
        # 2. Agreement score: percentage of movies matched by multiple sources
        agreement = confidence_breakdown.get("fusion_confidence", 0.0)
        
        # 3. Quality score: composite of completeness, agreement and final confidence
        final_conf = confidence_breakdown.get("final_confidence", 0.5)
        quality = round((completeness * 0.3) + (agreement * 0.3) + (final_conf * 0.4), 2)
        
        # Assign Grade
        grade = "D"
        if quality >= 0.85:
            grade = "A+"
        elif quality >= 0.75:
            grade = "A"
        elif quality >= 0.60:
            grade = "B"
        elif quality >= 0.40:
            grade = "C"
            
        result = {
            "quality_score": quality,
            "completeness_score": round(completeness, 2),
            "agreement_score": round(agreement, 2),
            "retrieval_grade": grade
        }
        
        logger.info(f"Diagnostic retrieval quality scored: {result}")
        return result

# Export singleton instance
quality_scorer = RetrievalQualityScorer()
