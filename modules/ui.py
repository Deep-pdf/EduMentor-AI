"""
EduMentor AI UI Module
======================

This module is responsible for rendering all Streamlit UI components.
It abstracts rendering logic for the Header, Sidebar, Chat Window, and Footer
to enforce separation of concerns, and binds UI interactions directly to the
LLMClient and PromptManager state objects.
"""

import streamlit as st
from modules.constants import (
    APP_SUBTITLE,
    APP_VERSION,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_TEXT_MUTED,
    STATE_CHAT_HISTORY,
)
from modules.logger import get_logger

logger = get_logger(__name__)


class UIController:
    """
    Renders Streamlit layout components for the EduMentor AI application interface.
    Coordinates interaction logic with LLMClient and PromptManager.
    """

    def __init__(self) -> None:
        """
        Initialize UIController and log creation.
        """
        logger.info("UIController instance created.")

    def inject_custom_styles(self) -> None:
        """
        Inject CSS stylesheets to build premium, modern Glassmorphism visuals
        respecting the theme configured in AppConfig.
        """
        logger.debug("Injecting custom CSS styling.")

        # Load theme from config
        from config import config

        theme = config.theme.lower()

        if theme == "light":
            bg_color = "#F8FAFC"
            text_color = "#0F172A"
            header_gradient = "linear-gradient(135deg, rgba(88, 101, 242, 0.1), rgba(16, 185, 129, 0.1))"
            card_border = "rgba(0, 0, 0, 0.05)"
            tag_bg = "rgba(88, 101, 242, 0.1)"
            tag_text = "#5865F2"
        else:
            bg_color = "#0E1117"
            text_color = "#FFFFFF"
            header_gradient = (
                f"linear-gradient(135deg, {COLOR_PRIMARY}22, {COLOR_SECONDARY}22)"
            )
            card_border = "rgba(255, 255, 255, 0.05)"
            tag_bg = "rgba(16, 185, 129, 0.1)"
            tag_text = COLOR_SECONDARY

        st.markdown(
            f"""
            <style>
            .stApp {{
                background-color: {bg_color};
                color: {text_color};
            }}
            .main-header {{
                text-align: center;
                padding: 1.5rem 0rem;
                background: {header_gradient};
                border-radius: 12px;
                border: 1px solid {card_border};
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
            .footer-text {{
                text-align: center;
                color: {COLOR_TEXT_MUTED};
                font-size: 0.85rem;
                padding: 2rem 0;
            }}
            .status-tag {{
                display: inline-block;
                padding: 0.35rem 0.75rem;
                border-radius: 6px;
                font-size: 0.85rem;
                font-weight: bold;
                margin: 0.5rem 0;
                border: 1px solid {tag_text}33;
                background-color: {tag_bg};
                color: {tag_text};
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

    def render_header(self) -> None:
        """
        Renders the application header structure.
        """
        from config import config

        logger.debug("Rendering Header component.")
        st.markdown(
            f"""
            <div class="main-header">
                <div class="main-title">{config.app_name}</div>
                <div class="main-subtitle">{APP_SUBTITLE}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def render_sidebar(self) -> None:
        """
        Renders control elements and session status information inside the Streamlit Sidebar.
        """
        from config import config

        logger.debug("Rendering Sidebar component.")
        with st.sidebar:
            st.markdown(f"## 🎓 {config.app_name}")
            st.markdown("---")

            # Tutor Engine model configuration info
            st.markdown("### 🤖 Tutor Engine")
            st.info(f"**Current Model:**\n`{config.model_name}`")
            st.caption("Change model by editing `MODEL_NAME` in the `.env` file.")

            st.markdown("---")

            # System Status Section showing LLM Connection
            st.markdown("### ⚙️ Connection Status")
            status = st.session_state.get("connection_status", "Connecting...")

            if status == "Connected":
                st.markdown(
                    '<span class="status-tag" style="background-color:rgba(16,185,129,0.1);color:#10B981;border-color:#10B98133;">🟢 Connected to Groq</span>',
                    unsafe_allow_html=True,
                )
            elif status == "Connecting...":
                st.markdown(
                    '<span class="status-tag" style="background-color:rgba(245,158,11,0.1);color:#F59E0B;border-color:#F59E0B33;">🟡 Connecting...</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<span class="status-tag" style="background-color:rgba(239,68,68,0.1);color:#EF4444;border-color:#EF444433;">🔴 Connection Error</span>',
                    unsafe_allow_html=True,
                )
                err_key = st.session_state.get("connection_error", "general")
                st.error(st.session_state.prompt_manager.get_error_prompt(err_key))

            st.markdown("---")

            # Reset chat controls
            st.markdown("### 🧹 Chat Management")
            if st.button(
                "Clear Chat Button",
                key="clear_chat_btn",
                use_container_width=True,
                help="Clear current chat log and reset metrics",
            ):
                logger.info(
                    "UI: Clear Chat button clicked. Resetting history and metrics."
                )
                st.session_state[STATE_CHAT_HISTORY] = []
                st.session_state.conversation_count = 0
                st.session_state.connection_status = "Connecting..."
                st.session_state.connection_error = None
                st.success("Chat history cleared!")
                st.rerun()

            st.markdown("---")

            # About Section
            st.markdown("### ℹ️ About EduMentor AI")
            st.markdown(
                f"**Version:** {APP_VERSION}<br>"
                "**Developer:** Senior AI Engineer<br><br>"
                "EduMentor AI is a Socratic tutor that helps students build critical thinking skills "
                "by guiding them through concepts step-by-step.<br><br>"
                "**Future Features:**\n"
                "- PDF Upload and Syllabus loader\n"
                "- Socratic Agent planning\n"
                "- ChromaDB Vector Store & RAG",
                unsafe_allow_html=True,
            )

    def render_chat_window(self) -> None:
        """
        Renders the active chat log and processes user questions.
        If history is empty, shows the Greeting Prompt from PromptManager.
        """
        logger.debug("Rendering Chat Window component.")

        st.markdown("### 💬 Socratic Chat Workspace")

        # 1. Retrieve history from session state
        chat_history = st.session_state.get(STATE_CHAT_HISTORY, [])

        # If history is empty, display greeting from PromptManager
        if not chat_history:
            greeting = st.session_state.prompt_manager.get_greeting_prompt()
            with st.chat_message("assistant"):
                st.markdown(greeting)
        else:
            # Render historical messages
            for message in chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # 2. Check if chat input should be disabled (e.g. fatal config error like missing API key)
        connection_status = st.session_state.get("connection_status", "Connecting...")
        connection_error = st.session_state.get("connection_error")
        input_disabled = (
            connection_status == "Error" and connection_error == "missing_key"
        )

        if input_disabled:
            st.chat_input("Chat disabled due to missing Groq API Key.", disabled=True)
            return

        # 3. Capture user question
        if user_query := st.chat_input("Ask your Socratic Tutor a question..."):
            logger.info("UI: User message received: %s", user_query[:50])
            st.session_state[STATE_CHAT_HISTORY].append(
                {"role": "user", "content": user_query}
            )
            st.session_state.conversation_count += 1
            st.rerun()

        # 4. Generate assistant response if the last message is from the user
        if chat_history and chat_history[-1]["role"] == "user":
            user_msg = chat_history[-1]["content"]

            with st.chat_message("assistant"):
                with st.spinner("EduMentor AI is formulating a Socratic response..."):
                    try:
                        logger.info("UI: Requesting response from LLMClient.")
                        # Compile prompt instructions inside PromptManager (System + Tutor + User Question)
                        prompt_payload = (
                            st.session_state.prompt_manager.build_tutor_prompt(user_msg)
                        )

                        # Generate response through LLMClient
                        response = st.session_state.llm_client.generate_response(
                            system_instruction=prompt_payload["system"],
                            user_question=prompt_payload["user"],
                        )

                        # Save assistant response to session state
                        st.session_state[STATE_CHAT_HISTORY].append(
                            {"role": "assistant", "content": response}
                        )
                        logger.info(
                            "UI: Socratic response generated and stored in session state."
                        )

                    except Exception as e:
                        # Capture and map exception to friendly error key
                        err_key = str(e)
                        error_text = st.session_state.prompt_manager.get_error_prompt(
                            err_key
                        )

                        # Append the friendly error message to chat history to show it in context
                        st.session_state[STATE_CHAT_HISTORY].append(
                            {"role": "assistant", "content": error_text}
                        )
                        logger.error(
                            "UI: Generation failed with key %s: %s",
                            err_key,
                            str(e),
                            exc_info=True,
                        )

            # Rerun to render the assistant response or error message
            st.rerun()

    def render_footer(self) -> None:
        """
        Renders the application footer.
        """
        logger.debug("Rendering Footer component.")
        st.markdown(
            f"""
            <div class="footer-text">
                EduMentor AI v{APP_VERSION} &bull; Socratic Tutor Backend &bull; Designed by Senior AI Engineer
            </div>
            """,
            unsafe_allow_html=True,
        )
