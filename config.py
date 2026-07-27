"""
EduMentor AI Configuration Module
=================================

This module handles centralized configuration management for EduMentor AI.
It loads environment variables from a `.env` file and defines the system's
operational parameters using Python dataclasses.
All modules should refer to the global `config` instance generated here.
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

from modules.constants import (
    DEFAULT_MODEL,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    MAX_UPLOAD_SIZE_MB,
    DIR_VECTOR_DB,
    APP_TITLE,
)

# Load environment variables from environment or local .env file
load_dotenv()


@dataclass
class AppConfig:
    """
    Centralized configurations object mapping environment parameters.
    Values default to constants if not specified in the environment.
    """

    # General Info
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", APP_TITLE))
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    theme: str = field(default_factory=lambda: os.getenv("THEME", "dark"))

    # LLM Settings (Groq API)
    groq_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("GROQ_API_KEY")
    )
    model_name: str = field(
        default_factory=lambda: os.getenv("MODEL_NAME", DEFAULT_MODEL)
    )
    temperature: float = field(
        default_factory=lambda: float(
            os.getenv("TEMPERATURE", str(DEFAULT_TEMPERATURE))
        )
    )
    max_tokens: int = field(
        default_factory=lambda: int(os.getenv("MAX_TOKENS", str(DEFAULT_MAX_TOKENS)))
    )

    # Embeddings & Vector Database settings
    embedding_model_name: str = field(
        default_factory=lambda: os.getenv(
            "EMBEDDINGS_MODEL_NAME", DEFAULT_EMBEDDING_MODEL
        )
    )
    chroma_db_path: str = field(
        default_factory=lambda: os.getenv("CHROMA_DB_PATH", DIR_VECTOR_DB)
    )

    # File uploads limits
    max_upload_size_mb: int = field(
        default_factory=lambda: int(os.getenv("UPLOAD_LIMIT", str(MAX_UPLOAD_SIZE_MB)))
    )

    # RAG Settings
    chunk_size: int = field(
        default_factory=lambda: int(os.getenv("CHUNK_SIZE", "1000"))
    )
    chunk_overlap: int = field(
        default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "200"))
    )
    top_k: int = field(default_factory=lambda: int(os.getenv("TOP_K", "4")))
    collection_name: str = field(
        default_factory=lambda: os.getenv("COLLECTION_NAME", "edumentor_collection")
    )

    def validate(self) -> None:
        """
        Validate application configuration properties and emit logger warnings
        for missing required environments.
        """
        # Import logger here to prevent circular import during initialization
        from modules.logger import get_logger

        logger = get_logger("config", log_level=self.log_level)

        logger.info("Initializing configuration validation...")

        if not self.groq_api_key:
            logger.warning(
                "GROQ_API_KEY environment variable is not defined. LLM connection will fail in later phases."
            )
        else:
            logger.info("GROQ_API_KEY is defined in the configuration.")

        logger.info("Application configurations loaded successfully.")


# Instantiate global configuration
config = AppConfig()
config.validate()
