"""
EduMentor AI Embeddings Module
==============================

This module coordinates text embedding operations.
It interfaces with sentence-transformer models to convert textual blocks into
numerical representations suitable for vector storage search indexes.
"""

from typing import List, Optional
from langchain_community.embeddings import HuggingFaceEmbeddings
from modules.logger import get_logger

logger = get_logger(__name__)


class EmbeddingManager:
    """
    Manages loading, referencing, and executing embedding models.
    Uses LangChain HuggingFaceEmbeddings wrapper.
    """

    def __init__(self, model_name: str) -> None:
        """
        Initialize Embedding manager.

        Args:
            model_name (str): ID of model to load from HuggingFace.
        """
        self.model_name = model_name
        self.model: Optional[HuggingFaceEmbeddings] = None
        logger.info("EmbeddingManager created with target model: %s", model_name)

    def load_model(self) -> None:
        """
        Instantiate and cache the HuggingFace sentence-transformer model in memory.
        Ensures model loads only once.

        Raises:
            RuntimeError: If model fails to load.
        """
        if self.model is not None:
            logger.debug("EmbeddingManager: Model already loaded. Skipping.")
            return

        logger.info(
            "Embedding Model Loaded: Initializing HuggingFace sentence-transformer %s in memory...",
            self.model_name,
        )
        try:
            self.model = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={"device": "cpu"},  # Explicit CPU mapping for portability
            )
            logger.info("EmbeddingManager: Model initialized and cached successfully.")
        except Exception as e:
            logger.error(
                "EmbeddingManager: Failed to load sentence-transformer model: %s",
                str(e),
                exc_info=True,
            )
            raise RuntimeError("embedding_model_load_failed")

    def generate(self, texts: List[str]) -> List[List[float]]:
        """
        Convert list of strings into high dimensional embedding vector arrays.

        Args:
            texts (list): Strings list to encode.

        Returns:
            list: List of float arrays representing text embeddings.

        Raises:
            RuntimeError: If embedding generation fails.
        """
        if self.model is None:
            logger.info(
                "EmbeddingManager: Model is not loaded. Loading now before generation."
            )
            self.load_model()

        logger.info(
            "Embeddings Generated: Generating vectors for %d text blocks...", len(texts)
        )
        try:
            embeddings = self.model.embed_documents(texts)
            return embeddings
        except Exception as e:
            logger.error(
                "EmbeddingManager: Generation of text embeddings failed: %s",
                str(e),
                exc_info=True,
            )
            raise RuntimeError("embedding_generation_failed")

    def generate_query(self, text: str) -> List[float]:
        """
        Convert query string parameter into float array representation.

        Args:
            text (str): Query string.

        Returns:
            list: List of floats representing the query embedding.

        Raises:
            RuntimeError: If query embedding fails.
        """
        if self.model is None:
            logger.info(
                "EmbeddingManager: Model is not loaded. Loading now before query generation."
            )
            self.load_model()

        logger.debug(
            "EmbeddingManager: Generating embedding for query: %s...", text[:30]
        )
        try:
            return self.model.embed_query(text)
        except Exception as e:
            logger.error(
                "EmbeddingManager: Generation of query embedding failed: %s",
                str(e),
                exc_info=True,
            )
            raise RuntimeError("query_embedding_failed")

    def save(self, file_path: str) -> None:
        """
        Backup model configuration or state configurations locally (placeholder).
        """
        logger.info(
            "Saving embedding weights/configurations to file: %s (placeholder)",
            file_path,
        )
