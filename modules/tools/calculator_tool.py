"""
EduMentor AI Calculator Tool Adapter
====================================

This module implements the CalculatorTool class, which performs deterministic
evaluations of mathematical expressions, avoiding LLM hallucinations.
"""

import math
import re
from typing import Any, Dict, List
from modules.tools.base_tool import BaseTool
from modules.logger import get_logger

logger = get_logger(__name__)


class CalculatorTool(BaseTool):
    """
    Deterministic Calculator Tool for performing basic arithmetic and mathematical functions.
    Ensures safe evaluation and prevents LLM calculations.
    """

    def initialize(self) -> None:
        """
        No startup initialization needed.
        """
        logger.info("CalculatorTool initialized.")

    def name(self) -> str:
        """
        Return the unique name of this tool.
        """
        return "Calculator Tool"

    def description(self) -> str:
        """
        Return description of CalculatorTool.
        """
        return "Performs deterministic mathematical equations, arithmetic, percentages, powers, and roots."

    def capabilities(self) -> List[str]:
        """
        Return capabilities categories.
        """
        return [
            "Mathematics",
            "Arithmetic",
            "Percentage Calculation",
            "Powers",
            "Roots",
        ]

    def supported_intents(self) -> List[str]:
        """
        Return the list of intents supported by this tool.
        """
        return ["Mathematics"]

    def execute(self, params: Dict[str, Any]) -> Any:
        """
        Evaluate arithmetic equations safely.

        Args:
            params (Dict[str, Any]): Dictionary containing:
                - 'expression': str (raw math expression)

        Returns:
            str: Result value or math error message.
        """
        expression = params.get("expression", params.get("query", "")).strip()
        if not expression:
            return "Empty mathematical expression."

        logger.info(
            "Tool Selected: Calculator Tool chosen for expression: %s", expression
        )
        import time

        start_time = time.time()

        try:
            # 1. Extract words and filter out non-math words before removing spaces
            allowed_funcs = {
                "sqrt",
                "pow",
                "sin",
                "cos",
                "tan",
                "log",
                "pi",
                "e",
                "abs",
            }
            words = re.findall(r"[a-zA-Z]+", expression)
            clean_expr = expression
            for word in words:
                if word.lower() not in allowed_funcs:
                    clean_expr = re.sub(
                        rf"\b{word}\b", "", clean_expr, flags=re.IGNORECASE
                    )

            # 2. Clean punctuation and spaces
            expr_clean = (
                clean_expr.replace(" ", "")
                .replace("x", "*")
                .replace("×", "*")
                .replace("÷", "/")
            )

            # 3. Filter allowed characters list to prevent malicious python eval injection
            allowed_chars = "0123456789+-*/().,%^ sqrtpowsincostanlogpabs"
            sanitized = "".join(c for c in expr_clean if c in allowed_chars)

            # Translate operator exponent symbol '^' to python exponentiation '**'
            sanitized = sanitized.replace("^", "**")

            # Setup math functions evaluation namespaces
            eval_env = {
                "sqrt": math.sqrt,
                "pow": math.pow,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "log": math.log,
                "pi": math.pi,
                "e": math.e,
                "abs": abs,
            }

            # Safe execution using empty builtins to block arbitrary method calling
            result = eval(sanitized, {"__builtins__": {}}, eval_env)
            duration = time.time() - start_time
            logger.info(
                "Tool Executed: Calculator successfully solved expression. Duration: %.2f seconds",
                duration,
            )
            logger.info(
                "Tool Returned Data: Mathematical result returned successfully."
            )
            return f"Result: {result}"

        except ZeroDivisionError:
            logger.error("Tool Failed: Division by zero occurred.")
            return "Error: Division by zero is undefined."
        except Exception as e:
            logger.error(
                "Tool Failed: Calculator evaluation error: %s", str(e), exc_info=True
            )
            return f"Error evaluating expression '{expression}': invalid math syntax."

    def status(self) -> Dict[str, Any]:
        """
        Return status metrics.
        """
        return {"healthy": True}

    def shutdown(self) -> None:
        """
        Clear references safely.
        """
        logger.info("CalculatorTool shut down.")
