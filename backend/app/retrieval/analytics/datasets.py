from typing import List, Dict, Any
from pydantic import BaseModel, Field

class BenchmarkEntry(BaseModel):
    """
    Representation of a single golden validation entry.
    """
    query: str
    expected_movie_ids: List[int]
    expected_strategy: str
    expected_databases: List[str] = Field(default_factory=list)
    minimum_confidence: float = 0.5
    expected_keywords: List[str] = Field(default_factory=list)

class EvaluationReport(BaseModel):
    total_queries: int
    precision_at_1: float
    precision_at_5: float
    recall_at_5: float
    mean_reciprocal_rank: float
    average_latency_ms: float
    cache_hit_ratio: float
    failure_rate: float
