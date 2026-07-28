"""
EduMentor AI Tool Factory Module
================================

This module implements the ToolFactory helper class for instantiating dynamic
cognitive tool adapters (Memory, RAG, Search, Calculator, and Time).
"""

from typing import Any
from modules.logger import get_logger
from modules.tools.search_tool import SearchTool
from modules.tools.calculator_tool import CalculatorTool
from modules.tools.time_tool import TimeTool
from modules.tools.rag_tool import RAGTool
from modules.tools.memory_tool import MemoryTool
from modules.tools.study_tool import StudyTool
from modules.tools.pdf_stats_tool import PDFStatisticsTool

logger = get_logger(__name__)


class ToolFactory:
    """
    Factory helper for instantiating dynamic cognitive tool adapters.
    Serves as an abstraction layer for constructing tool adapter singletons.
    """

    @staticmethod
    def create_search_tool() -> SearchTool:
        """
        Create and return a SearchTool instance.

        Returns:
            SearchTool: Instantiated SearchTool.
        """
        return SearchTool()

    @staticmethod
    def create_calculator_tool() -> CalculatorTool:
        """
        Create and return a CalculatorTool instance.

        Returns:
            CalculatorTool: Instantiated CalculatorTool.
        """
        return CalculatorTool()

    @staticmethod
    def create_time_tool() -> TimeTool:
        """
        Create and return a TimeTool instance.

        Returns:
            TimeTool: Instantiated TimeTool.
        """
        return TimeTool()

    @staticmethod
    def create_rag_tool(rag_engine: Any) -> RAGTool:
        """
        Create and return a RAGTool instance wrapping the RAGEngine.

        Args:
            rag_engine (Any): Concrete RAGEngine instance.

        Returns:
            RAGTool: Instantiated RAGTool wrapper.
        """
        return RAGTool(rag_engine)

    @staticmethod
    def create_memory_tool(memory: Any) -> MemoryTool:
        """
        Create and return a MemoryTool instance wrapping ConversationMemory.

        Args:
            memory (Any): Concrete ConversationMemory instance.

        Returns:
            MemoryTool: Instantiated MemoryTool wrapper.
        """
        return MemoryTool(memory)

    @staticmethod
    def create_study_tool() -> StudyTool:
        """
        Create and return a StudyTool instance.

        Returns:
            StudyTool: Instantiated StudyTool.
        """
        return StudyTool()

    @staticmethod
    def create_pdf_stats_tool() -> PDFStatisticsTool:
        """
        Create and return a PDFStatisticsTool instance.

        Returns:
            PDFStatisticsTool: Instantiated PDFStatisticsTool.
        """
        return PDFStatisticsTool()
