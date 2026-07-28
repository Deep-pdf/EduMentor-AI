"""
EduMentor AI Agent Module
=========================

This module represents the primary AI Agent Orchestrator.
It coordinates tools using the ToolRegistry, acting as the central thinking engine
that makes routing decisions and builds execution plans.
"""

import streamlit as st
from typing import Any, Dict
from modules.logger import get_logger

logger = get_logger(__name__)


class AIAgent:
    """
    Core cognitive agent orchestrating all application modules via ToolRegistry.
    Acts as the main application controller, completely decoupled from concrete tool implementations.
    """

    def __init__(
        self, llm_client: Any, prompt_manager: Any, tool_registry: Any
    ) -> None:
        """
        Initialize the AI Agent with its dependencies.

        Args:
            llm_client (Any): Configured LLM runner.
            prompt_manager (Any): Prompt compiler module.
            tool_registry (Any): Decoupled ToolRegistry coordinator.
        """
        self.llm_client = llm_client
        self.prompt_manager = prompt_manager
        self.tool_registry = tool_registry
        logger.info("AIAgent initialized with ToolRegistry.")

    def initialize(self) -> None:
        """
        Bootstrap the agent's internal cognitive chains or states.
        """
        logger.info("Agent Initialized: Bootstrapping Agent orchestrator state.")
        # Tools are initialized during registration inside ToolRegistry

    def analyze_request(self, user_input: str) -> str:
        """
        Determine the path of action via rule-based intent classification.
        Does not use LLM prompts for routing to keep operations cheap.

        Args:
            user_input (str): Message from the user.

        Returns:
            str: Classified intent keyword.
        """
        user_input_lower = user_input.lower().strip()

        # 0. Force Web Search user override
        if st.session_state.get("force_web_search", False):
            intent = "Current Events"
            logger.info(
                "Agent Decision: Intent classified as '%s' (FORCED by user).", intent
            )
            return intent

        # 1. Greeting matching
        greetings = [
            "hello",
            "hi",
            "hey",
            "greetings",
            "good morning",
            "good afternoon",
            "good evening",
            "yo",
            "sup",
        ]
        if any(
            user_input_lower.startswith(g) or user_input_lower == g for g in greetings
        ):
            intent = "Greeting"
            logger.info("Agent Decision: Intent classified as '%s'.", intent)
            return intent

        # 2. Time Request matching
        time_keywords = [
            "what time is it",
            "current time",
            "what day is today",
            "what is today's date",
            "what is the date",
            "what day of the week",
        ]
        if any(tk in user_input_lower for tk in time_keywords) or user_input_lower in [
            "time",
            "date",
        ]:
            intent = "Time Request"
            logger.info("Agent Decision: Intent classified as '%s'.", intent)
            return intent

        # 3. Mathematics matching (digits and basic arithmetic symbols)
        math_symbols = [
            "+",
            "-",
            "*",
            "/",
            "%",
            "^",
            "sqrt",
            "pow",
            "sin",
            "cos",
            "tan",
            "log",
            "divided by",
            "times",
            "plus",
            "minus",
        ]
        has_math_symbol = (
            any(sym in user_input_lower for sym in math_symbols)
            or "x" in user_input_lower
            or "×" in user_input_lower
            or "÷" in user_input_lower
        )
        has_digits = any(char.isdigit() for char in user_input_lower)
        if has_math_symbol and has_digits:
            intent = "Mathematics"
            logger.info("Agent Decision: Intent classified as '%s'.", intent)
            return intent

        # 4. Current Events matching (Web Search - checked only if enabled)
        web_search_enabled = st.session_state.get("web_search_enabled", True)
        if web_search_enabled:
            search_keywords = [
                "latest news",
                "current events",
                "news about",
                "recent news",
                "what happened today",
                "weather in",
                "latest developments in",
            ]
            if (
                any(sk in user_input_lower for sk in search_keywords)
                or "latest" in user_input_lower
                or "recent" in user_input_lower
            ):
                intent = "Current Events"
                logger.info("Agent Decision: Intent classified as '%s'.", intent)
                return intent

        # 5. Follow-up matching (referencing conversation memory)
        follow_ups = [
            "summarize what we discussed",
            "summarize what you just explained",
            "what was my previous question",
            "continue",
            "explain that differently",
            "give another example",
            "elaborate",
            "tell me more",
            "why?",
            "how?",
            "can you explain",
            "go on",
            "explain that",
            "what did you say",
            "tell me why",
        ]
        if any(f in user_input_lower for f in follow_ups) or user_input_lower in [
            "why",
            "how",
            "continue",
        ]:
            intent = "Conversation Follow-up"
            logger.info("Agent Decision: Intent classified as '%s'.", intent)
            return intent

        # 6. Document Question matching (RAG)
        doc_loaded = st.session_state.get("current_document_path") is not None
        if doc_loaded and self.tool_registry.check_availability("RAG Tool"):
            doc_keywords = [
                "document",
                "pdf",
                "chapter",
                "page",
                "section",
                "syllabus",
                "textbook",
                "file",
                "uploaded",
                "paper",
                "author",
                "this book",
                "here",
                "the text",
                "summarize the document",
                "read the document",
            ]
            if any(k in user_input_lower for k in doc_keywords):
                intent = "Document Question"
                logger.info("Agent Decision: Intent classified as '%s'.", intent)
                return intent

        # 7. Default general question answering
        intent = "General Question"
        logger.info("Agent Decision: Intent classified as '%s'.", intent)
        return intent

    def build_execution_plan(self, intent: str) -> Dict[str, Any]:
        """
        Compile execution plan specifying steps and target tool dispatching.

        Args:
            intent (str): Intent tag.

        Returns:
            dict: Configured execution plan.
        """
        plan = {
            "intent": intent,
            "tool_to_use": None,
            "direct_tool_return": False,
            "steps": [],
        }

        if intent == "Greeting":
            plan["steps"] = ["call_llm"]
        elif intent == "Time Request":
            plan["tool_to_use"] = "Time Tool"
            plan["direct_tool_return"] = True
            plan["steps"] = ["execute_tool"]
        elif intent == "Mathematics":
            plan["tool_to_use"] = "Calculator Tool"
            plan["direct_tool_return"] = True
            plan["steps"] = ["execute_tool"]
        elif intent == "Current Events":
            plan["tool_to_use"] = "Search Tool"
            plan["steps"] = ["execute_tool", "call_llm"]
        elif intent == "Document Question":
            plan["tool_to_use"] = "RAG Tool"
            plan["steps"] = ["execute_tool", "call_llm"]
        elif intent == "Conversation Follow-up":
            plan["steps"] = ["call_llm"]
        else:
            plan["steps"] = ["call_llm"]

        logger.info(
            "Execution Plan Created: Plan for intent '%s': steps=%s, tool=%s",
            intent,
            plan["steps"],
            plan["tool_to_use"],
        )
        return plan

    def process_request(self, user_input: str) -> str:
        """
        Central orchestration sequence routing incoming user prompts via tool registry dispatching.

        Args:
            user_input (str): Message from the user.

        Returns:
            str: Final response to return to the UI.
        """
        logger.info("Execution Started: AIAgent processing request.")

        # 1. Update memory tool if registered
        memory_tool = self.tool_registry.get_tool("Memory Tool")
        if memory_tool:
            existing = memory_tool.execute({"action": "load"})
            if (
                not existing
                or existing[-1]["role"] != "user"
                or existing[-1]["content"] != user_input
            ):
                memory_tool.execute(
                    {"action": "add", "role": "user", "content": user_input}
                )

        # 2. Intent analysis
        intent = self.analyze_request(user_input)

        # Reset force_web_search to False if it was True
        if st.session_state.get("force_web_search", False):
            st.session_state.force_web_search = False

        # 3. Build plan
        plan = self.build_execution_plan(intent)

        tool_output = ""
        context_block = ""
        retrieved_docs = []
        system_instruction = ""
        user_msg = user_input
        response = ""

        # 4. Run plan steps
        for step in plan["steps"]:
            logger.info("AIAgent: Running execution step '%s'", step)

            if step == "execute_tool":
                tool_name = plan["tool_to_use"]
                tool = self.tool_registry.get_tool(tool_name)
                if tool:
                    params = {"query": user_input, "expression": user_input}
                    tool_output = tool.execute(params)

                    if tool_name == "RAG Tool":
                        context_block = tool_output.get("context", "")
                        retrieved_docs = tool_output.get("retrieved_docs", [])
                    elif tool_name == "Search Tool":
                        context_block = tool_output
                else:
                    logger.warning(
                        "AIAgent: Selected tool '%s' is not registered.", tool_name
                    )
                    tool_output = f"Error: Tool '{tool_name}' is not registered."

            elif step == "call_llm":
                recent_history = []
                if memory_tool:
                    recent_history = memory_tool.execute({"action": "load_recent"})[:-1]

                # Compile appropriate prompt payloads based on context resource used
                if plan["tool_to_use"] == "RAG Tool":
                    prompt_payload = self.prompt_manager.build_rag_prompt_with_history(
                        user_input, context_block, recent_history
                    )
                elif plan["tool_to_use"] == "Search Tool":
                    prompt_payload = (
                        self.prompt_manager.build_search_prompt_with_history(
                            user_input, context_block, recent_history
                        )
                    )
                else:
                    prompt_payload = (
                        self.prompt_manager.build_tutor_prompt_with_history(
                            user_input, recent_history
                        )
                    )

                system_instruction = prompt_payload["system"]
                user_msg = prompt_payload["user"]

                try:
                    response = self.llm_client.generate_response(
                        system_instruction=system_instruction, user_question=user_msg
                    )
                except Exception as e:
                    logger.error(
                        "AIAgent: LLM response generation failed: %s",
                        str(e),
                        exc_info=True,
                    )
                    response = "I encountered an error trying to formulate a response. Please try again."

        # 5. Compile final answer
        if plan["direct_tool_return"]:
            final_response = tool_output
        else:
            final_response = response
            # Append RAG citations if document matches found
            if plan["tool_to_use"] == "RAG Tool" and retrieved_docs:
                pages = sorted(
                    list(
                        set(
                            doc.metadata.get("page_number")
                            for doc in retrieved_docs
                            if doc.metadata.get("page_number") is not None
                        )
                    )
                )
                if pages:
                    citations = ", ".join(f"Page {p}" for p in pages)
                    final_response += f"\n\n**Sources:** {citations}"

        # 6. Save assistant response to memory tool
        if memory_tool:
            memory_tool.execute(
                {"action": "add", "role": "assistant", "content": final_response}
            )

        logger.info("Execution Finished: Request processing completed.")
        logger.info("Response Returned: Answer returned to interface.")
        return final_response

    def shutdown(self) -> None:
        """
        Teardown agent connections.
        """
        logger.info("Shutting down AIAgent resources...")
        self.llm_client = None
        self.tool_registry = None
        logger.info("AIAgent: Shutdown completed.")
