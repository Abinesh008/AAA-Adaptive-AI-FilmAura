from typing import Callable, List, Dict, Any, Awaitable
from app.core.logging import get_logger

logger = get_logger("app.retrieval.hooks")

HookFunc = Callable[..., Awaitable[None]]

class RetrievalHookManager:
    """
    Registry for pre/post execution lifecycle hooks across all retrieval operations.
    """
    def __init__(self):
        self._hooks: Dict[str, List[HookFunc]] = {
            "before_normalization": [],
            "after_normalization": [],
            "before_planning": [],
            "after_planning": [],
            "before_execution": [],
            "after_execution": [],
            "before_fusion": [],
            "after_fusion": [],
            "before_reranking": [],
            "after_reranking": [],
            "before_reasoning": [],
            "after_reasoning": [],
            "before_response": [],
            "after_response": []
        }

    def register(self, hook_name: str, callback: HookFunc) -> None:
        name = hook_name.lower()
        if name in self._hooks:
            self._hooks[name].append(callback)
            logger.info(f"Registered hook callback for: {name}")
        else:
            logger.warning(f"Attempted to register invalid hook: {hook_name}")

    async def trigger(self, hook_name: str, *args: Any, **kwargs: Any) -> None:
        name = hook_name.lower()
        callbacks = self._hooks.get(name, [])
        for cb in callbacks:
            try:
                await cb(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error executing hook callback {cb.__name__} for {name}: {str(e)}")

# Singleton hook registry
hooks = RetrievalHookManager()
