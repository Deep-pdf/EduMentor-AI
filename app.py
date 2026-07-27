"""
EduMentor AI Entrypoint
======================
Responsibility: Streamlit startup page configuration, session state
initialization, connection bootstrapping, and rendering UI components.
No database or planning orchestration is carried out in this entrypoint.
"""

import streamlit as st
import datetime
import atexit
from config import config
from modules.logger import get_logger
from modules.constants import APP_TITLE, STATE_CHAT_HISTORY, STATE_CURRENT_MODEL
from modules import (
    UIController,
    LLMClient,
    PromptManager,
    EmbeddingManager,
    VectorStoreManager,
    RAGEngine,
    ConversationMemory,
    AIAgent,
    ToolManager,
    ToolRegistry,
)

# Initialize application logger
logger = get_logger("app", log_level=config.log_level)
logger.info("Application Started.")


@atexit.register
def log_shutdown() -> None:
    """
    Log application closing event when the server process is terminated.
    """
    logger.info("Application Closed.")


def init_state() -> None:
    """
    Bootstrap Streamlit session state keys with required Phase 2 parameters.
    """
    logger.info("Initializing Streamlit session states.")

    # 1. Session start time tracking
    if "session_start_time" not in st.session_state:
        st.session_state.session_start_time = datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    # 2. Conversation query counter
    if "conversation_count" not in st.session_state:
        st.session_state.conversation_count = 0

    # 3. Model state key
    if STATE_CURRENT_MODEL not in st.session_state:
        st.session_state[STATE_CURRENT_MODEL] = config.model_name

    # 4. Chat history (UI history list)
    if STATE_CHAT_HISTORY not in st.session_state:
        st.session_state[STATE_CHAT_HISTORY] = []

    # 5. Core modules
    if "prompt_manager" not in st.session_state:
        st.session_state.prompt_manager = PromptManager()

    # Initialize or recreate LLMClient if model changed in .env
    if (
        "llm_client" not in st.session_state
        or st.session_state.llm_client.model_name != config.model_name
    ):
        logger.info(
            "Model Loaded: Instantiating LLMClient for model: %s", config.model_name
        )
        st.session_state.llm_client = LLMClient(config.model_name, config.temperature)
        st.session_state.connection_status = "Connecting..."
        st.session_state.connection_error = None

    # 6. RAG Component Pipeline
    if "embedding_manager" not in st.session_state:
        logger.info("Main: Initializing EmbeddingManager...")
        st.session_state.embedding_manager = EmbeddingManager(
            config.embedding_model_name
        )
        # Load the sentence transformer model into memory
        st.session_state.embedding_manager.load_model()

    if "vector_store_manager" not in st.session_state:
        logger.info("Main: Initializing VectorStoreManager...")
        st.session_state.vector_store_manager = VectorStoreManager(
            config.chroma_db_path, config.collection_name
        )
        st.session_state.vector_store_manager.create_database()

    if "rag_engine" not in st.session_state:
        logger.info("Main: Initializing RAGEngine...")
        st.session_state.rag_engine = RAGEngine(
            st.session_state.vector_store_manager, st.session_state.embedding_manager
        )
        st.session_state.rag_engine.initialize()

    # 7. Document States
    if "current_document_name" not in st.session_state:
        st.session_state.current_document_name = None
    if "current_document_path" not in st.session_state:
        st.session_state.current_document_path = None
    if "current_document_metadata" not in st.session_state:
        st.session_state.current_document_metadata = None

    # 8. Memory State
    if "memory" not in st.session_state:
        st.session_state.memory = ConversationMemory(session_id="default", limit=10)

    # 9. Tool Manager
    if "tool_manager" not in st.session_state:
        st.session_state.tool_manager = ToolManager()

    # 10. Tool Registry & Core Tools registration
    if "tool_registry" not in st.session_state:
        logger.info("Main: Initializing ToolRegistry and registering core tools...")
        from modules.tools.tool_factory import ToolFactory

        registry = ToolRegistry()

        # Register Memory Tool
        registry.register(ToolFactory.create_memory_tool(st.session_state.memory))

        # Register RAG Tool
        registry.register(ToolFactory.create_rag_tool(st.session_state.rag_engine))

        # Register Search Tool
        registry.register(ToolFactory.create_search_tool())

        # Register Calculator Tool
        registry.register(ToolFactory.create_calculator_tool())

        # Register Time Tool
        registry.register(ToolFactory.create_time_tool())

        st.session_state.tool_registry = registry
        logger.info("Main: All core tools registered successfully.")

    # 11. Agent Orchestrator
    if "agent" not in st.session_state:
        st.session_state.agent = AIAgent(
            llm_client=st.session_state.llm_client,
            prompt_manager=st.session_state.prompt_manager,
            tool_registry=st.session_state.tool_registry,
        )
        st.session_state.agent.initialize()


def init_llm_connection() -> None:
    """
    Attempt to initialize the LLM Client connection at startup.
    Saves connection results (Connected, Error) to session state.
    """
    if "connection_status" not in st.session_state:
        st.session_state.connection_status = "Connecting..."
        st.session_state.connection_error = None

    if st.session_state.connection_status == "Connecting...":
        logger.info("Main: Attempting startup connection to Groq API.")
        try:
            st.session_state.llm_client.initialize()
            st.session_state.connection_status = "Connected"
            logger.info(
                "Groq Initialized: Startup connection successful. Groq is Connected."
            )
        except Exception as e:
            error_key = str(e)
            st.session_state.connection_status = "Error"
            st.session_state.connection_error = error_key
            logger.error("Main: Startup connection failed: %s", error_key)


def main() -> None:
    """
    Main application entrypoint.
    """
    # Page setup
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🎓",
        layout="wide",
        # Theme is handled dynamically inside our inject_custom_styles css overrides
    )

    # Bootstrapping configurations and state
    init_state()

    # Check LLM connection status
    init_llm_connection()

    # Draw visual components using UIController
    ui = UIController()
    ui.inject_custom_styles()
    ui.render_header()
    ui.render_sidebar()
    ui.render_chat_window()
    ui.render_footer()

    logger.debug("UI rendered successfully. Application waiting for interactions.")


if __name__ == "__main__":
    main()
