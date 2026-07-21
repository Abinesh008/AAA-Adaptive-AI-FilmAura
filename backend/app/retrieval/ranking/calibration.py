from typing import List
from app.retrieval.contracts.contract import RetrievalResult
from app.core.logging import get_logger

logger = get_logger("app.retrieval.calibration")

class ScoreCalibrator:
    """
    Standardizes database search relevance and distance metrics to standard 0-1 confidence metrics.
    """
    def calibrate_scores(self, results: List[RetrievalResult]) -> List[RetrievalResult]:
        calibrated = []
        for res in results:
            source = res.source.lower()
            original_score = res.score
            calibrated_score = 1.0
            
            if source == "chromadb":
                # L2 distance metric normalization: distance near 0 means similar (1.0).
                # Limit distance mapping to standard range.
                if original_score < 0:
                    calibrated_score = 1.0
                else:
                    calibrated_score = round(1.0 / (1.0 + original_score), 4)
            elif source == "neo4j":
                # Neo4j paths / count connections. E.g., original score can represent paths count
                calibrated_score = min(original_score, 1.0)
            elif source == "postgres":
                # SQL matches default to full confidence
                calibrated_score = min(original_score, 1.0)
                
            # Create a copy with updated calibrated score
            res_dict = res.dict()
            res_dict["score"] = calibrated_score
            calibrated.append(RetrievalResult(**res_dict))
            
        logger.info(f"Calibrated {len(results)} retrieval scores.")
        return calibrated

score_calibrator = ScoreCalibrator()
