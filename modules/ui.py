"""
EduMentor AI UI Module
======================

This module is responsible for rendering all Streamlit UI components.
It abstracts rendering logic for the Header, Sidebar, Chat Window, and Footer
to enforce separation of concerns, and binds UI interactions directly to the
AIAgent orchestrator instead of exposing individual subsystem layers.
"""

import streamlit as st
from modules.constants import (
    APP_SUBTITLE,
    APP_VERSION,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_TEXT_MUTED,
    DIR_UPLOADS,
)
from modules.logger import get_logger

logger = get_logger(__name__)


class UIController:
    """
    Renders Streamlit layout components for the EduMentor AI application interface.
    Coordinates interaction logic exclusively through the central AIAgent orchestrator.
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
        Handles PDF uploading, active document metadata, and database cleaning triggers.
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

            # PDF Upload Section
            st.markdown("### 📂 Study Material")
            uploaded_file = st.file_uploader(
                "Upload Syllabus/PDF",
                type=["pdf"],
                help="Upload a PDF file to enable document-grounded Socratic tutoring.",
            )

            if uploaded_file is not None:
                # Check if it is a new file or needs processing
                if st.session_state.get("current_document_name") != uploaded_file.name:
                    logger.info(
                        "PDF Uploaded: Received new document upload: %s",
                        uploaded_file.name,
                    )

                    # 1. Upload and save the PDF file copy locally
                    with st.spinner("Processing PDF..."):
                        try:
                            from modules.pdf_loader import PDFLoader

                            loader = PDFLoader(
                                upload_dir=DIR_UPLOADS,
                                max_size_mb=config.max_upload_size_mb,
                            )
                            saved_path = loader.upload(uploaded_file)

                            st.session_state.current_document_name = uploaded_file.name
                            st.session_state.current_document_path = saved_path
                            logger.info(
                                "PDF Loaded: Upload file copy saved to %s", saved_path
                            )
                        except Exception as e:
                            st.error(f"Failed to process PDF: {str(e)}")
                            logger.error(
                                "UI: PDF upload processing failed: %s",
                                str(e),
                                exc_info=True,
                            )
                            st.session_state.current_document_name = None
                            st.session_state.current_document_path = None
                            st.rerun()

                    # 2. Extract, chunk, generate embeddings, and insert in ChromaDB
                    if st.session_state.get("current_document_path"):
                        with st.spinner("Generating embeddings..."):
                            try:
                                res = st.session_state.rag_engine.process_document(
                                    st.session_state.current_document_path
                                )
                                st.session_state.current_document_metadata = res
                                st.success(f"Processed: {uploaded_file.name}")
                                logger.info(
                                    "UI: Document indexed. Status: %s",
                                    res.get("status"),
                                )
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to generate embeddings: {str(e)}")
                                logger.error(
                                    "UI: Embedding generation/indexing failed: %s",
                                    str(e),
                                    exc_info=True,
                                )
                                st.session_state.current_document_name = None
                                st.session_state.current_document_path = None
                                st.rerun()
            else:
                # If uploader is empty but we have an active document name, the user removed it!
                if st.session_state.get("current_document_name") is not None:
                    logger.info(
                        "UI: Active PDF removed by user. Wiping ChromaDB collection."
                    )
                    try:
                        st.session_state.rag_engine.clear_database()
                    except Exception as e:
                        logger.error(
                            "UI: Failed to clear ChromaDB on file removal: %s", str(e)
                        )
                    st.session_state.current_document_name = None
                    st.session_state.current_document_path = None
                    st.session_state.current_document_metadata = None
                    st.info("Study material removed. Vector store cleared.")
                    st.rerun()

            # Active Document details display
            if st.session_state.get("current_document_name"):
                st.markdown("### 📄 Active Document")
                meta = st.session_state.get("current_document_metadata", {})
                pages = meta.get("total_pages", "Unknown")
                chunks = meta.get("total_chunks", "Unknown")
                st.markdown(
                    f"**File:** `{st.session_state.current_document_name}`  \n"
                    f"**Pages:** {pages} &bull; **Chunks:** {chunks}"
                )

            st.markdown("---")

            # System Connection and RAG Status Section
            st.markdown("### ⚙️ System Status")
            status = st.session_state.get("connection_status", "Connecting...")

            if status == "Connected":
                st.markdown(
                    '<span class="status-tag" style="background-color:'
                    "rgba(16,185,129,0.1);color:#10B981;"
                    'border-color:#10B98133;">🟢 Connected to Groq</span>',
                    unsafe_allow_html=True,
                )
            elif status == "Connecting...":
                st.markdown(
                    '<span class="status-tag" style="background-color:'
                    "rgba(245,158,11,0.1);color:#F59E0B;"
                    'border-color:#F59E0B33;">🟡 Connecting...</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<span class="status-tag" style="background-color:'
                    "rgba(239,68,68,0.1);color:#EF4444;"
                    'border-color:#EF444433;">🔴 Connection Error</span>',
                    unsafe_allow_html=True,
                )
                err_key = st.session_state.get("connection_error", "general")
                st.error(st.session_state.prompt_manager.get_error_prompt(err_key))

            # Display RAG database status
            rag_status = st.session_state.rag_engine.status()
            db_init = "Ready" if rag_status.get("database_initialized") else "Offline"
            model_loaded = (
                "Loaded" if rag_status.get("embedding_model_loaded") else "Pending"
            )

            st.markdown(
                f"- **Vector Store:** `{db_init}`  \n"
                f"- **Embeddings:** `{model_loaded}`",
                unsafe_allow_html=True,
            )

            st.markdown("---")

            # Web Search & Think Mode Options
            st.markdown("### 🔍 Agent Settings")
            st.checkbox(
                "Enable Web Search",
                key="web_search_enabled",
                value=True,
                help="Allow the tutor to search the web for current events/news.",
            )
            st.checkbox(
                "Force Web Search",
                key="force_web_search",
                value=False,
                help="Force the agent to query the web search tool for the next question.",
            )
            st.checkbox(
                "🧠 Think Mode",
                key="think_mode_enabled",
                value=False,
                help="Instructs the AI agent to perform deep reasoning before formulating its response.",
            )

            st.markdown("---")

            # Reset chat controls
            st.markdown("### 🧹 Chat Management")
            if st.button(
                "Clear Chat Button",
                key="clear_chat_btn",
                use_container_width=True,
                help="Clear current chat log and wipe vector store collections",
            ):
                logger.info(
                    "UI: Clear Chat button clicked. Resetting history, memory, and database."
                )
                st.session_state.conversation_count = 0
                st.session_state.connection_status = "Connecting..."
                st.session_state.connection_error = None

                # Wipe persistent database collections and agent session memory
                try:
                    st.session_state.memory.clear()
                    st.session_state.rag_engine.clear_database()
                    logger.info("UI: Vector collection and memory wiped successfully.")
                except Exception as e:
                    logger.error("UI: Failed to clear database/memory: %s", str(e))

                st.session_state.current_document_name = None
                st.session_state.current_document_path = None
                st.session_state.current_document_metadata = None

                st.success("Chat history and vector store cleared!")
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
                "- Socratic Agent planning\n"
                "- Multiple document library loading",
                unsafe_allow_html=True,
            )

    def render_chat_window(self) -> None:
        """
        Renders the active chat log and processes user questions.
        All requests are routed through the central AI Agent.
        """
        logger.debug("Rendering Chat Window component.")

        st.markdown("### 💬 Socratic Chat Workspace")

        # 1. Retrieve history from Agent Memory (single source of truth)
        chat_history = st.session_state.memory.load()

        # If history is empty, display greeting from PromptManager
        if not chat_history:
            greeting = st.session_state.prompt_manager.get_greeting_prompt()
            with st.chat_message("assistant"):
                st.markdown(greeting)
        else:
            # Render historical messages
            for message in chat_history:
                with st.chat_message(message["role"]):
                    content = message["content"]
                    if "<thinking>" in content and "</thinking>" in content:
                        parts = content.split("</thinking>", 1)
                        thinking_text = parts[0].replace("<thinking>", "").strip()
                        answer_text = parts[1].strip()
                        with st.expander("🧠 Tutor's Thought Process", expanded=False):
                            st.markdown(thinking_text)
                        st.markdown(answer_text)
                    elif "<thinking>" in content:
                        parts = content.split("<thinking>", 1)
                        pre_thinking = parts[0].strip()
                        if pre_thinking:
                            st.markdown(pre_thinking)
                        thinking_text = parts[1].strip()
                        with st.expander("🧠 Tutor's Thought Process", expanded=True):
                            st.markdown(thinking_text)
                    else:
                        st.markdown(content)

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
            st.session_state.memory.add("user", user_query)
            st.session_state.conversation_count += 1
            st.rerun()

        # 4. Generate assistant response if the last message is from the user
        if chat_history and chat_history[-1]["role"] == "user":
            user_msg = chat_history[-1]["content"]

            with st.chat_message("assistant"):
                with st.spinner("EduMentor AI is formulating a response..."):
                    try:
                        logger.info("UI: Requesting response from AI Agent.")
                        # Route request to central AI Agent
                        st.session_state.agent.process_request(user_msg)
                        logger.info("UI: AI Agent execution completed.")
                    except Exception as e:
                        # Capture and map exception to friendly error key
                        err_key = str(e)
                        error_text = st.session_state.prompt_manager.get_error_prompt(
                            err_key
                        )

                        # Save the friendly error message to memory
                        st.session_state.memory.add("assistant", error_text)
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
