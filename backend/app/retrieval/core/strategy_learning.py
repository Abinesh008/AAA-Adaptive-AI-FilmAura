import threading
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from app.core.logging import get_logger

logger = get_logger("app.retrieval.strategy_learning")

class StrategyMetrics(BaseModel):
    runs: int = 0
    successes: int = 0
    avg_latency_ms: float = 0.0
    avg_confidence: float = 0.0

class StrategyLearningEngine:
    """
    Tracks execution performance statistics to adapt planner decisions over time.
    """
    def __init__(self):
        self._stats: Dict[str, Dict[str, StrategyMetrics]] = {}  # query_type -> strategy -> stats
        self._lock = threading.Lock()

    def record_execution(
        self,
        query_type: str,
        strategy: str,
        latency_ms: float,
        confidence: float,
        success: bool
    ) -> None:
        qtype = query_type.lower()
        strat = strategy.lower()
        
        with self._lock:
            if qtype not in self._stats:
                self._stats[qtype] = {}
            if strat not in self._stats[qtype]:
                self._stats[qtype][strat] = StrategyMetrics()
                
            stats = self._stats[qtype][strat]
            stats.runs += 1
            if success:
                stats.successes += 1
            
            # Running average calculations
            stats.avg_latency_ms = round(((stats.avg_latency_ms * (stats.runs - 1)) + latency_ms) / stats.runs, 2)
            stats.avg_confidence = round(((stats.avg_confidence * (stats.runs - 1)) + confidence) / stats.runs, 3)
            
            logger.info(f"Recorded strategy run: type={qtype}, strat={strat}, latency={latency_ms}ms, confidence={confidence}")

    def get_preferred_strategy(self, query_type: str) -> Optional[str]:
        """
        Recommend the strategy with the lowest latency-confidence score ratio.
        """
        qtype = query_type.lower()
        with self._lock:
            strategies = self._stats.get(qtype)
            if not strategies:
                return None
                
            best_strat = None
            best_score = float("inf")
            
            for strat, metrics in strategies.items():
                if metrics.successes == 0 or metrics.runs < 3:
                    continue  # Wait for a few warm-up runs
                
                # Custom scoring ratio: low latency & high confidence is better
                score = metrics.avg_latency_ms / (metrics.avg_confidence + 0.01)
                if score < best_score:
                    best_score = score
                    best_strat = strat
            
            if best_strat:
                logger.info(f"Strategy recommendation for '{qtype}': {best_strat} (score: {round(best_score, 2)})")
            return best_strat

    def get_all_stats(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        with self._lock:
            result = {}
            for qtype, strats in self._stats.items():
                result[qtype] = {}
                for strat, metrics in strats.items():
                    result[qtype][strat] = metrics.dict()
            return result

from typing import Optional
strategy_learning_engine = StrategyLearningEngine()
