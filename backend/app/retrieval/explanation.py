from typing import List, Dict, Any
from app.retrieval.contract import CandidateMovie
from app.core.logging import get_logger

logger = get_logger("app.retrieval.explanation")

class ExplanationEngine:
    """
    Generates natural language and structured visual explainability trees for retrieved candidates.
    """
    def generate_explanation(self, candidates: List[CandidateMovie]) -> Dict[str, Any]:
        if not candidates:
            return {
                "human_explanation": "No movies matched the query.",
                "explanation_tree": {}
            }

        top_cand = candidates[0]
        
        # Build natural language text
        sources = ", ".join(top_cand.matched_by_sources)
        human_text = (
            f"Recommended '{top_cand.title}' (ID {top_cand.tmdb_id}) as the top candidate. "
            f"It was verified across {sources} with an overall confidence of {top_cand.confidence}. "
        )
        
        # Add director or theme notes if present in metadata
        rel = top_cand.metadata.get("matched_relationship")
        if rel and rel != "unknown":
            human_text += f"Matched graph relationship: {rel}."

        # Compile structured visual explanation tree
        tree = {
            "node_name": "Query Resolution",
            "type": "root",
            "children": [
                {
                    "node_name": f"Top Candidate: {top_cand.title}",
                    "type": "movie",
                    "tmdb_id": top_cand.tmdb_id,
                    "confidence": top_cand.confidence,
                    "children": self._build_provenance_nodes(top_cand)
                }
            ]
        }
        
        return {
            "human_explanation": human_text,
            "explanation_tree": tree
        }

    def _build_provenance_nodes(self, candidate: CandidateMovie) -> List[Dict[str, Any]]:
        nodes = []
        for prov in candidate.provenance_details:
            nodes.append({
                "node_name": f"DB Source: {prov.database}",
                "type": "database",
                "table_or_label": prov.table_or_label,
                "node_id": prov.node_id_or_vector_id,
                "query": prov.query_executed,
                "weight": prov.confidence_contribution
            })
        return nodes

# Export singleton instance
explanation_engine = ExplanationEngine()
