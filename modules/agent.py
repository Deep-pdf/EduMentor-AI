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

        # 4. PDF Statistics matching
        pdf_stats_keywords = [
            "pdf statistics",
            "pdf stats",
            "page count",
            "word count",
            "reading time",
            "number of paragraphs",
            "number of headings",
            "top keywords",
            "document title",
            "metadata",
            "tell me about this pdf",
            "analyze pdf",
            "pdf info",
            "file size",
        ]
        if any(k in user_input_lower for k in pdf_stats_keywords):
            intent = "PDF Statistics"
            logger.info("Agent Decision: Intent classified as '%s'.", intent)
            return intent

        # 5. Study tool capabilities matching
        # Generate Quiz
        quiz_keywords = [
            "quiz",
            "mcq",
            "multiple choice",
            "practice questions",
            "practice question",
            "interview questions",
            "interview question",
            "practice test",
            "exam prep",
        ]
        if any(k in user_input_lower for k in quiz_keywords):
            intent = "Generate Quiz"
            logger.info("Agent Decision: Intent classified as '%s'.", intent)
            return intent

        # Generate Flashcards
        flashcard_keywords = ["flashcard", "flash card", "flashcards", "flash cards"]
        if any(k in user_input_lower for k in flashcard_keywords):
            intent = "Generate Flashcards"
            logger.info("Agent Decision: Intent classified as '%s'.", intent)
            return intent

        # Generate Revision Notes
        notes_keywords = [
            "revision notes",
            "study notes",
            "notes for",
            "notes of",
            "make notes",
        ]
        if any(k in user_input_lower for k in notes_keywords):
            intent = "Generate Revision Notes"
            logger.info("Agent Decision: Intent classified as '%s'.", intent)
            return intent

        # Summarize Document
        summary_keywords = [
            "summarize document",
            "summarize pdf",
            "summarize the document",
            "summarize chapter",
            "summary of the document",
            "document summary",
            "chapter summary",
            "eli5",
            "explain like i'm five",
        ]
        if any(k in user_input_lower for k in summary_keywords) or (
            user_input_lower == "summarize" or user_input_lower == "summary"
        ):
            intent = "Summarize Document"
            logger.info("Agent Decision: Intent classified as '%s'.", intent)
            return intent

        # 6. Latest News / Current Information (Web Search)
        web_search_enabled = st.session_state.get("web_search_enabled", True)
        if web_search_enabled:
            news_keywords = [
                "latest news",
                "news about",
                "recent news",
                "what happened today",
                "current events",
            ]
            if (
                any(k in user_input_lower for k in news_keywords)
                or "latest" in user_input_lower
                or "recent" in user_input_lower
            ):
                intent = "Latest News"
                logger.info("Agent Decision: Intent classified as '%s'.", intent)
                return intent

            info_keywords = [
                "weather in",
                "current price of",
                "recent developments in",
                "what is the current",
                "current status",
            ]
            if (
                any(k in user_input_lower for k in info_keywords)
                or "current" in user_input_lower
            ):
                intent = "Current Information"
                logger.info("Agent Decision: Intent classified as '%s'.", intent)
                return intent

        # 7. Follow-up matching (referencing conversation memory)
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

        # 8. Document Question matching (RAG)
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
                "read the document",
            ]
            if any(k in user_input_lower for k in doc_keywords):
                intent = "Document Question"
                logger.info("Agent Decision: Intent classified as '%s'.", intent)
                return intent

        # 9. Default general question answering
        intent = "General Question"
        logger.info("Agent Decision: Intent classified as '%s'.", intent)
        return intent

    def build_execution_plan(self, intent: str) -> Dict[str, Any]:
        """
        Compile execution plan specifying steps and target tools based on intent.

        Args:
            intent (str): Intent tag.

        Returns:
            dict: Configured execution plan.
        """
        plan = {
            "intent": intent,
            "tools_to_execute": [],
            "direct_tool_return": False,
            "steps": [],
        }

        # Handle direct tool returns first (backwards compatibility)
        if intent == "Time Request" and self.tool_registry.get_tool("Time Tool"):
            plan["tools_to_execute"] = ["Time Tool"]
            plan["direct_tool_return"] = True
            plan["steps"] = ["execute_tool"]
            return plan
        if intent == "Mathematics" and self.tool_registry.get_tool("Calculator Tool"):
            plan["tools_to_execute"] = ["Calculator Tool"]
            plan["direct_tool_return"] = True
            plan["steps"] = ["execute_tool"]
            return plan

        # Resolve primary tool by intent
        tool = self.tool_registry.resolve_tool_by_intent(intent)

        # Build execution sequence based on intent
        if intent == "Greeting":
            plan["steps"] = ["call_llm"]
        elif intent == "Conversation Follow-up":
            plan["steps"] = ["call_llm"]
        elif intent == "General Question":
            plan["steps"] = ["call_llm"]
        elif intent in [
            "Generate Quiz",
            "Generate Flashcards",
            "Generate Revision Notes",
        ]:
            plan["tools_to_execute"] = []
            if self.tool_registry.get_tool("Study Tool"):
                plan["tools_to_execute"].append("Study Tool")
            if self.tool_registry.get_tool("RAG Tool"):
                plan["tools_to_execute"].append("RAG Tool")
            plan["steps"] = ["execute_tools", "call_llm"]
        elif intent == "Summarize Document":
            plan["tools_to_execute"] = []
            if self.tool_registry.get_tool("RAG Tool"):
                plan["tools_to_execute"].append("RAG Tool")
            if self.tool_registry.get_tool("Study Tool"):
                plan["tools_to_execute"].append("Study Tool")
            plan["steps"] = ["execute_tools", "call_llm"]
        elif intent in ["Latest News", "Current Information"]:
            if tool:
                plan["tools_to_execute"] = [tool.name()]
            plan["steps"] = ["execute_tools", "call_llm"]
        elif intent == "PDF Statistics":
            if tool:
                plan["tools_to_execute"] = [tool.name()]
            plan["steps"] = ["execute_tools", "call_llm"]
        else:
            # Fallback to direct LLM call
            plan["steps"] = ["call_llm"]

        logger.info(
            "Execution Plan Created: Plan for intent '%s': steps=%s, tools=%s",
            intent,
            plan["steps"],
            plan["tools_to_execute"],
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
        study_output = None

        # 4. Run plan steps
        for step in plan["steps"]:
            logger.info("AIAgent: Running execution step '%s'", step)

            if step == "execute_tool":
                # Backwards compatibility execute single direct return tool
                tool_name = plan["tools_to_execute"][0]
                tool = self.tool_registry.get_tool(tool_name)
                if tool:
                    params = {"query": user_input, "expression": user_input}
                    tool_output = tool.execute(params)
                else:
                    logger.warning(
                        "AIAgent: Direct tool '%s' is not registered.", tool_name
                    )
                    tool_output = f"Error: Tool '{tool_name}' is not registered."

            elif step == "execute_tools":
                # Execute tools in the plan
                for tool_name in plan["tools_to_execute"]:
                    tool = self.tool_registry.get_tool(tool_name)
                    if not tool:
                        logger.warning(
                            "AIAgent: Configured tool '%s' is not registered.",
                            tool_name,
                        )
                        continue

                    # Execute and harvest results
                    if tool_name == "RAG Tool":
                        rag_res = tool.execute({"query": user_input})
                        context_block = rag_res.get("context", "")
                        retrieved_docs = rag_res.get("retrieved_docs", [])
                    elif tool_name == "Study Tool":
                        study_output = tool.execute(
                            {"query": user_input, "intent": intent}
                        )
                    elif tool_name == "Search Tool":
                        context_block = tool.execute({"query": user_input})
                    elif tool_name == "PDF Statistics Tool":
                        context_block = tool.execute({})

            elif step == "call_llm":
                recent_history = []
                if memory_tool:
                    recent_history = memory_tool.execute({"action": "load_recent"})[:-1]

                # Combine study instructions with user question if Study Tool was run
                if study_output:
                    user_msg = (
                        f"{user_input}\n\n"
                        f"--- STUDY TASK INSTRUCTIONS ---\n"
                        f"Task Type: {study_output.get('task_type')}\n"
                        f"Instructions: {study_output.get('prompt_instructions')}\n"
                        f"Expected Output Format:\n{study_output.get('expected_format')}\n"
                        f"-------------------------------"
                    )

                # Compile appropriate prompt payloads based on context resource used
                if "RAG Tool" in plan["tools_to_execute"] or intent in [
                    "Generate Quiz",
                    "Generate Flashcards",
                    "Generate Revision Notes",
                    "Summarize Document",
                    "Document Question",
                ]:
                    prompt_payload = self.prompt_manager.build_rag_prompt_with_history(
                        user_msg, context_block, recent_history
                    )
                elif "Search Tool" in plan["tools_to_execute"] or intent in [
                    "Latest News",
                    "Current Information",
                ]:
                    prompt_payload = (
                        self.prompt_manager.build_search_prompt_with_history(
                            user_msg, context_block, recent_history
                        )
                    )
                elif "PDF Statistics Tool" in plan["tools_to_execute"]:
                    # Format stats socratically using RAG prompt context wrapper
                    prompt_payload = self.prompt_manager.build_rag_prompt_with_history(
                        user_msg, context_block, recent_history
                    )
                else:
                    prompt_payload = (
                        self.prompt_manager.build_tutor_prompt_with_history(
                            user_msg, recent_history
                        )
                    )

                system_instruction = prompt_payload["system"]
                user_question_final = prompt_payload["user"]

                # Append Think Mode instructions if enabled in session state
                if st.session_state.get("think_mode_enabled", False):
                    system_instruction += (
                        "\n\nCRITICAL THINK MODE INSTRUCTION:\n"
                        "You MUST start your response with a detailed, step-by-step reasoning analysis enclosed inside "
                        "<thinking> ... </thinking> XML tags. Detail your understanding of the user's question, "
                        "the pedagogical goal, and how you will guide them Socrates-style. After the closing "
                        "</thinking> tag, write your final response to the student."
                    )

                try:
                    response = self.llm_client.generate_response(
                        system_instruction=system_instruction,
                        user_question=user_question_final,
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
            if "RAG Tool" in plan["tools_to_execute"] and retrieved_docs:
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
