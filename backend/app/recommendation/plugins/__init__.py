from typing import Dict, List, Optional
from app.recommendation.interfaces.plugin import BaseRecommendationPlugin
from app.recommendation.plugins.collaborative import collaborative_plugin
from app.recommendation.plugins.graph_walk import graph_walk_plugin
from app.core.logging import get_logger

logger = get_logger("app.recommendation.plugins.registry")

class RecommendationPluginRegistry:
    """
    Registry coordinator holding initialized recommendation candidate generator plugins.
    """
    def __init__(self):
        self._plugins: Dict[str, BaseRecommendationPlugin] = {}
        
        # Self-register default plugins
        self.register(collaborative_plugin)
        self.register(graph_walk_plugin)

    def register(self, plugin: BaseRecommendationPlugin) -> None:
        logger.info(f"Registering recommendation plugin: {plugin.name}")
        self._plugins[plugin.name] = plugin

    def get_plugin(self, name: str) -> Optional[BaseRecommendationPlugin]:
        return self._plugins.get(name)

    def list_plugins(self) -> List[BaseRecommendationPlugin]:
        return list(self._plugins.values())

# Export registry singleton
plugin_registry = RecommendationPluginRegistry()
