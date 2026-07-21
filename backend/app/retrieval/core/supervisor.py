import asyncio
import time
from typing import List, Dict, Any
from app.core.logging import get_logger
from app.retrieval.contracts.contract import ExecutionPlan, RetrievalResult, ExecutionStep
from app.retrieval.reasoning.evidence import Evidence
from app.retrieval.query.query_trace import QueryTrace
from app.retrieval.core.circuit_breaker import circuit_breakers
from app.retrieval.contracts.resources import resources
from app.retrieval.core.registry import capability_registry

logger = get_logger("app.retrieval.supervisor")

class ParallelSupervisor:
    """
    Supervisor coordinating concurrent plugin executions safely inside circuit breaker wrappers.
    """
    async def execute_plan(self, plan: ExecutionPlan, trace: QueryTrace) -> List[RetrievalResult]:
        trace.record_start("plugin_execution")
        tasks = []
        for step in plan.steps:
            tasks.append(self._safe_execute_step(step, trace))
            
        results = await asyncio.gather(*tasks)
        
        # Flatten results list
        flat_results = []
        for res_list in results:
            flat_results.extend(res_list)
            
        trace.record_end("plugin_execution")
        return flat_results

    async def _safe_execute_step(self, step: ExecutionStep, trace: QueryTrace) -> List[RetrievalResult]:
        plugin_name = step.plugin_name.lower()
        cb = circuit_breakers.get(plugin_name)
        
        # Guard: Check circuit breaker state
        if cb and not cb.is_allowed():
            logger.warning(f"Circuit breaker '{plugin_name}' is OPEN. Bypassing execution.")
            trace.selected_databases.append(f"{plugin_name} (bypassed - circuit open)")
            return []

        plugin = capability_registry.get_plugin(plugin_name)
        if not plugin:
            logger.error(f"Plugin '{plugin_name}' not found in CapabilityRegistry.")
            return []

        # Bound concurrency using database semaphores
        sem = resources.get_db_semaphore(plugin_name)
        async with sem:
            start_time = time.time()
            try:
                # Execute with strict timeout limits
                timeout = resources.timeout_seconds
                results = await asyncio.wait_for(
                    plugin.search(step, trace),
                    timeout=timeout
                )
                
                # Record success to circuit breaker
                if cb:
                    cb.record_success()
                    
                trace.selected_databases.append(plugin_name)
                logger.info(f"Plugin '{plugin_name}' finished in {round((time.time() - start_time) * 1000, 2)}ms")
                return results
                
            except asyncio.TimeoutError:
                logger.error(f"Plugin '{plugin_name}' timed out after {timeout}s.")
                if cb:
                    cb.record_failure()
                trace.selected_databases.append(f"{plugin_name} (timeout)")
                return []
            except Exception as e:
                logger.error(f"Plugin '{plugin_name}' raised an error: {str(e)}")
                if cb:
                    cb.record_failure()
                trace.selected_databases.append(f"{plugin_name} (failed)")
                return []

# Export singleton supervisor instance
supervisor = ParallelSupervisor()
