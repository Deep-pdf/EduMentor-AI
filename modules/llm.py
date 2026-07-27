"""
EduMentor AI LLM Client Module
==============================

This module provides the LLM client manager layer.
It acts as a wrapper around the Groq model API (utilizing LangChain integrations).
All model generation requests are routed through this component, isolating
LangChain and Groq dependencies from the rest of the application.
"""

from typing import Any, Optional
from modules.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    """
    Client manager for communicating with external Large Language Model APIs (Groq Cloud).
    Provides authentication checks, error wrapping, and generation methods.
    """

    def __init__(
        self,
        model_name: str,
        temperature: float,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
    ) -> None:
        """
        Initialize LLM parameters and load configuration.

        Args:
            model_name (str): ID of the model to configure.
            temperature (float): Generation temperature.
            max_tokens (int, optional): Maximum response tokens to generate.
            api_key (str, optional): Groq API key override.
        """
        self.model_name = model_name
        self.temperature = temperature

        # Load from config inside to prevent circular import issues
        from config import config

        self.max_tokens = max_tokens or config.max_tokens
        self.api_key = api_key or config.groq_api_key

        self.client: Optional[Any] = None
        self.is_initialized: bool = False
        logger.info(
            "LLMClient created for model: %s (temperature: %f)", model_name, temperature
        )

    def initialize(self) -> None:
        """
        Establish connection to the Groq API client, validate credentials,
        and perform a lightweight check to verify network and model loading.

        Raises:
            ValueError: If the API key is missing or invalid, or if the model is unsupported.
            ConnectionError: If the internet or Groq service is unavailable.
            TimeoutError: If the API request times out.
            Exception: For other unexpected API issues.
        """
        if self.is_initialized:
            logger.debug(
                "LLMClient is already initialized and verified. Skipping check."
            )
            return

        logger.info("Initializing connection to Groq API client...")

        # 1. Check for missing API key
        if not self.api_key or self.api_key == "your_groq_api_key_here":
            logger.error(
                "Groq API initialization failed: GROQ_API_KEY is not defined or is the default template."
            )
            raise ValueError("missing_key")

        # 2. Instantiate ChatGroq
        try:
            from langchain_groq import ChatGroq

            self.client = ChatGroq(
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                groq_api_key=self.api_key,
                timeout=15,  # 15 seconds timeout
            )

            # 3. Dry-run verification to check API Key, model validity, and connection
            from langchain_core.messages import HumanMessage

            logger.info(
                "Verifying Groq API credentials and model validity using dry-run request..."
            )
            self.client.invoke([HumanMessage(content="ping")])

            self.is_initialized = True
            logger.info("Groq API initialized and verified successfully.")

        except Exception as e:
            self.client = None
            self.is_initialized = False

            err_msg = str(e).lower()
            logger.error("Groq API connection check failed: %s", str(e), exc_info=True)

            if (
                "api key" in err_msg
                or "api_key" in err_msg
                or "authentication" in err_msg
                or "unauthorized" in err_msg
                or "401" in err_msg
            ):
                raise ValueError("invalid_key")
            elif (
                "model" in err_msg
                or "not found" in err_msg
                or "404" in err_msg
                or "bad request" in err_msg
            ):
                raise ValueError("invalid_model")
            elif "rate limit" in err_msg or "429" in err_msg or "quota" in err_msg:
                raise ValueError("rate_limit")
            elif "timeout" in err_msg or "deadline" in err_msg:
                raise TimeoutError("timeout")
            elif (
                "connection" in err_msg
                or "resolve" in err_msg
                or "dns" in err_msg
                or "offline" in err_msg
                or "network" in err_msg
                or "getaddrinfo" in err_msg
            ):
                raise ConnectionError("network")
            else:
                raise Exception("general")

    def generate_response(self, system_instruction: str, user_question: str) -> str:
        """
        Send a structured Socratic generation request to the configured Groq model.

        Args:
            system_instruction (str): Compiled tutor and system instructions.
            user_question (str): Core message input from the user.

        Returns:
            str: Generated markdown text response.

        Raises:
            ValueError: If the API key is missing/invalid, or if the model is unsupported.
            ConnectionError: If network is unavailable.
            TimeoutError: If the request times out.
            Exception: For other unexpected API issues.
        """
        if not self.is_initialized or not self.client:
            logger.info(
                "LLMClient is not initialized. Triggering initialize() before request."
            )
            self.initialize()

        logger.info(
            "LLMClient: Sending Socratic prompt payload to Groq model: %s",
            self.model_name,
        )
        from langchain_core.messages import SystemMessage, HumanMessage

        try:
            messages = [
                SystemMessage(content=system_instruction),
                HumanMessage(content=user_question),
            ]
            response = self.client.invoke(messages)
            response_content = str(response.content).strip()
            logger.info(
                "LLMClient: Response received successfully (%d characters).",
                len(response_content),
            )
            return response_content

        except Exception as e:
            err_msg = str(e).lower()
            logger.error("LLMClient generation failed: %s", str(e), exc_info=True)

            if (
                "api key" in err_msg
                or "api_key" in err_msg
                or "authentication" in err_msg
                or "unauthorized" in err_msg
                or "401" in err_msg
            ):
                raise ValueError("invalid_key")
            elif (
                "model" in err_msg
                or "not found" in err_msg
                or "404" in err_msg
                or "bad request" in err_msg
            ):
                raise ValueError("invalid_model")
            elif "rate limit" in err_msg or "429" in err_msg or "quota" in err_msg:
                raise ValueError("rate_limit")
            elif "timeout" in err_msg or "deadline" in err_msg:
                raise TimeoutError("timeout")
            elif (
                "connection" in err_msg
                or "resolve" in err_msg
                or "dns" in err_msg
                or "offline" in err_msg
                or "network" in err_msg
                or "getaddrinfo" in err_msg
            ):
                raise ConnectionError("network")
            else:
                raise Exception("general")

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Send Socratic prompt matching the original placeholder signature.

        Args:
            prompt (str): Core message input from user.
            system_instruction (str, optional): Instruction to inject as the system prompt.

        Returns:
            str: Generated text response.
        """
        sys_inst = system_instruction or "You are a Socratic educational tutor."
        return self.generate_response(system_instruction=sys_inst, user_question=prompt)

    def shutdown(self) -> None:
        """
        Perform teardown steps and release model reference pools.
        """
        logger.info(
            "Shutting down LLM client instance for model: %s...", self.model_name
        )
        self.client = None
        self.is_initialized = False
