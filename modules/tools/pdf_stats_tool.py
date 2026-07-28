"""
EduMentor AI PDF Statistics Tool
=================================

This module implements the PDFStatisticsTool, which parses uploaded study documents
to extract page counts, word counts, paragraph counts, headings, and top keywords.
"""

import os
import math
import re
from collections import Counter
from typing import Any, Dict, List
import streamlit as st
import pypdf

from modules.tools.base_tool import BaseTool
from modules.logger import get_logger

logger = get_logger(__name__)


class PDFStatisticsTool(BaseTool):
    """
    Lightweight analysis tool to generate structured metadata and statistics
    about the uploaded learning materials without calling the LLM.
    """

    def __init__(self) -> None:
        """
        Initialize the PDFStatisticsTool.
        """
        logger.info("PDFStatisticsTool created.")

    def initialize(self) -> None:
        """
        Initialize tool resources.
        """
        logger.info("PDFStatisticsTool initialized.")

    def name(self) -> str:
        """
        Return the unique name of this tool.
        """
        return "PDF Statistics Tool"

    def description(self) -> str:
        """
        Return description explaining the tool's statistics capabilities.
        """
        return (
            "Analyzes uploaded PDF documents to compute page count, word count, estimated reading time, "
            "paragraph/heading counts, top keywords, and file size metadata."
        )

    def capabilities(self) -> List[str]:
        """
        Return capabilities tags.
        """
        return [
            "Document Analytics",
            "PDF Metadata Analysis",
            "Reading Metrics Extraction",
        ]

    def supported_intents(self) -> List[str]:
        """
        Return intents supported by this tool.
        """
        return ["PDF Statistics"]

    def execute(self, params: Dict[str, Any]) -> Any:
        """
        Extract document metrics and metadata from the active study PDF.

        Args:
            params (Dict[str, Any]): Parameters containing:
                - 'file_path': str (Optional override for active document path)

        Returns:
            str: Formatted markdown summary of PDF statistics.
        """
        file_path = params.get("file_path") or st.session_state.get(
            "current_document_path"
        )

        logger.info("Tool Selected: PDF Statistics Tool chosen.")
        if not file_path or not os.path.exists(file_path):
            logger.warning(
                "PDF Statistics Tool: No active document path found or file does not exist."
            )
            return "Error: No PDF document is currently uploaded. Please upload a study document first."

        import time

        start_time = time.time()

        try:
            reader = pypdf.PdfReader(file_path)
            page_count = len(reader.pages)
            file_size_bytes = os.path.getsize(file_path)
            file_size_kb = file_size_bytes / 1024
            file_size_mb = file_size_kb / 1024

            # Document Title
            doc_title = (
                reader.metadata.title
                if reader.metadata.title
                else os.path.basename(file_path)
            )
            metadata = {
                k.replace("/", ""): v for k, v in dict(reader.metadata).items() if v
            }

            # Extracted metrics
            word_count = 0
            paragraph_count = 0
            heading_count = 0
            full_text = []

            # Stopwords for simple keyword extraction
            stopwords = {
                "the",
                "of",
                "and",
                "to",
                "a",
                "in",
                "is",
                "that",
                "it",
                "for",
                "on",
                "with",
                "as",
                "was",
                "at",
                "by",
                "an",
                "be",
                "this",
                "are",
                "from",
                "or",
                "have",
                "you",
                "not",
                "your",
                "we",
                "he",
                "she",
                "they",
                "but",
                "their",
                "will",
                "can",
                "has",
                "more",
                "about",
                "would",
                "their",
                "there",
            }

            for page_num, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                full_text.append(text)

                # Words
                words = text.split()
                word_count += len(words)

                # Paragraphs estimation
                paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
                paragraph_count += len(paragraphs)

                # Headings estimation (short capitalized lines without ending punctuation)
                lines = text.split("\n")
                for line in lines:
                    line_stripped = line.strip()
                    if 3 <= len(line_stripped) <= 60 and not line_stripped.endswith(
                        (".", "?", "!")
                    ):
                        # Check if it has title casing or significant uppercase words
                        if sum(1 for c in line_stripped if c.isupper()) >= 2:
                            heading_count += 1

            combined_text = " ".join(full_text)
            # Find words containing only letters
            all_words = re.findall(r"\b[a-zA-Z]{3,15}\b", combined_text.lower())
            filtered_words = [w for w in all_words if w not in stopwords]
            word_freqs = Counter(filtered_words).most_common(10)
            top_keywords = ", ".join(
                f"**{word}** ({count})" for word, count in word_freqs
            )

            # Estimated reading speed: 200 words per minute
            reading_time_min = math.ceil(word_count / 200)

            duration = time.time() - start_time
            logger.info(
                "Tool Executed: PDF Statistics Tool completed. Duration: %.2f seconds",
                duration,
            )

            # Build markdown response
            size_str = (
                f"{file_size_mb:.2f} MB"
                if file_size_mb >= 1.0
                else f"{file_size_kb:.1f} KB"
            )
            response = (
                f"### 📊 Study Material Analytics: {doc_title}\n"
                f"- **File Name:** `{os.path.basename(file_path)}`\n"
                f"- **File Size:** `{size_str}`\n"
                f"- **Total Pages:** `{page_count}` page(s)\n"
                f"- **Total Words:** `{word_count:,}` words\n"
                f"- **Estimated Reading Time:** `{reading_time_min}` minute(s)\n"
                f"- **Estimated Paragraphs:** `{paragraph_count}`\n"
                f"- **Estimated Headings/Sections:** `{heading_count}`\n\n"
                f"#### 🔑 Top Keywords Found\n"
                f"{top_keywords if top_keywords else 'No significant keywords extracted.'}\n\n"
                f"#### 📂 PDF Document Metadata\n"
            )

            if metadata:
                for k, v in metadata.items():
                    response += f"- **{k}:** `{v}`\n"
            else:
                response += "*No additional metadata fields populated.*"

            logger.info("Tool Returned Data: PDF analytics text compiled successfully.")
            return response

        except Exception as e:
            logger.error(
                "Tool Failed: PDF Statistics Tool execution failed: %s",
                str(e),
                exc_info=True,
            )
            return f"Failed to extract statistics from PDF: {str(e)}"

    def status(self) -> Dict[str, Any]:
        """
        Return status metrics.
        """
        return {"healthy": True}

    def shutdown(self) -> None:
        """
        Perform shutdown cleanup.
        """
        logger.info("PDFStatisticsTool shut down.")
