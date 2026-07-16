from typing import List, Dict, Any
from app.retrieval.datasets import BenchmarkEntry, EvaluationReport
from app.retrieval.contract import CandidateMovie
from app.core.logging import get_logger

logger = get_logger("app.retrieval.evaluation")

class RetrievalEvaluator:
    """
    Evaluator scoring metrics (Precision, Recall, MRR) for query candidate lists.
    """
    def calculate_metrics(
        self,
        results: List[CandidateMovie],
        entry: BenchmarkEntry,
        latency_ms: float,
        cache_hit: bool,
        failed: bool
    ) -> Dict[str, Any]:
        retrieved_ids = [c.tmdb_id for c in results]
        expected_ids = entry.expected_movie_ids
        
        # 1. Precision@1
        p_at_1 = 0.0
        if retrieved_ids and retrieved_ids[0] in expected_ids:
            p_at_1 = 1.0
            
        # 2. Precision@5
        top_5 = retrieved_ids[:5]
        hits_5 = sum(1 for rid in top_5 if rid in expected_ids)
        p_at_5 = hits_5 / 5.0 if top_5 else 0.0
        
        # 3. Recall@5
        r_at_5 = hits_5 / len(expected_ids) if expected_ids else 0.0
        
        # 4. Mean Reciprocal Rank (MRR)
        mrr = 0.0
        for idx, rid in enumerate(retrieved_ids):
            if rid in expected_ids:
                mrr = 1.0 / (idx + 1)
                break
                
        return {
            "precision_at_1": p_at_1,
            "precision_at_5": p_at_5,
            "recall_at_5": r_at_5,
            "mrr": mrr,
            "latency_ms": latency_ms,
            "cache_hit": cache_hit,
            "failed": failed
        }

    def compile_report(self, run_metrics: List[Dict[str, Any]]) -> EvaluationReport:
        total = len(run_metrics)
        if total == 0:
            return EvaluationReport(
                total_queries=0, precision_at_1=0.0, precision_at_5=0.0,
                recall_at_5=0.0, mean_reciprocal_rank=0.0, average_latency_ms=0.0,
                cache_hit_ratio=0.0, failure_rate=0.0
            )
            
        p1 = sum(m["precision_at_1"] for m in run_metrics) / total
        p5 = sum(m["precision_at_5"] for m in run_metrics) / total
        r5 = sum(m["recall_at_5"] for m in run_metrics) / total
        mrr = sum(m["mrr"] for m in run_metrics) / total
        latency = sum(m["latency_ms"] for m in run_metrics) / total
        cache = sum(1 for m in run_metrics if m["cache_hit"]) / total
        failures = sum(1 for m in run_metrics if m["failed"]) / total
        
        return EvaluationReport(
            total_queries=total,
            precision_at_1=round(p1, 3),
            precision_at_5=round(p5, 3),
            recall_at_5=round(r5, 3),
            mean_reciprocal_rank=round(mrr, 3),
            average_latency_ms=round(latency, 2),
            cache_hit_ratio=round(cache, 3),
            failure_rate=round(failures, 3)
        )

# Export singleton evaluator instance
evaluator = RetrievalEvaluator()
