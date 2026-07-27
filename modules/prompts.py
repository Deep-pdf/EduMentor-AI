"""
EduMentor AI Prompt Manager Module
==================================

This module handles prompts generation templates.
Centralizes instructional templates (Socratic tutoring, document summarization, 
quiz creation, career guidance, and concept explanations) to keep prompts isolated 
from LLM invocation code.

Future Scope:
- Define structured system and user templates.
- Support dynamic variable interpolation (e.g. topic, age, learning level).
- Support LangChain prompt template loading.
"""

from typing import Any, Dict
from modules.logger import get_logger

logger = get_logger(__name__)


class PromptManager:
    """
    Manager for compiling system and user prompts for LLM operations.
    """

    def __init__(self) -> None:
        logger.info("PromptManager initialized.")

    def get_tutor_prompt(self, subject: str, student_level: str) -> Any:
        """
        Compile prompt template instructing the model to act as a Socratic tutor.

        Args:
            subject (str): Concept/Topic to teach.
            student_level (str): Academic tier of the student.

        Returns:
            Any: Compiled prompt template object.

        Raises:
            NotImplementedError: Implementation deferred to Phase 2.
        """
        logger.debug("Generating Tutor prompt for subject: %s, level: %s", subject, student_level)
        # TODO: Implement prompt compiling in Phase 2
        raise NotImplementedError("PromptManager.get_tutor_prompt() is not yet implemented.")

    def get_summarizer_prompt(self, document_context: str) -> Any:
        """
        Compile prompt instructing the model to generate a summary of document chunks.

        Args:
            document_context (str): Extracted document text.

        Returns:
            Any: Compiled prompt template object.

        Raises:
            NotImplementedError: Implementation deferred to Phase 2.
        """
        logger.debug("Generating Summarizer prompt for context chunk length: %d", len(document_context))
        # TODO: Implement summarizer templates in Phase 2
        raise NotImplementedError("PromptManager.get_summarizer_prompt() is not yet implemented.")

    def get_quiz_prompt(self, subject: str, total_questions: int) -> Any:
        """
        Compile prompt for generating evaluation quizzes dynamically.

        Args:
            subject (str): Target topic of evaluation.
            total_questions (int): Number of quiz items to produce.

        Returns:
            Any: Compiled prompt template object.

        Raises:
            NotImplementedError: Implementation deferred to Phase 2.
        """
        logger.debug("Generating Quiz prompt for subject: %s, questions: %d", subject, total_questions)
        # TODO: Implement quiz generator prompts in Phase 2
        raise NotImplementedError("PromptManager.get_quiz_prompt() is not yet implemented.")

    def get_career_advisor_prompt(self, student_profile: Dict[str, Any]) -> Any:
        """
        Compile prompt instructing model to act as a Career Advisor based on performance.

        Args:
            student_profile (dict): Performance and interests profile of student.

        Returns:
            Any: Compiled prompt template object.

        Raises:
            NotImplementedError: Implementation deferred to Phase 2.
        """
        logger.debug("Generating Career Advisor prompt for profile.")
        # TODO: Implement career advisor prompts in Phase 2
        raise NotImplementedError("PromptManager.get_career_advisor_prompt() is not yet implemented.")

    def get_explanation_prompt(self, concept: str, context: str) -> Any:
        """
        Compile prompt instructing model to explain a hard concept in multiple difficulty tiers.

        Args:
            concept (str): Concept/Term to explain.
            context (str): Contextual references.

        Returns:
            Any: Compiled prompt template object.

        Raises:
            NotImplementedError: Implementation deferred to Phase 2.
        """
        logger.debug("Generating concept Explanation prompt for: %s", concept)
        # TODO: Implement explanation prompts in Phase 2
        raise NotImplementedError("PromptManager.get_explanation_prompt() is not yet implemented.")
