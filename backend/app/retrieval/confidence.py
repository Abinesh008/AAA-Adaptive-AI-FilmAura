from typing import Dict, List
from app.retrieval.contract import CandidateMovie
from app.core.logging import get_logger

logger = get_logger("app.retrieval.confidence")

class ConfidenceEngine:
    """
    Calculates composite query confidence scores based on sub-layer results.
    """
    def calculate_confidence(self, candidates: List[CandidateMovie], databases_used: List[str]) -> Dict[str, float]:
        if not candidates:
            return {
                "sql_confidence": 0.0,
                "graph_confidence": 0.0,
                "vector_confidence": 0.0,
                "fusion_confidence": 0.0,
                "reasoning_confidence": 0.0,
                "final_confidence": 0.0
            }

        # Sub-layer calculations
        sql_conf = 1.0 if "postgres" in databases_used else 0.0
        graph_conf = 0.85 if "neo4j" in databases_used else 0.0
        vector_conf = 0.9 if "chromadb" in databases_used else 0.0
        
        # Fusion confidence: ratio of candidate agreement across multiple sources
        agreement_count = sum(1 for c in candidates if len(c.matched_by_sources) > 1)
        fusion_conf = round(agreement_count / len(candidates), 2) if candidates else 0.0
        
        # LLM self-evaluation default score
        reasoning_conf = 0.9
        
        # Composite final confidence weighted averages
        weights = {
            "sql": 0.2,
            "graph": 0.3,
            "vector": 0.3,
            "fusion": 0.2
        }
        
        weighted_sum = (
            (sql_conf * weights["sql"]) +
            (graph_conf * weights["graph"]) +
            (vector_conf * weights["vector"]) +
            (fusion_conf * weights["fusion"])
        )
        
        final_conf = round(weighted_sum, 2)
        
        breakdown = {
            "sql_confidence": sql_conf,
            "graph_confidence": graph_conf,
            "vector_confidence": vector_conf,
            "fusion_confidence": fusion_conf,
            "reasoning_confidence": reasoning_conf,
            "final_confidence": final_conf
        }
        
        logger.info(f"Composite confidence breakdown calculated: {breakdown}")
        return breakdown

# Export singleton instance
confidence_engine = ConfidenceEngine()
