"""
EduMentor AI Vector Store Module
================================

This module acts as the ChromaDB Client Manager.
Saves document chunks alongside their semantic embedding vectors, and performs
distance search calculations to fetch target documents context.
"""

import os
from typing import Any, List, Optional
import chromadb
from langchain_community.vectorstores import Chroma
from modules.logger import get_logger

logger = get_logger(__name__)


class VectorStoreManager:
    """
    Manages vector database lifecycle, indexing, and querying.
    Wraps LangChain's Chroma vector store.
    """

    def __init__(self, db_path: str, collection_name: str) -> None:
        """
        Initialize vector store parameters.

        Args:
            db_path (str): File system path to persist database folders.
            collection_name (str): ID of collection index.
        """
        self.db_path = db_path
        self.collection_name = collection_name
        self.client: Optional[Chroma] = None
        logger.info("VectorStoreManager created for path: %s", db_path)

    def get_client(self, embedding_function: Any = None) -> Chroma:
        """
        Lazy load and cache the LangChain Chroma database client instance.

        Args:
            embedding_function (Any, optional): Instance of embedding model wrapper.

        Returns:
            Chroma: Configured database client wrapper.
        """
        if self.client is None:
            logger.info(
                "VectorStoreManager: Initializing Chroma client at %s...", self.db_path
            )
            self.client = Chroma(
                persist_directory=self.db_path,
                collection_name=self.collection_name,
                embedding_function=embedding_function,
            )
        elif embedding_function is not None:
            # Bind/update embedding function dynamically if provided
            self.client._embedding_function = embedding_function
        return self.client

    def create_database(self) -> None:
        """
        Initialize persistent database engine and generate standard index collections.

        Raises:
            RuntimeError: If database instantiation fails.
        """
        logger.info(
            "Database Created: Bootstrapping vector database storage files at %s...",
            self.db_path,
        )
        try:
            # Ensure database directory exists
            os.makedirs(self.db_path, exist_ok=True)

            # Verify and instantiate persistent Chroma DB collection
            chroma_client = chromadb.PersistentClient(path=self.db_path)
            chroma_client.get_or_create_collection(name=self.collection_name)
            logger.info(
                "VectorStoreManager: Database collection '%s' created successfully.",
                self.collection_name,
            )
        except Exception as e:
            logger.error(
                "VectorStoreManager: Database bootstrapping failed: %s",
                str(e),
                exc_info=True,
            )
            raise RuntimeError("database_creation_failed")

    def add_documents(self, documents: List[Any], embeddings: Any) -> None:
        """
        Insert parsed document objects alongside compiled embeddings in database collections.

        Args:
            documents (list): Document chunks with metadata tags.
            embeddings (Any): Instance of embedding coordinator.

        Raises:
            RuntimeError: If document indexing fails.
        """
        logger.info(
            "VectorStoreManager: Inserting %d documents inside index collections...",
            len(documents),
        )
        try:
            client = self.get_client(embedding_function=embeddings.model)
            client.add_documents(documents)
            logger.info(
                "VectorStoreManager: Successfully indexed %d document chunks.",
                len(documents),
            )
        except Exception as e:
            logger.error(
                "VectorStoreManager: Failed to insert documents: %s",
                str(e),
                exc_info=True,
            )
            raise RuntimeError("chroma_add_failed")

    def similarity_search(
        self, query_embedding: List[float], top_k: int = 4
    ) -> List[Any]:
        """
        Query database vectors to locate document nodes closest to target vector.

        Args:
            query_embedding (list): Numerical embedding vector of query string.
            top_k (int): Number of matching results to yield.

        Returns:
            list: Similar document objects list (LangChain Document objects).

        Raises:
            RuntimeError: If search fails.
        """
        logger.info(
            "Similarity Search Started: Searching database vectors for query..."
        )
        try:
            client = self.get_client()
            results = client.similarity_search_by_vector(query_embedding, k=top_k)
            logger.info(
                "Similarity Search Finished: Retrieved %d matches.", len(results)
            )
            return results
        except Exception as e:
            logger.error(
                "VectorStoreManager: Similarity vector query failed: %s",
                str(e),
                exc_info=True,
            )
            raise RuntimeError("chroma_search_failed")

    def delete(self, document_ids: List[str]) -> None:
        """
        Delete targeted records or document nodes from database indexes.

        Args:
            document_ids (list): IDs of nodes to remove.

        Raises:
            RuntimeError: If deletion fails.
        """
        logger.info(
            "VectorStoreManager: Deleting %d records from collection index...",
            len(document_ids),
        )
        try:
            client = self.get_client()
            client.delete(ids=document_ids)
            logger.info(
                "VectorStoreManager: Records successfully removed from vector index."
            )
        except Exception as e:
            logger.error(
                "VectorStoreManager: Deletion from vector store failed: %s",
                str(e),
                exc_info=True,
            )
            raise RuntimeError("chroma_delete_failed")

    def delete_collection(self) -> None:
        """
        Wipes the database collection entirely and recreates it.

        Raises:
            RuntimeError: If resetting fails.
        """
        logger.info("VectorStoreManager: Wiping collection: %s", self.collection_name)
        try:
            chroma_client = chromadb.PersistentClient(path=self.db_path)
            try:
                chroma_client.delete_collection(self.collection_name)
                logger.info(
                    "VectorStoreManager: Collection '%s' deleted successfully.",
                    self.collection_name,
                )
            except ValueError:
                logger.warning(
                    "VectorStoreManager: Collection '%s' did not exist to delete.",
                    self.collection_name,
                )

            # Re-create empty collection
            chroma_client.get_or_create_collection(self.collection_name)

            # Reset client cache
            self.client = None
            logger.info(
                "VectorStoreManager: Re-initialized empty collection '%s'.",
                self.collection_name,
            )
        except Exception as e:
            logger.error(
                "VectorStoreManager: Wiping collection failed: %s",
                str(e),
                exc_info=True,
            )
            raise RuntimeError("chroma_reset_failed")
