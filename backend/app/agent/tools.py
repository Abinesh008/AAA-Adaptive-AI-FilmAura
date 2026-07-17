from typing import Dict, Any, List, Callable, Optional
from app.retrieval.sdk import retrieval_client
from app.core.logging import get_logger

logger = get_logger("app.agent.tools")

class AgentTool:
    def __init__(self, name: str, description: str, parameters: Dict[str, Any], func: Callable):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.func = func

    async def execute(self, **kwargs) -> Any:
        try:
            if asyncio.iscoroutinefunction(self.func):
                return await self.func(**kwargs)
            return self.func(**kwargs)
        except Exception as e:
            logger.error(f"Failed to execute tool '{self.name}': {str(e)}")
            return {"error": str(e)}

import asyncio

class AgentToolRegistry:
    """
    Registry for tools available to the ReAct planning and reasoning agent.
    """
    def __init__(self):
        self._tools: Dict[str, AgentTool] = {}
        self._register_default_tools()

    def register(self, name: str, description: str, parameters: Dict[str, Any], func: Callable):
        self._tools[name] = AgentTool(name, description, parameters, func)
        logger.info(f"Registered agent tool: {name}")

    def get_tool(self, name: str) -> Optional[AgentTool]:
        return self._tools.get(name)

    def get_all_tools(self) -> List[AgentTool]:
        return list(self._tools.values())

    def get_schemas(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in self._tools.values()
        ]

    def _register_default_tools(self):
        # 1. Search tool
        self.register(
            name="search_movies",
            description="Search for movies matching a vague, conceptual, thematic, or keyword description. Returns lists of matching candidates.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query, e.g. 'spinning top totem dream collapse'"},
                    "profile": {"type": "string", "enum": ["fast", "balanced", "quality"], "default": "balanced"}
                },
                "required": ["query"]
            },
            func=self._wrap_search
        )
        
        # 2. Recommend tool
        self.register(
            name="recommend_movies",
            description="Recommend movies matching a query where the user asks for recommendations similar to other films.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The recommendation query, e.g. 'movies similar to Interstellar'"},
                    "profile": {"type": "string", "enum": ["fast", "balanced", "quality"], "default": "balanced"}
                },
                "required": ["query"]
            },
            func=self._wrap_recommend
        )

        # 3. Identify tool
        self.register(
            name="identify_movie",
            description="Identify a specific movie based on vague descriptions or plot elements.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": " Vague plot description, e.g. 'movie where a guy gets memory loss and tattoos clues on his body'"},
                    "profile": {"type": "string", "enum": ["fast", "balanced", "quality"], "default": "balanced"}
                },
                "required": ["query"]
            },
            func=self._wrap_identify
        )

        # 4. Explain tool
        self.register(
            name="explain_movie_retrieval",
            description="Get structured provenance and details explanation tree for a executed trace ID.",
            parameters={
                "type": "object",
                "properties": {
                    "trace_id": {"type": "string", "description": "The UUID trace ID of the query execution."}
                },
                "required": ["trace_id"]
            },
            func=self._wrap_explain
        )

        # 5. User preferences tool
        self.register(
            name="get_user_preferences",
            description="Retrieve configured user taste profiles, including favorite directors, actors, genres, and excluded content constraints.",
            parameters={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "The unique user identifier."}
                },
                "required": ["user_id"]
            },
            func=self._wrap_preferences
        )

    # Wrappers translating Pydantic models to clean dict responses
    async def _wrap_search(self, query: str, profile: str = "balanced") -> Dict[str, Any]:
        res = await retrieval_client.search(query=query, profile=profile)
        return res.dict()

    async def _wrap_recommend(self, query: str, profile: str = "balanced") -> Dict[str, Any]:
        res = await retrieval_client.recommend(query=query, profile=profile)
        return res.dict()

    async def _wrap_identify(self, query: str, profile: str = "balanced") -> Dict[str, Any]:
        res = await retrieval_client.identify(query=query, profile=profile)
        return res.dict()

    def _wrap_explain(self, trace_id: str) -> Dict[str, Any]:
        return retrieval_client.explain(trace_id=trace_id)

    async def _wrap_preferences(self, user_id: str) -> Dict[str, Any]:
        # Return mock preferences indicating the framework contract
        logger.info(f"Retrieving user profile context for: {user_id}")
        return {
            "user_id": user_id,
            "favorite_genres": ["Sci-Fi", "Thriller"],
            "favorite_directors": ["Christopher Nolan", "Denis Villeneuve"],
            "disliked_genres": ["Horror"],
            "preferred_era": "2000s and later"
        }

# Export singleton tool registry
agent_tool_registry = AgentToolRegistry()
