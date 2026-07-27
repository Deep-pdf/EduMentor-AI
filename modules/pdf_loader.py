"""
EduMentor AI PDF Loader Module
==============================

This module implements utilities for handling uploaded PDF materials.
Validates file sizes, parses layout formatting using PyPDF libraries,
extracts text nodes, and cleans them to optimize embeddings.
"""

import os
import time
import re
from typing import Any, List
import pypdf
from modules.logger import get_logger

logger = get_logger(__name__)


class PDFLoader:
    """
    Handles PDF material loading, file validations, and text extraction steps.
    """

    def __init__(self, upload_dir: str, max_size_mb: int) -> None:
        """
        Initialize PDF loader settings and ensure upload directory exists.

        Args:
            upload_dir (str): Folder path to save copies of uploads.
            max_size_mb (int): Max upload size restriction.
        """
        self.upload_dir = upload_dir
        self.max_size_mb = max_size_mb
        os.makedirs(self.upload_dir, exist_ok=True)
        logger.info(
            "PDFLoader created with uploads path: %s (limit: %d MB)",
            upload_dir,
            max_size_mb,
        )

    def upload(self, file_object: Any) -> str:
        """
        Save the uploaded streamlit file object to the local filesystem upload directory.

        Args:
            file_object (Any): Streamlit uploaded file handle.

        Returns:
            str: Path to the saved file copy.

        Raises:
            ValueError: If file size exceeds the limit.
            IOError: If saving the file fails.
        """
        logger.info("PDFLoader: Saving file upload to directory: %s", self.upload_dir)
        try:
            # Check file size
            file_bytes = file_object.getvalue()
            file_size_mb = len(file_bytes) / (1024 * 1024)
            if file_size_mb > self.max_size_mb:
                logger.error(
                    "PDFLoader: Upload size %f MB exceeds maximum limit of %d MB",
                    file_size_mb,
                    self.max_size_mb,
                )
                raise ValueError("upload_size_limit")

            # Extract a safe filename to prevent path traversal
            file_name = file_object.name
            safe_name = os.path.basename(file_name)
            file_path = os.path.join(self.upload_dir, safe_name)

            # Write file copy to data/uploads
            with open(file_path, "wb") as f:
                f.write(file_bytes)

            logger.info("PDF Uploaded: Saved successfully at %s", file_path)
            return file_path
        except ValueError as ve:
            raise ve
        except Exception as e:
            logger.error(
                "PDFLoader: Failed to save uploaded file: %s", str(e), exc_info=True
            )
            raise IOError("upload_failed")

    def validate(self, file_path: str) -> bool:
        """
        Validate file characteristics such as size limits and format integrity.

        Args:
            file_path (str): File path to evaluate.

        Returns:
            bool: True if file meets validation rules.
        """
        logger.info("PDFLoader: Validating file characteristics for: %s", file_path)
        if not os.path.exists(file_path):
            logger.error(
                "PDFLoader: Validation failed. File does not exist: %s", file_path
            )
            return False

        try:
            # Validate size limits
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > self.max_size_mb:
                logger.error(
                    "PDFLoader: File size %f MB exceeds limits of %d MB",
                    file_size_mb,
                    self.max_size_mb,
                )
                return False

            # Validate readability and non-corruption
            reader = pypdf.PdfReader(file_path)
            if len(reader.pages) == 0:
                logger.error("PDFLoader: PDF file has 0 pages or is corrupted.")
                return False

            # Verify we can read text from the first page
            _ = reader.pages[0].extract_text()
            logger.info("PDFLoader: File validation passed for %s", file_path)
            return True
        except Exception as e:
            logger.error(
                "PDFLoader: PDF integrity check failed: %s", str(e), exc_info=True
            )
            return False

    def extract_text(self, file_path: str) -> List[str]:
        """
        Extract page text strings using PyPDF reader utilities.

        Args:
            file_path (str): Path of file to parse.

        Returns:
            List[str]: List of raw string content extracted per page.

        Raises:
            IOError: If parsing fails.
        """
        logger.info("PDFLoader: Extracting document content from file: %s", file_path)
        start_time = time.time()
        raw_pages: List[str] = []
        total_chars = 0

        try:
            reader = pypdf.PdfReader(file_path)
            total_pages = len(reader.pages)
            logger.info("PDFLoader: PDF has %d pages to extract.", total_pages)

            for page_num in range(total_pages):
                page = reader.pages[page_num]
                text = page.extract_text() or ""
                raw_pages.append(text)
                total_chars += len(text)

            duration = time.time() - start_time
            logger.info(
                "PDF Loaded: %d pages, Characters Extracted: %d, Processing Time: %.2f seconds",
                total_pages,
                total_chars,
                duration,
            )
            return raw_pages
        except Exception as e:
            logger.error("PDFLoader: Text extraction failed: %s", str(e), exc_info=True)
            raise IOError("extraction_failed")

    def clean_text(self, raw_pages: List[str]) -> List[str]:
        """
        Apply text normalization rules (strip whitespaces, remove junk encodings).

        Args:
            raw_pages (List[str]): Extracted page strings list.

        Returns:
            List[str]: List of clean string pages.
        """
        logger.info("PDFLoader: Cleaning raw text pages...")
        clean_pages: List[str] = []

        for text in raw_pages:
            if not text:
                clean_pages.append("")
                continue

            # Replace Carriage Returns and common byte representations
            text_cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
            text_cleaned = text_cleaned.replace("\u00a0", " ").replace("\t", " ")

            # Split text by double newline to preserve paragraph separation
            paragraphs = text_cleaned.split("\n\n")
            cleaned_paragraphs = []

            for para in paragraphs:
                # Remove excessive whitespace inside each paragraph
                para_clean = re.sub(r"\s+", " ", para).strip()
                if para_clean:
                    cleaned_paragraphs.append(para_clean)

            # Re-assemble page text using double newlines
            page_clean = "\n\n".join(cleaned_paragraphs)
            clean_pages.append(page_clean)

        logger.info(
            "PDFLoader: Text cleaning finished. Total pages cleaned: %d",
            len(clean_pages),
        )
        return clean_pages
