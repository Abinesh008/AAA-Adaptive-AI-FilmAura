from app.retrieval.query.query_trace import QueryTrace
from app.core.logging import get_logger

logger = get_logger("app.retrieval.profiler")

class PipelineProfiler:
    """
    Profiler printing execution time breakdowns across query stages.
    """
    def log_profile_summary(self, trace: QueryTrace) -> None:
        summary = {step: f"{duration}ms" for step, duration in trace.latencies.items()}
        logger.info(f"Timeline profile summary: {summary}")

profiler = PipelineProfiler()
