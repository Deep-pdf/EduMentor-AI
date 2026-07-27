"""
EduMentor AI Tool Manager Module
================================

This module implements the ToolManager class for backward compatibility.
"""

from typing import Any, Dict, List
from modules.logger import get_logger

logger = get_logger(__name__)


class ToolManager:
    """
    Registry manager for configuring, loading, and calling tools for agents.
    Maintained for backward compatibility.
    """

    def __init__(self) -> None:
        self.tools: Dict[str, Any] = {}
        logger.info("ToolManager initialized (compatibility stub).")

    def register_tool(self, name: str, description: str, func: Any) -> None:
        """
        Register a tool.
        """
        logger.info("Registering compatibility tool: %s", name)

    def get_all_tools(self) -> List[Any]:
        """
        Get all tools.
        """
        return []

    def execute_tool(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """
        Execute a tool.
        """
        logger.info("Executing compatibility tool: %s", name)
        return None
