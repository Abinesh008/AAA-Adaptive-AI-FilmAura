import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class QueryTrace(BaseModel):
    """
    Main traceability and observability contract generated for every query session.
    """
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    span_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: Optional[str] = None
    parent_trace_id: Optional[str] = None
    
    # Timestamps & profiler logs
    timeline: Dict[str, float] = Field(default_factory=dict)
    latencies: Dict[str, float] = Field(default_factory=dict)
    
    # Execution choices & metadata
    planner_decisions: Dict[str, Any] = Field(default_factory=dict)
    selected_databases: List[str] = Field(default_factory=list)
    expanded_queries: List[str] = Field(default_factory=list)
    cache_status: str = "miss"
    
    # Scoring logs
    fusion_scores: Dict[str, Dict[str, float]] = Field(default_factory=dict) # tmdb_id -> scores
    reranking_scores: Dict[str, Dict[str, float]] = Field(default_factory=dict) # tmdb_id -> scores
    confidence_breakdown: Dict[str, float] = Field(default_factory=dict)
    reasoning_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Versioning & feature matrix state
    configuration_hash: Optional[str] = None
    feature_flags: Dict[str, str] = Field(default_factory=dict)
    active_profile: str = "balanced"
    plugin_versions: Dict[str, str] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True

    def record_start(self, step_name: str) -> None:
        """
        Record the start timestamp of a pipeline step.
        """
        self.timeline[f"{step_name}_start"] = datetime.utcnow().timestamp()

    def record_end(self, step_name: str) -> None:
        """
        Record the end timestamp of a pipeline step and calculate latency.
        """
        end_time = datetime.utcnow().timestamp()
        self.timeline[f"{step_name}_end"] = end_time
        start_time = self.timeline.get(f"{step_name}_start")
        if start_time:
            self.latencies[step_name] = round((end_time - start_time) * 1000, 2) # in milliseconds
