from typing import List, Dict
from app.retrieval.contract import CandidateMovie
from app.core.logging import get_logger

logger = get_logger("app.retrieval.diversity")

class CandidateDiversityEngine:
    """
    Diversifies query candidates to prevent recommendation redundancy.
    """
    def diversify(self, candidates: List[CandidateMovie], max_results: int = 10) -> List[CandidateMovie]:
        if not candidates:
            return []
            
        logger.info(f"Applying diversity engine constraints on {len(candidates)} candidates.")
        
        diversified: List[CandidateMovie] = []
        
        # Keep track of categories we've already included to apply penalties
        directors_seen: Dict[str, int] = {}
        genres_seen: Dict[str, int] = {}
        decades_seen: Dict[str, int] = {}
        
        # Sort incoming by score descending
        sorted_candidates = sorted(candidates, key=lambda c: c.score, reverse=True)
        
        for cand in sorted_candidates:
            # Extract attributes from metadata
            director = cand.metadata.get("director", "unknown").lower()
            genres = cand.metadata.get("genres", [])
            year = cand.metadata.get("year", 2000)
            decade = (year // 10) * 10
            
            penalty = 0.0
            
            # Apply penalties for overrepresented directors
            if director != "unknown" and director in directors_seen:
                penalty += 0.2 * directors_seen[director]
                
            # Apply penalties for overlapping genres
            for g in genres:
                g_lower = g.lower()
                if g_lower in genres_seen:
                    penalty += 0.05 * genres_seen[g_lower]
                    
            # Apply decade penalties
            if decade in decades_seen:
                penalty += 0.1 * decades_seen[decade]
                
            # Calibrate adjusted score
            adjusted_score = cand.score - penalty
            
            # Create a copy with the adjusted score
            cand_dict = cand.dict()
            cand_dict["score"] = round(adjusted_score, 4)
            updated_cand = CandidateMovie(**cand_dict)
            
            # Record attributes
            if director != "unknown":
                directors_seen[director] = directors_seen.get(director, 0) + 1
            for g in genres:
                g_lower = g.lower()
                genres_seen[g_lower] = genres_seen.get(g_lower, 0) + 1
            decades_seen[decade] = decades_seen.get(decade, 0) + 1
            
            diversified.append(updated_cand)
            
        # Re-sort using adjusted score
        diversified.sort(key=lambda c: c.score, reverse=True)
        logger.info(f"Diversity sorting complete. Top candidate is: ID {diversified[0].tmdb_id if diversified else 'none'}")
        return diversified[:max_results]

# Export singleton candidate diversity instance
diversity_engine = CandidateDiversityEngine()
