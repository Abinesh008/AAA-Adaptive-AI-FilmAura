import threading
from typing import Dict, Any, List
from app.retrieval.query.query_trace import QueryTrace
from app.core.logging import get_logger

logger = get_logger("app.retrieval.analytics")

class RetrievalAnalytics:
    """
    Analytics recorder compiling query latencies and pipeline execution statistics.
    """
    def __init__(self):
        self._total_queries = 0
        self._cache_hits = 0
        self._circuit_trips = 0
        self._latencies: List[float] = []
        self._slow_queries: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def record_query(self, trace: QueryTrace) -> None:
        with self._lock:
            self._total_queries += 1
            if trace.cache_status == "hit":
                self._cache_hits += 1
                
            total_latency = trace.latencies.get("total", 0.0)
            if total_latency > 0.0:
                self._latencies.append(total_latency)
                # Keep sliding window of last 1000 latencies
                if len(self._latencies) > 1000:
                    self._latencies.pop(0)
                    
            # Record slow query traces (exceeding 2 seconds)
            if total_latency > 2000.0:
                self._slow_queries.append({
                    "trace_id": trace.trace_id,
                    "latency_ms": total_latency,
                    "databases": trace.selected_databases.copy(),
                    "active_profile": trace.active_profile
                })
                if len(self._slow_queries) > 50:
                    self._slow_queries.pop(0)

    def get_diagnostics_metrics(self) -> Dict[str, Any]:
        with self._lock:
            avg_lat = round(sum(self._latencies) / len(self._latencies), 2) if self._latencies else 0.0
            p95_lat = 0.0
            if self._latencies:
                sorted_lat = sorted(self._latencies)
                idx = int(len(sorted_lat) * 0.95)
                p95_lat = sorted_lat[min(idx, len(sorted_lat) - 1)]
                
            hit_ratio = round(self._cache_hits / self._total_queries, 3) if self._total_queries > 0 else 0.0
            
            return {
                "total_queries_executed": self._total_queries,
                "cache_hit_ratio": hit_ratio,
                "average_latency_ms": avg_lat,
                "p95_latency_ms": p95_lat,
                "slow_queries_count": len(self._slow_queries),
                "recent_slow_queries": self._slow_queries.copy()
            }

# Export singleton analytics recorder
retrieval_analytics = RetrievalAnalytics()
