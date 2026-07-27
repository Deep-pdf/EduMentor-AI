"""
EduMentor AI Modules Package
============================

This package contains all modular abstractions for the application backend
and frontend routing. It isolates systems to enforce Separation of Concerns
and SOLID development principles.

Exposes:
- UIController (ui)
- LLMClient (llm)
- PromptManager (prompts)
- RAGEngine (rag)
- ConversationMemory (memory)
- ToolManager (tools)
- AIAgent (agent)
- PDFLoader (pdf_loader)
- EmbeddingManager (embeddings)
- VectorStoreManager (vector_store)
"""

from modules.ui import UIController
from modules.llm import LLMClient
from modules.prompts import PromptManager
from modules.rag import RAGEngine
from modules.memory import ConversationMemory
from modules.tools import ToolManager
from modules.agent import AIAgent
from modules.pdf_loader import PDFLoader
from modules.embeddings import EmbeddingManager
from modules.vector_store import VectorStoreManager
from modules.tool_registry import ToolRegistry

__all__ = [
    "UIController",
    "LLMClient",
    "PromptManager",
    "RAGEngine",
    "ConversationMemory",
    "ToolManager",
    "AIAgent",
    "PDFLoader",
    "EmbeddingManager",
    "VectorStoreManager",
    "ToolRegistry",
]
