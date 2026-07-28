"""
EduMentor AI Search Tool Adapter
================================

This module implements the SearchTool class, which queries the DuckDuckGo search
engine using the official duckduckgo-search library to fetch real-time public info.
"""

from typing import Any, Dict, List
from modules.tools.base_tool import BaseTool
from modules.logger import get_logger

logger = get_logger(__name__)


class SearchTool(BaseTool):
    """
    Search Tool wrapping the DuckDuckGo DDGS library.
    Fetches real-time web results to ground conversational queries.
    """

    def __init__(self, max_results: int = 4) -> None:
        """
        Initialize the SearchTool.

        Args:
            max_results (int): Number of top search results to retrieve.
        """
        self.max_results = max_results
        self.ddgs: Any = None
        logger.info("SearchTool created with max_results: %d", max_results)

    def initialize(self) -> None:
        """
        Initialize the DDGS API context.
        """
        from duckduckgo_search import DDGS

        self.ddgs = DDGS()
        logger.info("SearchTool initialized.")

    def name(self) -> str:
        """
        Return the unique name of this tool.
        """
        return "Search Tool"

    def description(self) -> str:
        """
        Return description of SearchTool.
        """
        return "Queries DuckDuckGo search engine to fetch real-time public information, news, and current events."

    def capabilities(self) -> List[str]:
        """
        Return capabilities categories.
        """
        return ["Current Events", "Latest News", "General Search", "Information Lookup"]

    def supported_intents(self) -> List[str]:
        """
        Return the list of intents supported by this tool.
        """
        return ["Latest News", "Current Information"]

    def execute(self, params: Dict[str, Any]) -> Any:
        """
        Query DuckDuckGo for the user prompt.

        Args:
            params (Dict[str, Any]): Dictionary containing:
                - 'query': str (search prompt)

        Returns:
            str: Formatted markdown string showing search results.
        """
        query = params.get("query", "")
        if not query:
            return "Empty search query."

        logger.info("Tool Selected: Search Tool chosen with query: %s", query[:50])
        import time

        start_time = time.time()
        try:
            from duckduckgo_search import DDGS

            with DDGS() as ddgs:
                results = [r for r in ddgs.text(query, max_results=self.max_results)]

            duration = time.time() - start_time
            logger.info(
                "Tool Executed: Search Tool successfully completed. Duration: %.2f seconds",
                duration,
            )

            if not results:
                logger.info("Tool Returned Data: No search results returned.")
                return f"No search results found for query: '{query}'."

            formatted_results = []
            for idx, r in enumerate(results):
                title = r.get("title", "No Title")
                href = r.get("href", "No Link")
                body = r.get("body", "No description available.")
                formatted_results.append(
                    f"[{idx + 1}] Title: {title}\nLink: {href}\nContent: {body}"
                )

            output = "\n\n---\n\n".join(formatted_results)
            logger.info(
                "Tool Returned Data: Formatted search text returned successfully."
            )
            return output

        except Exception as e:
            logger.error(
                "Tool Failed: Search Tool execution failed: %s", str(e), exc_info=True
            )
            return f"Web search failed due to: {str(e)}"

    def status(self) -> Dict[str, Any]:
        """
        Return status metrics.
        """
        return {"healthy": True, "max_results": self.max_results}

    def shutdown(self) -> None:
        """
        Clear references safely.
        """
        self.ddgs = None
        logger.info("SearchTool shut down.")
