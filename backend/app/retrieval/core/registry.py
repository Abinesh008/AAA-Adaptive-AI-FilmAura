import pkgutil
import importlib
from typing import Dict, Any, List, Type
from app.core.logging import get_logger
from app.retrieval.interfaces.plugin import BaseRetrievalPlugin

logger = get_logger("app.retrieval.registry")

class PipelineRegistry:
    """
    Registry managing ordered execution stages for the retrieval pipeline.
    """
    def __init__(self):
        self._stages: List[str] = [
            "normalization",
            "expansion",
            "planning",
            "execution",
            "fusion",
            "reranking",
            "context",
            "reasoning"
        ]

    def get_stages(self) -> List[str]:
        return self._stages.copy()

    def register_stage(self, stage_name: str, after_stage: Optional[str] = None) -> None:
        """
        Dynamically insert a new pipeline execution stage.
        """
        name = stage_name.lower()
        if name in self._stages:
            logger.warning(f"Stage '{name}' is already registered.")
            return
            
        if after_stage and after_stage.lower() in self._stages:
            idx = self._stages.index(after_stage.lower())
            self._stages.insert(idx + 1, name)
        else:
            self._stages.append(name)
        logger.info(f"Registered pipeline stage: {name}")

class CapabilityRegistry:
    """
    Registry mapping plugins to their advertised query capabilities.
    """
    def __init__(self):
        self._plugins: Dict[str, BaseRetrievalPlugin] = {}
        self._capabilities: Dict[str, Dict[str, bool]] = {}

    def register_plugin(self, name: str, plugin: BaseRetrievalPlugin, caps: Dict[str, bool]) -> None:
        key = name.lower()
        self._plugins[key] = plugin
        self._capabilities[key] = caps
        logger.info(f"Registered plugin: {key} with capabilities: {caps}")

    def get_plugin(self, name: str) -> Optional[BaseRetrievalPlugin]:
        return self._plugins.get(name.lower())

    def get_plugins_supporting(self, capability: str) -> List[str]:
        """
        Query plugins supporting a specific capability (e.g. supports_graph).
        """
        matches = []
        for name, caps in self._capabilities.items():
            if caps.get(capability.lower(), False):
                matches.append(name)
        return matches

    def get_all_manifests(self) -> Dict[str, Any]:
        manifests = {}
        for name, plugin in self._plugins.items():
            manifests[name] = {
                "name": name,
                "version": getattr(plugin, "version", "1.0.0"),
                "capabilities": self._capabilities.get(name, {}),
                "dependencies": getattr(plugin, "dependencies", []),
                "health_status": "healthy"
            }
        return manifests

from typing import Optional
pipeline_registry = PipelineRegistry()
capability_registry = CapabilityRegistry()

def discover_plugins() -> None:
    """
    Dynamically discovers and registers all retrieval plugins located inside app/retrieval/plugins.
    """
    try:
        package = importlib.import_module("app.retrieval.plugins")
        for _, module_name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            mod = importlib.import_module(module_name)
            for attr in dir(mod):
                obj = getattr(mod, attr)
                if isinstance(obj, type) and issubclass(obj, BaseRetrievalPlugin) and obj != BaseRetrievalPlugin:
                    # Instantiate and register
                    plugin_instance = obj()
                    name = getattr(plugin_instance, "name", obj.__name__.lower())
                    caps = getattr(plugin_instance, "capabilities", {})
                    capability_registry.register_plugin(name, plugin_instance, caps)
    except Exception as e:
        logger.error(f"Plugin auto-discovery failed: {str(e)}")
