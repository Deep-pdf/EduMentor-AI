"""
EduMentor AI RAG Engine Module
==============================

This module implements the Retrieval-Augmented Generation (RAG) Orchestrator.
It coordinates between PDF loaders, embedding managers, vector stores,
and the LLM client to provide context-enriched answers.
"""

import os
import time
from typing import Any, Dict, List, Tuple
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from modules.logger import get_logger

logger = get_logger(__name__)


class RAGEngine:
    """
    Orchestrates the Retrieval-Augmented Generation workflow lifecycle.
    Bridges PDFLoader, EmbeddingManager, and VectorStoreManager.
    """

    def __init__(self, vector_store_manager: Any, embedding_manager: Any) -> None:
        """
        Initialize RAGEngine dependencies.

        Args:
            vector_store_manager (Any): Manager class for DB read/writes.
            embedding_manager (Any): Manager class for embedding model vectors.
        """
        self.vector_store_manager = vector_store_manager
        self.embedding_manager = embedding_manager
        logger.info(
            "RAGEngine initialized with VectorStoreManager and EmbeddingManager."
        )

    def initialize(self) -> None:
        """
        Prepare DB connections and verify vector index states.

        Raises:
            RuntimeError: If initialization fails.
        """
        logger.info("Initializing RAG database indexes...")
        try:
            self.vector_store_manager.create_database()
            # Ensure the embedding model is loaded at startup
            self.embedding_manager.load_model()
            logger.info("RAGEngine: RAG components initialized successfully.")
        except Exception as e:
            logger.error("RAGEngine: Failed to initialize: %s", str(e), exc_info=True)
            raise RuntimeError("rag_init_failed")

    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        Process an uploaded document: extract text, clean text, split into chunks,
        index in vector database, and capture processing metrics.
        Avoids duplicate indexing of already processed documents.

        Args:
            file_path (str): Path to the saved PDF file.

        Returns:
            Dict[str, Any]: Dictionary containing status and metrics (chunks, pages, etc.).

        Raises:
            RuntimeError: If document processing fails.
        """
        from config import config

        logger.info("Chunking Started: Processing document: %s", file_path)
        start_time = time.time()

        try:
            # 1. Check if the document has already been processed and indexed in the DB
            doc_name = os.path.basename(file_path)
            client = self.vector_store_manager.get_client(
                embedding_function=self.embedding_manager.model
            )

            existing = client.get(where={"source": file_path})
            if existing and existing.get("ids"):
                logger.info(
                    "RAGEngine: Document '%s' already indexed. Skipping embedding and database write.",
                    doc_name,
                )
                total_chunks = len(existing["ids"])
                duration = time.time() - start_time

                # Retrieve total pages info using PDFLoader directly
                from modules.pdf_loader import PDFLoader

                loader = PDFLoader(
                    upload_dir=config.chroma_db_path,
                    max_size_mb=config.max_upload_size_mb,
                )
                raw_pages = loader.extract_text(file_path)

                return {
                    "status": "already_indexed",
                    "total_chunks": total_chunks,
                    "average_chunk_size": int(config.chunk_size),
                    "total_pages": len(raw_pages),
                    "duration": duration,
                    "message": f"Document '{doc_name}' is already indexed and ready.",
                }

            # 2. Extract and Clean Text
            from modules.pdf_loader import PDFLoader

            loader = PDFLoader(
                upload_dir=config.chroma_db_path, max_size_mb=config.max_upload_size_mb
            )

            # Extract
            raw_pages = loader.extract_text(file_path)
            total_pages = len(raw_pages)

            # Clean
            clean_pages = loader.clean_text(raw_pages)

            # 3. Text Chunking
            raw_docs = []
            for page_idx, page_content in enumerate(clean_pages):
                raw_docs.append(
                    Document(
                        page_content=page_content,
                        metadata={"page_number": page_idx + 1},
                    )
                )

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=config.chunk_size,
                chunk_overlap=config.chunk_overlap,
                length_function=len,
            )

            # Split
            split_docs = splitter.split_documents(raw_docs)
            total_chunks = len(split_docs)

            # Calculate metrics
            total_chunk_chars = sum(len(doc.page_content) for doc in split_docs)
            avg_chunk_size = (
                int(total_chunk_chars / total_chunks) if total_chunks > 0 else 0
            )

            # Add metadata tags
            timestamp = time.time()
            for chunk_idx, doc in enumerate(split_docs):
                doc.metadata.update(
                    {
                        "document_name": doc_name,
                        "chunk_number": chunk_idx + 1,
                        "source": file_path,
                        "timestamp": timestamp,
                    }
                )

            # 4. Generate Embeddings & Index in Vector DB
            logger.info(
                "Embedding Model Loaded: Triggering embedding generation for document..."
            )
            self.vector_store_manager.add_documents(split_docs, self.embedding_manager)

            duration = time.time() - start_time
            logger.info(
                "Chunking Finished: Total Chunks: %d, Average Chunk Size: %d, Chunking Duration: %.2f seconds",
                total_chunks,
                avg_chunk_size,
                duration,
            )

            return {
                "status": "success",
                "total_chunks": total_chunks,
                "average_chunk_size": avg_chunk_size,
                "total_pages": total_pages,
                "duration": duration,
                "message": f"Successfully processed and indexed {total_chunks} chunks.",
            }

        except Exception as e:
            logger.error(
                "RAGEngine: Failed to process document: %s", str(e), exc_info=True
            )
            raise RuntimeError("document_processing_failed")

    def retrieve(self, query: str, top_k: int = 4) -> List[Any]:
        """
        Perform semantic similarity queries to fetch relevant text chunks.

        Args:
            query (str): The search query from the user.
            top_k (int): Number of similar document chunks to retrieve.

        Returns:
            list: List of retrieved LangChain Document objects.
        """
        logger.info("RAGEngine: Executing retrieval search for query: %s", query[:50])
        try:
            # 1. Convert question to embedding
            query_embedding = self.embedding_manager.generate_query(query)

            # 2. Search database
            results = self.vector_store_manager.similarity_search(
                query_embedding, top_k=top_k
            )
            return results
        except Exception as e:
            logger.error("RAGEngine: Retrieval failed: %s", str(e), exc_info=True)
            return []

    def generate_context(self, query: str) -> Tuple[str, List[Any]]:
        """
        Retrieve chunks and compile them into a unified context block.

        Args:
            query (str): The input request query.

        Returns:
            Tuple[str, List[Any]]: Aggregated context string and original document matches.
        """
        from config import config

        logger.info(
            "RAGEngine: Generating aggregated text context for query: %s", query[:50]
        )

        # Retrieve relevant chunks using top_k from Config
        docs = self.retrieve(query, top_k=config.top_k)

        # Compile retrieved chunks
        context_chunks = []
        for idx, doc in enumerate(docs):
            page_num = doc.metadata.get("page_number", "Unknown")
            context_chunks.append(
                f"[Source Chunk {idx + 1} | Page {page_num}]:\n{doc.page_content}"
            )

        context_block = "\n\n---\n\n".join(context_chunks)
        logger.info(
            "RAGEngine: Context block compiled successfully with %d chunks.", len(docs)
        )
        return context_block, docs

    def clear_database(self) -> None:
        """
        Empty index collections and clear cached databases locally.
        """
        logger.info("Clearing RAG vector collections database...")
        try:
            self.vector_store_manager.delete_collection()
            logger.info("RAGEngine: RAG vector store cleared successfully.")
        except Exception as e:
            logger.error(
                "RAGEngine: Failed to clear database: %s", str(e), exc_info=True
            )
            raise RuntimeError("clear_database_failed")

    def status(self) -> Dict[str, Any]:
        """
        Return the operational status of the RAGEngine components.

        Returns:
            Dict[str, Any]: Configuration and data metrics of vector database.
        """
        unique_docs = set()
        total_chunks = 0
        try:
            client = self.vector_store_manager.get_client()
            results = client.get(include=["metadatas"])
            if results and results.get("metadatas"):
                total_chunks = len(results["metadatas"])
                for meta in results["metadatas"]:
                    if meta and "document_name" in meta:
                        unique_docs.add(meta["document_name"])
        except Exception:
            pass

        return {
            "db_path": self.vector_store_manager.db_path,
            "collection_name": self.vector_store_manager.collection_name,
            "embeddings_model": self.embedding_manager.model_name,
            "embedding_model_loaded": self.embedding_manager.model is not None,
            "database_initialized": self.vector_store_manager.client is not None,
            "indexed_documents": list(unique_docs),
            "total_chunks_indexed": total_chunks,
        }
