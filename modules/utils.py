"""
EduMentor AI Utilities Module
=============================

This module provides common helper functions used across the application.
Includes placeholder methods for future implementations of string validation, 
file path resolution, system utilities, and data formatting.

Future Scope:
- PDF byte size checks.
- Text cleaning helper functions.
- Local time formatting for chat messages.
"""

import os
from typing import Any, Dict
from modules.logger import get_logger

logger = get_logger(__name__)


class FileUtils:
    """
    Utilities for managing local files and paths safely.
    """

    @staticmethod
    def validate_file_extension(file_name: str) -> bool:
        """
        Check if the file type uploaded is valid (e.g. PDF).

        TODO:
        Verify extensions dynamically based on constants settings.
        """
        logger.debug("Validating file extension for name: %s", file_name)
        # Placeholder implementation
        return file_name.lower().endswith(".pdf")

    @staticmethod
    def get_safe_filename(file_name: str) -> str:
        """
        Sanitize standard filenames to prevent path traversal issues.

        TODO:
        Implement comprehensive filename cleaning in Phase 3.
        """
        logger.debug("Sanitizing filename: %s", file_name)
        # Placeholder implementation
        return os.path.basename(file_name).replace(" ", "_")


class FormattingUtils:
    """
    Utilities for transforming and formatting data representations.
    """

    @staticmethod
    def format_bytes_to_mb(size_bytes: int) -> float:
        """
        Convert raw bytes to human readable Megabytes.
        """
        logger.debug("Formatting bytes: %d", size_bytes)
        return size_bytes / (1024 * 1024)

    @staticmethod
    def format_chat_message(role: str, content: str) -> Dict[str, str]:
        """
        Format message dictionaries to comply with LLM history specifications.
        """
        logger.debug("Formatting message for role: %s", role)
        return {
            "role": role,
            "content": content
        }


class SystemUtils:
    """
    Common utilities for debugging and checking environment constraints.
    """

    @staticmethod
    def check_directory_exists(directory_path: str) -> bool:
        """
        Verify if a given path exists and is a directory.
        """
        logger.debug("Checking directory: %s", directory_path)
        return os.path.isdir(directory_path)

    @staticmethod
    def sanitize_env_value(value: Any) -> str:
        """
        Clean whitespace or configurations loaded from environmental scopes.
        """
        return str(value).strip()
