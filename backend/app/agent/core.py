import uuid
import json
import re
from typing import Dict, Any, Optional
import time
from app.core.metrics import AGENT_LATENCY
from app.api.deps import get_llm_provider
from app.agent.prompts import ROUTER_SYSTEM_PROMPT
from app.agent.memory import conversation_memory
from app.agent.planning import react_planner
from app.retrieval.query_trace import QueryTrace
from app.retrieval.guardrails import guardrail_engine
from app.retrieval.session_store import session_store
from app.core.logging import get_logger

logger = get_logger("app.agent.core")

class AgentCoordinator:
    """
    Coordinator routing user conversations to custom greetings, clarifications, or retrieval plans.
    """
    async def chat(self, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        start_agent_time = time.time()
        s_id = session_id or str(uuid.uuid4())
        logger.info(f"Received agent chat request. Session ID: {s_id}")
        
        # Initialize Trace observability
        trace = QueryTrace(session_id=s_id)
        trace.record_start("agent_total")
        
        # Guardrails check
        is_safe, guard_err = guardrail_engine.validate_query(query, trace)
        if not is_safe:
            answer_text = f"Request rejected due to security policy: {guard_err}"
            conversation_memory.add_message(s_id, "user", query)
            conversation_memory.add_message(s_id, "assistant", answer_text)
            trace.record_end("agent_total")
            session_store.save_session(trace)
            AGENT_LATENCY.observe(time.time() - start_agent_time)
            return {
                "answer": answer_text,
                "session_id": s_id,
                "trace_id": trace.trace_id,
                "intent": "rejected",
                "steps": [],
                "history_length": len(conversation_memory.get_history(s_id))
            }
            
        # Add user message to session history
        conversation_memory.add_message(s_id, "user", query)
        
        # 1. Classify intent via router prompt
        intent_type = "retrieval"
        try:
            llm = get_llm_provider()
            route_prompt = ROUTER_SYSTEM_PROMPT
            # Feed current message context
            route_prompt += f"\nQuery: '{query}'\nJSON Response:"
            
            raw_route = await llm.generate_async(route_prompt)
            json_match = re.search(r"(\{.*?\})", raw_route, re.DOTALL)
            if json_match:
                route_data = json.loads(json_match.group(1))
                intent_type = route_data.get("intent", "retrieval")
                logger.info(f"Router classified intent as '{intent_type}' with confidence {route_data.get('confidence')}")
        except Exception as e:
            logger.error(f"Router intent classification failed: {str(e)}. Defaulting to retrieval route.")
            
        trace.planner_decisions["agent_intent"] = intent_type
        
        # 2. Execute target route
        answer_text = ""
        steps_taken = []
        
        if intent_type == "greet":
            trace.record_start("agent_greet")
            # Generate conversational response directly using LLM
            history_str = conversation_memory.get_history_as_string(s_id)
            greet_prompt = f"You are FilmAura's conversational agent. Speak naturally, be helpful and keep the conversation friendly. Do not call retrieval tools.\nChat History:\n{history_str}\nAssistant:"
            answer_text = await get_llm_provider().generate_async(greet_prompt)
            trace.record_end("agent_greet")
            
        elif intent_type == "clarify":
            trace.record_start("agent_clarify")
            # Clear details or parse specific selection candidates
            # Fallback to planner executing clarify options
            profile = conversation_memory.get_user_profile(s_id)
            history_str = conversation_memory.get_history_as_string(s_id)
            plan_res = await react_planner.run_loop(query, profile, history_str, trace)
            answer_text = plan_res["answer"]
            steps_taken = plan_res["steps"]
            trace.record_end("agent_clarify")
            
        else:  # retrieval
            # Asynchronously update profile based on user preferences in query
            await conversation_memory.update_taste_profile(s_id, query)
            
            trace.record_start("agent_retrieval_plan")
            profile = conversation_memory.get_user_profile(s_id)
            history_str = conversation_memory.get_history_as_string(s_id)
            plan_res = await react_planner.run_loop(query, profile, history_str, trace)
            answer_text = plan_res["answer"]
            steps_taken = plan_res["steps"]
            trace.record_end("agent_retrieval_plan")

        # Save assistant message to session history
        conversation_memory.add_message(s_id, "assistant", answer_text)
        
        trace.record_end("agent_total")
        # Save trace to session store
        session_store.save_session(trace)
        
        AGENT_LATENCY.observe(time.time() - start_agent_time)
        return {
            "answer": answer_text,
            "session_id": s_id,
            "trace_id": trace.trace_id,
            "intent": intent_type,
            "steps": steps_taken,
            "history_length": len(conversation_memory.get_history(s_id))
        }

# Export coordinator singleton instance
agent_coordinator = AgentCoordinator()
