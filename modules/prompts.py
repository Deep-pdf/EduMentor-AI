"""
EduMentor AI Prompt Manager Module
==================================

This module handles prompt templates and generation templates.
It centralizes instructional templates (System, Socratic tutoring, greetings,
and user-friendly error messages) to keep prompts isolated from LLM invocation
and application UI code.
"""

from typing import Any, Dict
from modules.logger import get_logger

logger = get_logger(__name__)


class PromptManager:
    """
    Manager for compiling system, tutor, greeting, and error prompts for LLM operations.
    """

    # Centralized System Prompt
    SYSTEM_PROMPT: str = (
        "You are EduMentor AI, a personalized, professional AI Socratic Tutor "
        "and Educational Assistant."
    )

    # Centralized Socratic Tutor Prompt
    TUTOR_PROMPT: str = (
        "Your primary directive is to behave as an educational tutor. "
        "Adopt a personality that is Friendly, Professional, Patient, and Encouraging. "
        "Adhere to the following Socratic tutoring rules:\n"
        "1. Never fabricate facts intentionally. If you do not know the answer or are "
        "uncertain, clearly admit your uncertainty.\n"
        "2. Explain concepts clearly and concisely, breaking down complex topics step-by-step.\n"
        "3. Guide the student's thinking rather than immediately giving away the direct answer "
        "to a problem unless they are completely stuck.\n"
        "4. Avoid giving harmful, inappropriate, or non-educational advice.\n"
        "5. Structure your responses professionally. Use Markdown formatting (such as bullet "
        "points, headers, bold text, and blockquotes) to make answers highly readable and structured."
    )

    # Centralized Greeting Prompt
    GREETING_PROMPT: str = (
        "Hello! I am EduMentor AI, your personalized Socratic Tutor and Educational Assistant. "
        "I'm here to help you understand complex concepts, practice questions, or answer your academic queries. "
        "What concept or subject would you like to explore today?"
    )

    # Centralized User-Friendly Error Prompts
    ERROR_PROMPTS: Dict[str, str] = {
        "missing_key": (
            "⚠️ **Configuration Error:** The Groq API key is missing. Please ensure that "
            "`GROQ_API_KEY` is defined in your `.env` file and restart the application."
        ),
        "invalid_key": (
            "🔑 **Authentication Error:** The Groq API key provided appears to be invalid or unauthorized. "
            "Please check the API key in your `.env` file."
        ),
        "network": (
            "🌐 **Connection Error:** Unable to reach the Groq API. Please check your internet connection "
            "and try again."
        ),
        "rate_limit": (
            "⏳ **Rate Limit Exceeded:** Too many requests have been sent to Groq. Please wait a moment "
            "before trying again."
        ),
        "timeout": (
            "⏱️ **Timeout Error:** The request to the Groq API timed out. Please try sending your question again."
        ),
        "invalid_model": (
            "🤖 **Model Error:** The configured model is invalid or not supported by Groq. "
            "Please check your `.env` file and verify `MODEL_NAME`."
        ),
        "general": (
            "❌ **Tutor Error:** An unexpected error occurred while communicating with the AI Tutor. "
            "Please try again."
        ),
    }

    def __init__(self) -> None:
        """
        Initialize the PromptManager and log instantiation.
        """
        logger.info("PromptManager initialized.")

    def get_system_prompt(self) -> str:
        """
        Retrieve the centralized system prompt.

        Returns:
            str: Centralized system prompt string.
        """
        return self.SYSTEM_PROMPT

    def get_tutor_prompt(self, subject: str = "", student_level: str = "") -> str:
        """
        Retrieve the tutor prompt template. Supports optional parameterization.

        Args:
            subject (str, optional): Concept/Topic to teach.
            student_level (str, optional): Academic level of the student.

        Returns:
            str: Centralized tutor instruction prompt string.
        """
        prompt = self.TUTOR_PROMPT
        if subject or student_level:
            context_add = f"\nCurrently assisting the student with '{subject}'"
            if student_level:
                context_add += f" at an '{student_level}' level."
            else:
                context_add += "."
            prompt += context_add
        return prompt

    def get_greeting_prompt(self) -> str:
        """
        Retrieve the centralized welcome message for the student.

        Returns:
            str: Centralized welcome message string.
        """
        return self.GREETING_PROMPT

    def get_error_prompt(self, error_key: str) -> str:
        """
        Retrieve a user-friendly error message based on an error category.

        Args:
            error_key (str): Category of the error (e.g. 'missing_key', 'network', etc.).

        Returns:
            str: Friendly error string to display in UI.
        """
        return self.ERROR_PROMPTS.get(error_key, self.ERROR_PROMPTS["general"])

    def build_tutor_prompt(self, user_question: str) -> Dict[str, str]:
        """
        Construct a structured prompt dictionary containing compiled instructions and user question.
        No LangChain message objects are returned to keep internals hidden.

        Args:
            user_question (str): The raw message from the user.

        Returns:
            Dict[str, str]: A dictionary with 'system' and 'user' keys.
        """
        logger.info(
            "PromptManager: Compiling System + Tutor instructions with user question."
        )
        system_content = f"{self.get_system_prompt()}\n\n{self.get_tutor_prompt()}"
        return {"system": system_content, "user": user_question}

    # Maintaining placeholder methods from original skeleton to prevent breaking compatibility
    def get_summarizer_prompt(self, document_context: str) -> Any:
        """
        Compile prompt instructing the model to generate a summary of document chunks.

        Args:
            document_context (str): Extracted document text.

        Raises:
            NotImplementedError: Implementation deferred to later phases.
        """
        logger.debug("Generating Summarizer prompt placeholder.")
        raise NotImplementedError(
            "PromptManager.get_summarizer_prompt() is not yet implemented."
        )

    def get_quiz_prompt(self, subject: str, total_questions: int) -> Any:
        """
        Compile prompt for generating evaluation quizzes dynamically.

        Args:
            subject (str): Target topic of evaluation.
            total_questions (int): Number of quiz items to produce.

        Raises:
            NotImplementedError: Implementation deferred to later phases.
        """
        logger.debug("Generating Quiz prompt placeholder.")
        raise NotImplementedError(
            "PromptManager.get_quiz_prompt() is not yet implemented."
        )

    def get_career_advisor_prompt(self, student_profile: Dict[str, Any]) -> Any:
        """
        Compile prompt instructing model to act as a Career Advisor based on performance.

        Args:
            student_profile (dict): Performance and interests profile of student.

        Raises:
            NotImplementedError: Implementation deferred to later phases.
        """
        logger.debug("Generating Career Advisor prompt placeholder.")
        raise NotImplementedError(
            "PromptManager.get_career_advisor_prompt() is not yet implemented."
        )

    def get_explanation_prompt(self, concept: str, context: str) -> Any:
        """
        Compile prompt instructing model to explain a hard concept in multiple difficulty tiers.

        Args:
            concept (str): Concept/Term to explain.
            context (str): Contextual references.

        Raises:
            NotImplementedError: Implementation deferred to later phases.
        """
        logger.debug("Generating concept Explanation prompt placeholder.")
        raise NotImplementedError(
            "PromptManager.get_explanation_prompt() is not yet implemented."
        )
