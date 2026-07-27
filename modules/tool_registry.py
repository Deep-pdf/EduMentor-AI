"""
EduMentor AI Tool Registry Module
==================================

This module implements the ToolRegistry, which acts as the single source of
truth for registering, listing, and retrieving tools for the AI Agent.
"""

from typing import Dict, List, Optional
from modules.logger import get_logger
from modules.tools.base_tool import BaseTool

logger = get_logger(__name__)


class ToolRegistry:
    """
    Decoupled single source of truth for registering, listing, and retrieving tools.
    Decouples the Agent from direct instantiation of component classes.
    """

    def __init__(self) -> None:
        """
        Initialize the ToolRegistry instance.
        """
        self._tools: Dict[str, BaseTool] = {}
        logger.info("Registry Initialized: Tool registry created.")

    def register(self, tool: BaseTool) -> None:
        """
        Register a new tool instance in the registry collection and initialize it.

        Args:
            tool (BaseTool): Instance of tool to register.

        Raises:
            RuntimeError: If initialization of the tool fails.
        """
        tool_name = tool.name()
        try:
            tool.initialize()
            self._tools[tool_name] = tool
            logger.info("Tool Registered: Successfully loaded and registered '%s'.", tool_name)
        except Exception as e:
            logger.error(
                "Tool Failed: Registration initialization failed for '%s': %s",
                tool_name,
                str(e),
                exc_info=True
            )
            raise RuntimeError(f"tool_init_failed_{tool_name}")

    def remove(self, name: str) -> None:
        """
        Remove a tool from the registry and call its shutdown method.

        Args:
            name (str): Unique name of the tool to remove.
        """
        if name in self._tools:
            try:
                self._tools[name].shutdown()
                logger.info("Tool Registry: Removed tool '%s'.", name)
            except Exception as e:
                logger.error("Tool Registry: Shutdown failed for '%s' during removal: %s", name, str(e))
            del self._tools[name]

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """
        Retrieve a registered tool instance by name.

        Args:
            name (str): Unique name of the tool to retrieve.

        Returns:
            Optional[BaseTool]: Tool instance if found, else None.
        """
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        """
        List all registered tool names.

        Returns:
            List[str]: List of active tool names.
        """
        return list(self._tools.keys())

    def discover_capabilities(self) -> Dict[str, List[str]]:
        """
        List capabilities mapping for all active tools.

        Returns:
            Dict[str, List[str]]: Tool-to-capabilities mapping.
        """
        return {name: tool.capabilities() for name, tool in self._tools.items()}

    def check_availability(self, name: str) -> bool:
        """
        Verify if a specific tool is registered and operational.

        Args:
            name (str): Tool name to check.

        Returns:
            bool: True if tool is available and healthy, False otherwise.
        """
        tool = self.get_tool(name)
        if not tool:
            return False
        try:
            status = tool.status()
            return status.get("healthy", False)
        except Exception:
            return False
