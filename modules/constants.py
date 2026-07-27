"""
EduMentor AI Constants Module
=============================

This module centralizes all constant values used across the EduMentor AI application.
To maintain clean architecture, avoid magic strings/numbers elsewhere in the codebase; 
instead, reference the constants defined here.

Future Scope:
- Add prompt template identifier constants.
- Include specialized UI theme and styling definitions.
- Set LLM hyperparameter configurations.
"""

from typing import Final, Tuple

# Application Identity
APP_TITLE: Final[str] = "EduMentor AI"
APP_SUBTITLE: Final[str] = "Your Personalized Socratic Tutor & Educational Assistant"
APP_VERSION: Final[str] = "1.0.0"

# Folder Structure
DIR_DATA: Final[str] = "data"
DIR_UPLOADS: Final[str] = "data/uploads"
DIR_VECTOR_DB: Final[str] = "vector_db"
DIR_LOGS: Final[str] = "logs"
DIR_ASSETS: Final[str] = "assets"

# File Constraints
ALLOWED_EXTENSIONS: Final[Tuple[str, ...]] = (".pdf",)
MAX_UPLOAD_SIZE_MB: Final[int] = 200

# UI Theme Config (Glassmorphism & Sleek Dark Palette)
COLOR_BACKGROUND: Final[str] = "#0E1117"
COLOR_PRIMARY: Final[str] = "#5865F2"  # Vibrant indigo
COLOR_SECONDARY: Final[str] = "#10B981"  # Emerald green
COLOR_ACCENT: Final[str] = "#EC4899"  # Deep pink
COLOR_TEXT_MUTED: Final[str] = "#8892B0"

# Future Prompt Templates Names (Placeholder identifiers)
PROMPT_TUTOR_SOCRATIC: Final[str] = "socratic_tutor"
PROMPT_SUMMARIZER: Final[str] = "pdf_summarizer"
PROMPT_QUIZ_GENERATOR: Final[str] = "quiz_generator"
PROMPT_CAREER_ADVISOR: Final[str] = "career_advisor"
PROMPT_EXPLAINER: Final[str] = "concept_explainer"

# Model Configuration Defaults
DEFAULT_MODEL: Final[str] = "llama3-70b-8192"
DEFAULT_EMBEDDING_MODEL: Final[str] = "all-MiniLM-L6-v2"
DEFAULT_TEMPERATURE: Final[float] = 0.5
DEFAULT_MAX_TOKENS: Final[int] = 2048

# Session State Keys
STATE_CHAT_HISTORY: Final[str] = "chat_history"
STATE_UPLOADED_PDFS: Final[str] = "uploaded_pdfs"
STATE_CONVERSATION_MEMORY: Final[str] = "conversation_memory"
STATE_CURRENT_MODEL: Final[str] = "current_model"
STATE_CURRENT_TOOL: Final[str] = "current_tool"
STATE_AGENT_STATUS: Final[str] = "agent_status"
STATE_SESSION_ID: Final[str] = "session_id"
STATE_SYSTEM_LOGGER: Final[str] = "system_logger"
