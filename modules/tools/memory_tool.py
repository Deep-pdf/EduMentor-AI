"""
EduMentor AI Memory Tool Adapter
================================

This module wraps the ConversationMemory module to expose it through
the standard BaseTool interface for the Agentic Tool Registry.
"""

from typing import Any, Dict, List
from modules.tools.base_tool import BaseTool
from modules.logger import get_logger

logger = get_logger(__name__)


class MemoryTool(BaseTool):
    """
    Memory Tool Adapter wrapping ConversationMemory.
    Provides session history management via a standardized capability.
    """

    def __init__(self, memory: Any) -> None:
        """
        Initialize the MemoryTool.

        Args:
            memory (Any): Instance of ConversationMemory.
        """
        self.memory = memory
        logger.info("MemoryTool created with ConversationMemory reference.")

    def initialize(self) -> None:
        """
        No complex initialization needed since the memory backend is persistent
        inside the Streamlit session state.
        """
        logger.info("MemoryTool initialized.")

    def name(self) -> str:
        """
        Return the unique name of this tool.
        """
        return "Memory Tool"

    def description(self) -> str:
        """
        Return description of MemoryTool.
        """
        return "Retrieves and manages conversation history and previous context turns."

    def capabilities(self) -> List[str]:
        """
        Return capabilities categories.
        """
        return ["Conversation Follow-up", "History Retrieval", "Clear History"]

    def execute(self, params: Dict[str, Any]) -> Any:
        """
        Perform conversational memory actions.

        Args:
            params (Dict[str, Any]): Dictionary containing:
                - 'action': 'load' (default) | 'load_recent' | 'add' | 'clear'
                - 'limit': int (optional for load_recent)
                - 'role': str ('user' or 'assistant' for add)
                - 'content': str (body of message for add)

        Returns:
            Any: Formatted history payloads or success status.
        """
        action = params.get("action", "load")
        logger.info("Tool Selected: Memory Tool chosen with action '%s'.", action)
        import time

        start_time = time.time()
        try:
            result = None
            if action == "load":
                result = self.memory.load()
            elif action == "load_recent":
                limit = params.get("limit", self.memory.limit)
                result = self.memory.load_recent(limit=limit)
            elif action == "add":
                role = params.get("role", "")
                content = params.get("content", "")
                self.memory.add(role, content)
                result = "Success"
            elif action == "clear":
                self.memory.clear()
                result = "Success"

            duration = time.time() - start_time
            logger.info("Tool Executed: Memory Tool successfully completed. Duration: %.2f seconds", duration)
            logger.info("Tool Returned Data: Memory operation returned successfully.")
            return result
        except Exception as e:
            logger.error("Tool Failed: Memory Tool execution failed: %s", str(e), exc_info=True)
            raise e

    def status(self) -> Dict[str, Any]:
        """
        Return status metrics.
        """
        return {
            "healthy": True,
            "session_id": self.memory.session_id,
            "limit": self.memory.limit,
            "state_key": self.memory.state_key,
        }

    def shutdown(self) -> None:
        """
        Clear memory references safely.
        """
        self.memory = None
        logger.info("MemoryTool shut down.")
