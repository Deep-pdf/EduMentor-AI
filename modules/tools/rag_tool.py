"""
EduMentor AI RAG Tool Adapter
==============================

This module wraps the RAGEngine module to expose it through
the standard BaseTool interface for the Agentic Tool Registry.
"""

from typing import Any, Dict, List
from modules.tools.base_tool import BaseTool
from modules.logger import get_logger

logger = get_logger(__name__)


class RAGTool(BaseTool):
    """
    RAG Tool Adapter wrapping RAGEngine.
    Enables semantic document lookup via the Tool Registry interface.
    """

    def __init__(self, rag_engine: Any) -> None:
        """
        Initialize the RAGTool.

        Args:
            rag_engine (Any): Instance of RAGEngine.
        """
        self.rag_engine = rag_engine
        logger.info("RAGTool created with RAGEngine reference.")

    def initialize(self) -> None:
        """
        Ensure RAG engine persistent collection is ready.
        """
        logger.info("RAGTool initialized.")

    def name(self) -> str:
        """
        Return the unique name of this tool.
        """
        return "RAG Tool"

    def description(self) -> str:
        """
        Return description of RAGTool.
        """
        return "Retrieves matching context chunks from uploaded PDF learning materials to ground questions."

    def capabilities(self) -> List[str]:
        """
        Return capabilities categories.
        """
        return ["Document Question", "Syllabus Retrieval", "Academic Context Lookup"]

    def supported_intents(self) -> List[str]:
        """
        Return the list of intents supported by this tool.
        """
        return [
            "Document Question",
            "Generate Quiz",
            "Generate Flashcards",
            "Generate Revision Notes",
            "Summarize Document",
        ]

    def execute(self, params: Dict[str, Any]) -> Any:
        """
        Query RAGEngine for semantic context block.

        Args:
            params (Dict[str, Any]): Dictionary containing:
                - 'query': str (user search query)

        Returns:
            Dict[str, Any]: Dictionary containing:
                - 'context': str (concatenated context string)
                - 'retrieved_docs': List[Document] (source chunks)
        """
        query = params.get("query", "")
        logger.info("Tool Selected: RAG Tool chosen for execution.")
        import time

        start_time = time.time()
        try:
            context, docs = self.rag_engine.generate_context(query)
            duration = time.time() - start_time
            logger.info(
                "Tool Executed: RAG Tool successfully executed. Duration: %.2f seconds",
                duration,
            )
            logger.info("Tool Returned Data: Context block returned successfully.")
            return {"context": context, "retrieved_docs": docs}
        except Exception as e:
            logger.error(
                "Tool Failed: RAG Tool execution failed: %s", str(e), exc_info=True
            )
            raise e

    def status(self) -> Dict[str, Any]:
        """
        Return RAGEngine health status.
        """
        raw_status = self.rag_engine.status()
        raw_status["healthy"] = raw_status.get("database_initialized", False)
        return raw_status

    def shutdown(self) -> None:
        """
        Clear references safely.
        """
        self.rag_engine = None
        logger.info("RAGTool shut down.")
