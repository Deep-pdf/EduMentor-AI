"""
EduMentor AI Memory Module
==========================

This module handles session-based conversational history management.
Maintains history contexts, formats window messages for LLM inputs,
and produces summary structures of the discussion.
"""

import time
import streamlit as st
from typing import Any, List, Dict
from modules.logger import get_logger

logger = get_logger(__name__)


class ConversationMemory:
    """
    Manages conversational memory buffer streams and state histories.
    Uses Streamlit session state for session-based isolation.
    """

    def __init__(self, session_id: str, limit: int = 10) -> None:
        """
        Initialize conversational memory manager.

        Args:
            session_id (str): Unique session tag for isolating client history.
            limit (int): Max number of message turns (user + assistant) to keep in context window.
        """
        self.session_id = session_id
        self.limit = limit
        self.state_key = f"memory_history_{session_id}"

        # Initialize the backing storage inside Streamlit session state
        if self.state_key not in st.session_state:
            st.session_state[self.state_key] = []

        logger.info("ConversationMemory created for session: %s (limit: %d turns)", session_id, limit)

    def add(self, role: str, content: str) -> None:
        """
        Save a new dialogue utterance (from user or assistant) to memory storage.

        Args:
            role (str): Sender of the message (e.g. "user", "assistant").
            content (str): The body text of the message.
        """
        logger.info("Memory Saved: Adding %s message to memory store...", role)
        messages = st.session_state[self.state_key]

        # Append new message node with order and timestamp metadata
        messages.append({
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "order": len(messages)
        })
        logger.info("ConversationMemory: Saved successfully. Current queue length: %d", len(messages))

    def load(self) -> List[Dict[str, Any]]:
        """
        Retrieve all formatted messages stored for the current session window.

        Returns:
            list: List of dictionaries matching conversation message schemas.
        """
        logger.debug("Loading conversational messages from memory...")
        return st.session_state.get(self.state_key, [])

    def load_recent(self, limit: int = None) -> List[Dict[str, str]]:
        """
        Load a subset of recent messages formatted for LLM invocation.

        Args:
            limit (int, optional): Max message turns (user + assistant) to return. Defaults to self.limit.

        Returns:
            list: List of dictionaries with 'role' and 'content' keys.
        """
        window = limit if limit is not None else self.limit
        msg_limit = window * 2  # 1 turn = 1 user + 1 assistant message

        messages = self.load()
        recent_messages = messages[-msg_limit:] if msg_limit > 0 else messages

        return [{"role": m["role"], "content": m["content"]} for m in recent_messages]

    def clear(self) -> None:
        """
        Reset memory logs and delete current session conversations.
        """
        logger.info("Memory Saved: Clearing memory cache for session: %s", self.session_id)
        st.session_state[self.state_key] = []
        logger.info("ConversationMemory: Memory cache wiped.")

    def summarize(self) -> str:
        """
        Invoke the LLM or concatenate historical message trails into a brief overview.

        Returns:
            str: Summary string representation.
        """
        logger.info("Summarizing conversational memory records...")
        recent_turns = self.load_recent()
        if not recent_turns:
            return "No conversation history available to summarize."

        summary_lines = []
        for msg in recent_turns:
            role = "Student" if msg["role"] == "user" else "Tutor"
            summary_lines.append(f"{role}: {msg['content']}")

        return "Conversation Summary:\n" + "\n".join(summary_lines)
