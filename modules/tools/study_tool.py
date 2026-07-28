"""
EduMentor AI Study Tool
=======================

This module implements the StudyTool class which prepares structured educational instructions
(MCQs, revision notes, summaries, etc.) to enhance Socratic learning without invoking the LLM directly.
"""

from typing import Any, Dict, List
from modules.tools.base_tool import BaseTool
from modules.logger import get_logger

logger = get_logger(__name__)


class StudyTool(BaseTool):
    """
    Cognitive study assistant tool. Prepares task-specific prompt structures
    and templates to guide the tutor during content generation.
    """

    def __init__(self) -> None:
        """
        Initialize the StudyTool.
        """
        logger.info("StudyTool created.")

    def initialize(self) -> None:
        """
        Initialize study tool states.
        """
        logger.info("StudyTool initialized.")

    def name(self) -> str:
        """
        Return the unique name of this tool.
        """
        return "Study Tool"

    def description(self) -> str:
        """
        Return description explaining the tool's study capabilities.
        """
        return (
            "Generates structured prompt instructions and format structures for educational tasks "
            "like quizzes, flashcards, revision notes, chapter summaries, and conceptual breakdowns."
        )

    def capabilities(self) -> List[str]:
        """
        Return list of capabilities tags.
        """
        return ["Study Assistant", "Material Synthesis", "Concept Simplification"]

    def supported_intents(self) -> List[str]:
        """
        Return list of intents supported by this tool.
        """
        return [
            "Generate Quiz",
            "Generate Flashcards",
            "Generate Revision Notes",
            "Summarize Document",
        ]

    def execute(self, params: Dict[str, Any]) -> Any:
        """
        Determine study instructions and format templates based on query keywords or intent.

        Args:
            params (Dict[str, Any]): Parameters containing user query/intent context.

        Returns:
            Dict[str, str]: Structured study instructions containing:
                - 'task_type': str
                - 'prompt_instructions': str
                - 'expected_format': str
        """
        query = params.get("query", "").lower()
        intent = params.get("intent", "")

        logger.info(
            "Tool Selected: Study Tool chosen with intent '%s' and query: %s",
            intent,
            query[:50],
        )

        # Default fallback instructions
        task_type = "Study Guide"
        instructions = (
            "Provide a structured, step-by-step Socratic tutorial on the topic."
        )
        fmt = "Socratic dialogue format with encouraging questions."

        # Match capabilities based on intent or query keywords
        if (
            intent == "Generate Quiz"
            or "quiz" in query
            or "mcq" in query
            or "practice questions" in query
            or "questions" in query
        ):
            task_type = "Generate Practice Questions"
            if "mcq" in query or "multiple choice" in query:
                task_type = "Generate MCQs"
                instructions = (
                    "Create a set of multiple-choice questions (MCQs) covering the provided material. "
                    "For each question, provide 4 options (A, B, C, D) and detail the correct "
                    "answer with an explanation."
                )
                fmt = (
                    "### MCQ Set\n"
                    "1. [Question Text]\n"
                    "   A) [Option A]\n"
                    "   B) [Option B]\n"
                    "   C) [Option C]\n"
                    "   D) [Option D]\n"
                    "   **Correct Option:** [Letter]\n"
                    "   **Explanation:** [Brief reason why the option is correct]"
                )
            elif "interview" in query:
                task_type = "Generate Interview Questions"
                instructions = (
                    "Formulate challenging, conceptual interview questions targeting key principles in the text, "
                    "along with comprehensive, exemplary answers to help the user prepare."
                )
                fmt = (
                    "### Interview Prep\n**Question:** [Text]\n**Ideal Answer:** [Text]"
                )
            else:
                instructions = (
                    "Formulate deep, application-based conceptual practice questions designed to test the user's "
                    "understanding, along with guided solution pathways."
                )
                fmt = (
                    "### Concept Check\n**Problem:** [Text]\n**Socratic Hint:** [Hint]"
                )

        elif (
            intent == "Generate Flashcards"
            or "flashcard" in query
            or "flash card" in query
        ):
            task_type = "Generate Flashcards"
            instructions = (
                "Develop high-yield, active-recall flashcards from the text. Each flashcard should have a clear, "
                "focused front (question, definition, or concept) and a corresponding back (concise answer/details)."
            )
            fmt = "### Flashcards\n**Front:** [Concept/Question]\n**Back:** [Definition/Explanation]\n---"

        elif (
            intent == "Generate Revision Notes"
            or "notes" in query
            or "revision" in query
        ):
            task_type = "Generate Revision Notes"
            instructions = (
                "Compile highly structured, concise revision notes. Highlight core concepts, definitions, "
                "key takeaways, and bullet points to allow rapid review."
            )
            fmt = (
                "### Revision Summary\n"
                "- **[Core Concept Name]:** [Definition and context]\n"
                "  - [Key Detail]\n"
                "  - [Key Takeaway]"
            )

        elif (
            intent == "Summarize Document" or "summarize" in query or "summary" in query
        ):
            task_type = "Summarize Chapter"
            if "explain like I'm five" in query or "eli5" in query or "simple" in query:
                task_type = "Explain Like I'm Five"
                instructions = (
                    "Deconstruct the complex concepts in the provided text and explain them using simple terms, "
                    "intuitive metaphors, and analogies suitable for a five-year-old child."
                )
                fmt = "### Explain Like I'm Five\n**Analogy:** [Intuitive scenario]\n**Simple Terms:** [Explanation]"
            else:
                instructions = (
                    "Provide a comprehensive, high-level summary of the chapter/document contents, "
                    "capturing primary objectives, subtopics, and overall conclusions."
                )
                fmt = (
                    "### Executive Summary\n"
                    "- **Overview:** [Brief description]\n"
                    "- **Key Pillars:** [Key topics list]\n"
                    "- **Conclusion:** [Key findings]"
                )

        logger.info(
            "Tool Executed: Study Tool completed. Task type identified: %s", task_type
        )
        return {
            "task_type": task_type,
            "prompt_instructions": instructions,
            "expected_format": fmt,
        }

    def status(self) -> Dict[str, Any]:
        """
        Return status metrics.
        """
        return {"healthy": True}

    def shutdown(self) -> None:
        """
        Perform shutdown cleanup.
        """
        logger.info("StudyTool shut down.")
