"""
EduMentor AI Time Tool Adapter
==============================

This module implements the TimeTool class, which fetches current date,
time, day of week, and timezone information deterministically.
"""

import datetime
from typing import Any, Dict, List
from modules.tools.base_tool import BaseTool
from modules.logger import get_logger

logger = get_logger(__name__)


class TimeTool(BaseTool):
    """
    Time Tool for retrieving current date, time, timezone, and day of week.
    Bypasses the LLM to deliver fast, real-time results.
    """

    def initialize(self) -> None:
        """
        No complex initialization needed.
        """
        logger.info("TimeTool initialized.")

    def name(self) -> str:
        """
        Return the unique name of this tool.
        """
        return "Time Tool"

    def description(self) -> str:
        """
        Return description of TimeTool.
        """
        return (
            "Retrieves current date, time, timezone, and day of week deterministically."
        )

    def capabilities(self) -> List[str]:
        """
        Return capabilities categories.
        """
        return ["Time Request", "Current Date", "Current Time", "Day of Week"]

    def supported_intents(self) -> List[str]:
        """
        Return the list of intents supported by this tool.
        """
        return ["Time Request"]

    def execute(self, params: Dict[str, Any]) -> Any:
        """
        Fetch and format the current datetime string.

        Args:
            params (Dict[str, Any]): No parameters required.

        Returns:
            str: Formatted datetime details.
        """
        logger.info("Tool Selected: Time Tool chosen for execution.")
        import time

        start_time = time.time()

        try:
            now = datetime.datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")
            day_str = now.strftime("%A")
            timezone_offset = now.astimezone().tzname() or "Local Time"

            result = (
                f"Current Date: {date_str}\n"
                f"Current Time: {time_str} ({timezone_offset})\n"
                f"Day of Week: {day_str}"
            )
            duration = time.time() - start_time
            logger.info(
                "Tool Executed: Time Tool completed execution. Duration: %.2f seconds",
                duration,
            )
            logger.info("Tool Returned Data: Deterministic timestamp returned.")
            return result
        except Exception as e:
            logger.error("Tool Failed: Time Tool failed: %s", str(e), exc_info=True)
            return "Failed to fetch current time."

    def status(self) -> Dict[str, Any]:
        """
        Return status metrics.
        """
        return {"healthy": True}

    def shutdown(self) -> None:
        """
        No complex teardown needed.
        """
        logger.info("TimeTool shut down.")
