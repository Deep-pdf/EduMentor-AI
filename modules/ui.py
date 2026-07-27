"""
EduMentor AI UI Module
======================

This module is responsible for rendering all Streamlit UI components.
It abstracts rendering logic for the Header, Sidebar, Chat Window, and Footer
to enforce separation of concerns.

Future Scope:
- Connect inputs to state management.
- Bind upload events to PDF processors.
- Render message loops dynamically from historical state.
"""

import streamlit as st
from modules.constants import (
    APP_TITLE,
    APP_SUBTITLE,
    APP_VERSION,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_TEXT_MUTED
)
from modules.logger import get_logger

logger = get_logger(__name__)


class UIController:
    """
    Renders Streamlit layout components for the EduMentor AI application interface.
    """

    def __init__(self) -> None:
        logger.info("Initializing UIController instances.")

    def inject_custom_styles(self) -> None:
        """
        Inject CSS stylesheets to build premium, modern Glassmorphism visuals.
        """
        logger.debug("Injecting custom CSS styling.")
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-color: #0E1117;
                color: #FFFFFF;
            }}
            .main-header {{
                text-align: center;
                padding: 1.5rem 0rem;
                background: linear-gradient(135deg, {COLOR_PRIMARY}22, {COLOR_SECONDARY}22);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.05);
                margin-bottom: 2rem;
            }}
            .main-title {{
                font-family: 'Outfit', 'Inter', sans-serif;
                font-size: 2.8rem;
                font-weight: 800;
                background: linear-gradient(to right, #6366F1, #10B981);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0.2rem;
            }}
            .main-subtitle {{
                color: {COLOR_TEXT_MUTED};
                font-size: 1.1rem;
                font-weight: 400;
            }}
            .chat-bubble {{
                background: rgba(255, 255, 255, 0.03);
                border-radius: 8px;
                padding: 1rem;
                border-left: 4px solid {COLOR_PRIMARY};
                margin-bottom: 1rem;
            }}
            .chat-bubble-user {{
                background: rgba(88, 101, 242, 0.08);
                border-radius: 8px;
                padding: 1rem;
                border-left: 4px solid {COLOR_SECONDARY};
                margin-bottom: 1rem;
            }}
            .footer-text {{
                text-align: center;
                color: {COLOR_TEXT_MUTED};
                font-size: 0.85rem;
                padding: 2rem 0;
            }}
            .status-tag {{
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-size: 0.8rem;
                font-weight: bold;
                background-color: rgba(16, 185, 129, 0.1);
                color: {COLOR_SECONDARY};
                border: 1px solid {COLOR_SECONDARY}33;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

    def render_header(self) -> None:
        """
        Renders the application header structure.
        """
        logger.debug("Rendering Header component.")
        st.markdown(
            f"""
            <div class="main-header">
                <div class="main-title">{APP_TITLE}</div>
                <div class="main-subtitle">{APP_SUBTITLE}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    def render_sidebar(self) -> None:
        """
        Renders control elements inside the Streamlit Sidebar.
        """
        logger.debug("Rendering Sidebar component.")
        with st.sidebar:
            st.markdown("### 🎓 Session Control")
            
            # Placeholder selector for LLM Models
            st.selectbox(
                "Tutor Engine Model (Placeholder)",
                options=["llama3-70b-8192", "llama3-8b-8192"],
                disabled=True,
                help="Select engine in future phases."
            )

            # Placeholder file uploader
            st.markdown("### 📂 Learning Material")
            st.file_uploader(
                "Upload Syllabus/PDF (Placeholder)",
                type=["pdf"],
                disabled=True,
                help="Upload disabled. Feature will be activated in Phase 3."
            )

            st.markdown("---")
            
            # System Status Section
            st.markdown("### ⚙️ System Status")
            st.markdown(
                """
                - **Architecture Status:** <span class="status-tag">Initialized</span>
                - **Session Storage:** <span class="status-tag">Ready</span>
                - **AI Backend:** <span class="status-tag" style="background-color:rgba(88,101,242,0.1);color:#5865F2;border-color:#5865F233;">Placeholder Mode</span>
                """,
                unsafe_allow_html=True
            )

    def render_chat_window(self) -> None:
        """
        Renders mock interface chat boxes representing dialogue streams.
        """
        logger.debug("Rendering Chat Window component.")
        
        # Display setup status card
        st.info("💡 **Welcome to Phase 1 Architecture Initialization!** The skeleton structures are fully loaded and operational.")
        
        st.markdown("### 💬 Conversational Tutor Workspace")
        
        # UI Placeholder Chat Bubbles (showing future socratic interactions)
        st.markdown(
            """
            <div class="chat-bubble">
                <strong>EduMentor AI:</strong> Hello! I am your AI Socratic Tutor. 
                Once future phases are implemented, we will walk through your material together. 
                What concept would you like to explore today?
            </div>
            <div class="chat-bubble-user">
                <strong>Student (You):</strong> [Chat input is disabled during architecture phase]
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Render a disabled text input box
        st.text_input(
            "Send a message to your tutor (Placeholder)...",
            placeholder="Type your question here...",
            disabled=True,
            help="Chat submission will be linked to the Agent runner in Phase 4."
        )

    def render_footer(self) -> None:
        """
        Renders the application footer.
        """
        logger.debug("Rendering Footer component.")
        st.markdown(
            f"""
            <div class="footer-text">
                EduMentor AI v{APP_VERSION} — Core Framework Architecture &bull; Designed for Streamlit Cloud
            </div>
            """,
            unsafe_allow_html=True
        )
