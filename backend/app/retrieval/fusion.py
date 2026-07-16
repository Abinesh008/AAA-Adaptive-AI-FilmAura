from typing import List, Dict, Any
from app.retrieval.contract import RetrievalResult, CandidateMovie, FusionResult, ProvenanceChain
from app.core.logging import get_logger

logger = get_logger("app.retrieval.fusion")

class HybridCoordinator:
    """
    Pluggable Fusion Coordinator merging retrieval results across different databases.
    """
    def fuse_results(self, results: List[RetrievalResult], strategy: str = "rrf") -> FusionResult:
        if not results:
            return FusionResult(candidates=[], fusion_algorithm=strategy)
            
        logger.info(f"Fusing {len(results)} results using strategy: {strategy}")
        
        # Group raw inputs by tmdb_id
        grouped: Dict[str, List[RetrievalResult]] = {}
        for res in results:
            id_key = res.entity_id
            if id_key not in grouped:
                grouped[id_key] = []
            grouped[id_key].append(res)
            
        candidates: List[CandidateMovie] = []
        
        if strategy.lower() == "rrf" or strategy.lower() == "weighted_rrf":
            candidates = self._run_rrf(grouped)
        elif strategy.lower() == "borda":
            candidates = self._run_borda(grouped)
        else:
            # Default fallback: Simple average calibration score
            candidates = self._run_simple_average(grouped)
            
        # Order by final score descending
        candidates.sort(key=lambda c: c.score, reverse=True)
        return FusionResult(candidates=candidates, fusion_algorithm=strategy)

    def _run_rrf(self, grouped: Dict[str, List[RetrievalResult]], k: int = 60) -> List[CandidateMovie]:
        candidates = []
        
        # Compute RRF score: Sum( 1 / (k + rank_in_db) )
        # First sort each database results to assign ranks
        db_ranks: Dict[str, List[str]] = {}  # db -> list of entity_ids ordered by score desc
        for entity_id, res_list in grouped.items():
            for res in res_list:
                db = res.source
                if db not in db_ranks:
                    db_ranks[db] = []
                db_ranks[db].append((entity_id, res.score))
                
        # Sort ranks inside each db
        for db in db_ranks:
            db_ranks[db].sort(key=lambda x: x[1], reverse=True)
            db_ranks[db] = [x[0] for x in db_ranks[db]]
            
        for entity_id, res_list in grouped.items():
            rrf_score = 0.0
            sources = []
            provenance = []
            titles = []
            
            for res in res_list:
                db = res.source
                if db not in sources:
                    sources.append(db)
                provenance.append(res.provenance)
                
                title = res.metadata.get("title")
                if title and title not in titles:
                    titles.append(title)
                    
                # Rank index is 0-indexed in db_ranks list
                if entity_id in db_ranks[db]:
                    rank = db_ranks[db].index(entity_id) + 1
                    rrf_score += 1.0 / (k + rank)
                    
            candidates.append(CandidateMovie(
                tmdb_id=int(entity_id),
                title=titles[0] if titles else f"Movie {entity_id}",
                score=round(rrf_score, 6),
                confidence=round(sum(res.confidence for res in res_list) / len(res_list), 2),
                matched_by_sources=sources,
                provenance_details=provenance,
                metadata={"rrf_score": rrf_score}
            ))
            
        return candidates

    def _run_borda(self, grouped: Dict[str, List[RetrievalResult]]) -> List[CandidateMovie]:
        candidates = []
        # Expose Borda count ranks: candidates get points depending on how many candidates they beat
        db_lists: Dict[str, List[str]] = {}
        for entity_id, res_list in grouped.items():
            for res in res_list:
                db = res.source
                if db not in db_lists:
                    db_lists[db] = []
                db_lists[db].append((entity_id, res.score))
                
        for db in db_lists:
            db_lists[db].sort(key=lambda x: x[1], reverse=True)
            db_lists[db] = [x[0] for x in db_lists[db]]
            
        for entity_id, res_list in grouped.items():
            borda_score = 0.0
            sources = []
            provenance = []
            titles = []
            
            for res in res_list:
                db = res.source
                if db not in sources:
                    sources.append(db)
                provenance.append(res.provenance)
                
                title = res.metadata.get("title")
                if title and title not in titles:
                    titles.append(title)
                    
                if entity_id in db_lists[db]:
                    # Points = total candidates - rank
                    borda_score += len(db_lists[db]) - db_lists[db].index(entity_id)
                    
            candidates.append(CandidateMovie(
                tmdb_id=int(entity_id),
                title=titles[0] if titles else f"Movie {entity_id}",
                score=borda_score,
                confidence=round(sum(res.confidence for res in res_list) / len(res_list), 2),
                matched_by_sources=sources,
                provenance_details=provenance,
                metadata={"borda_score": borda_score}
            ))
            
        return candidates

    def _run_simple_average(self, grouped: Dict[str, List[RetrievalResult]]) -> List[CandidateMovie]:
        candidates = []
        for entity_id, res_list in grouped.items():
            score_avg = sum(res.score for res in res_list) / len(res_list)
            sources = list(set(res.source for res in res_list))
            provenance = [res.provenance for res in res_list]
            titles = list(set(res.metadata.get("title") for res in res_list if res.metadata.get("title")))
            
            candidates.append(CandidateMovie(
                tmdb_id=int(entity_id),
                title=titles[0] if titles else f"Movie {entity_id}",
                score=round(score_avg, 4),
                confidence=round(sum(res.confidence for res in res_list) / len(res_list), 2),
                matched_by_sources=sources,
                provenance_details=provenance,
                metadata={"average_score": score_avg}
            ))
        return candidates

# Export singleton hybrid fusion coordinator instance
hybrid_coordinator = HybridCoordinator()
