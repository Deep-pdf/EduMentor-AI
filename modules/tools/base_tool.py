"""
EduMentor AI Tool Base Class
============================

This module defines the abstract BaseTool class, which sets the unified interface
required for all dynamic cognitive tools in the EduMentor AI Agentic system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseTool(ABC):
    """
    Abstract Base Class for all dynamic cognitive tools.
    All registered tools must subclass this to enforce unified Agent execution.
    """

    @abstractmethod
    def initialize(self) -> None:
        """
        Set up connection objects, database clients, or external API drivers.
        """
        pass

    @abstractmethod
    def name(self) -> str:
        """
        Return the unique name descriptor of the tool.

        Returns:
            str: Unified tool name.
        """
        pass

    @abstractmethod
    def description(self) -> str:
        """
        Return the description explaining the tool's usage, helping the Agent select it.

        Returns:
            str: Detailed description.
        """
        pass

    @abstractmethod
    def capabilities(self) -> List[str]:
        """
        Return the semantic capabilities categories supported by the tool.

        Returns:
            List[str]: List of capability tags.
        """
        pass

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Any:
        """
        Perform the business logic associated with the tool action.

        Args:
            params (Dict[str, Any]): Dictionary of runtime parameters.

        Returns:
            Any: Execution result data.
        """
        pass

    @abstractmethod
    def status(self) -> Dict[str, Any]:
        """
        Return operational status, active configuration parameters, or health metrics.

        Returns:
            Dict[str, Any]: Tool operational status metrics.
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """
        Tear down connections, reset state, and free system resources safely.
        """
        pass
