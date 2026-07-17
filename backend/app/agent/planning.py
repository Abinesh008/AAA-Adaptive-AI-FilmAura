import json
import re
from typing import Dict, Any, List
from app.api.deps import get_llm_provider
from app.agent.tools import agent_tool_registry
from app.agent.prompts import REACT_SYSTEM_PROMPT
from app.core.logging import get_logger

logger = get_logger("app.agent.planning")

class ReActPlanner:
    """
    Execution engine managing iterative Thought-Action-Observation loops for vague user requests.
    """
    def __init__(self, max_iterations: int = 5):
        self.max_iterations = max_iterations

    async def run_loop(self, query: str, user_profile: Dict[str, Any], chat_history: str, agent_trace: Any) -> Dict[str, Any]:
        logger.info(f"Starting ReAct reasoning loop for query: '{query}'")
        
        # Format tools description list
        tools = agent_tool_registry.get_schemas()
        tools_desc = "\n".join([f"- {t['name']}: {t['description']} Parameters: {t['parameters']}" for t in tools])
        
        # Build initial prompt
        prompt = REACT_SYSTEM_PROMPT.format(
            tools_description=tools_desc,
            query=query,
            user_profile=json.dumps(user_profile),
            chat_history=chat_history
        )
        
        steps_log: List[Dict[str, Any]] = []
        final_answer = None
        
        for iteration in range(1, self.max_iterations + 1):
            agent_trace.record_start(f"react_iteration_{iteration}")
            logger.info(f"ReAct Loop Iteration {iteration}/{self.max_iterations}")
            
            try:
                # Call LLM provider
                llm = get_llm_provider()
                response = await llm.generate_async(prompt)
                
                # Append response to prompt log so LLM recalls history
                prompt += f"\n{response}"
                
                # Parse action or final answer
                action_match = re.search(r"Action:\s*(\w+)", response)
                action_input_match = re.search(r"Action Input:\s*(\{.*?\})", response, re.DOTALL)
                final_answer_match = re.search(r"Final Answer:\s*(.*)", response, re.DOTALL)
                
                if final_answer_match:
                    final_answer = final_answer_match.group(1).strip()
                    logger.info("Found final answer in LLM response.")
                    agent_trace.record_end(f"react_iteration_{iteration}")
                    break
                    
                if action_match and action_input_match:
                    tool_name = action_match.group(1).strip()
                    tool_input_str = action_input_match.group(1).strip()
                    
                    try:
                        tool_params = json.loads(tool_input_str)
                    except json.JSONDecodeError:
                        tool_params = {"query": query}  # Fallback if LLM writes invalid JSON
                        
                    logger.info(f"Executing tool '{tool_name}' with parameters: {tool_params}")
                    tool = agent_tool_registry.get_tool(tool_name)
                    
                    if tool:
                        observation = await tool.execute(**tool_params)
                    else:
                        observation = {"error": f"Tool '{tool_name}' is not registered."}
                        
                    observation_str = json.dumps(observation)[:3000] # Cap observation output size
                    prompt += f"\nObservation: {observation_str}"
                    
                    steps_log.append({
                        "iteration": iteration,
                        "thought": response,
                        "tool": tool_name,
                        "input": tool_params,
                        "observation": observation
                    })
                else:
                    # Malformed/no matches - let's default to search_movies tool fallback
                    logger.warning("Malformed LLM ReAct response. Injecting default search tool helper.")
                    fallback_params = {"query": query}
                    tool = agent_tool_registry.get_tool("search_movies")
                    observation = await tool.execute(**fallback_params)
                    observation_str = json.dumps(observation)[:1000]
                    prompt += f"\nObservation: {observation_str}"
                    
            except Exception as e:
                logger.error(f"Error in ReAct iteration {iteration}: {str(e)}")
                # If LLM execution fails, break and default
                final_answer = f"I encountered an error while processing your request. Please try again."
                agent_trace.record_end(f"react_iteration_{iteration}")
                break
                
            agent_trace.record_end(f"react_iteration_{iteration}")
            
        if not final_answer:
            # Fallback direct formatting if iterations exceeded
            logger.warning("ReAct loop exceeded max iterations without returning final answer.")
            final_answer = "I searched across the catalog but couldn't finalize a recommendation. Please clarify your movie criteria."
            
        return {
            "answer": final_answer,
            "steps": steps_log
        }

# Export singleton planner instance
react_planner = ReActPlanner()
