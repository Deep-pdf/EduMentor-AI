"""
EduMentor AI Logger Module
==========================

This module provides centralized logging initialization. It sets up both a 
console handler and a rotating file handler to save log outputs under the 
configured log directory.

Usage:
    from modules.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Application started.")
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from modules.constants import DIR_LOGS

# Ensure log directory exists
os.makedirs(DIR_LOGS, exist_ok=True)

# Default log format
LOG_FORMAT: str = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

# Global cache of initialized loggers to avoid duplicating handlers
_loggers = {}

def get_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Get or create a configured logger instance.

    Args:
        name (str): Name of the logger, typically __name__.
        log_level (str): Logging severity level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Returns:
        logging.Logger: The configured Logger instance.
    """
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    
    # Map string level to logging level integer
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # Avoid duplicate handlers if the logger has already been configured in hierarchy
    if not logger.handlers:
        # Create formatter
        formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

        # 1. Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(numeric_level)
        logger.addHandler(console_handler)

        # 2. Rotating File Handler
        log_file_path = os.path.join(DIR_LOGS, "app.log")
        try:
            file_handler = RotatingFileHandler(
                log_file_path, 
                maxBytes=5 * 1024 * 1024,  # 5 MB
                backupCount=3,
                encoding="utf-8"
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(numeric_level)
            logger.addHandler(file_handler)
        except Exception as e:
            # Fallback if file handler fails (e.g. permission error)
            print(f"Warning: Failed to initialize file logger at {log_file_path}: {e}")

        # Disable propagation so root logger doesn't duplicate logs
        logger.propagate = False

    _loggers[name] = logger
    return logger
