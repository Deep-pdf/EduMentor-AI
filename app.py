"""
EduMentor AI Entrypoint
======================
Responsibility: Streamlit startup page configuration, session state 
initialization, and routing rendering to modules.ui components.
No logic/orchestration is carried out in this entrypoint.
"""

import streamlit as st
from config import config
from modules.logger import get_logger
from modules.constants import (
    APP_TITLE,
    STATE_SESSION_ID,
    STATE_CHAT_HISTORY,
    STATE_UPLOADED_PDFS,
    STATE_CONVERSATION_MEMORY,
    STATE_CURRENT_MODEL,
    STATE_CURRENT_TOOL,
    STATE_AGENT_STATUS
)
from modules import (
    UIController,
    LLMClient,
    PromptManager,
    RAGEngine,
    ConversationMemory,
    ToolManager,
    AIAgent,
    PDFLoader,
    EmbeddingManager,
    VectorStoreManager
)

# Initialize application logger
logger = get_logger("app", log_level=config.log_level)


def init_state() -> None:
    """
    Bootstrap Streamlit session state keys with empty/placeholder values.
    """
    logger.info("Initializing Streamlit session states.")
    
    if STATE_SESSION_ID not in st.session_state:
        st.session_state[STATE_SESSION_ID] = "student_session_001"
    
    if STATE_CHAT_HISTORY not in st.session_state:
        st.session_state[STATE_CHAT_HISTORY] = []
        
    if STATE_UPLOADED_PDFS not in st.session_state:
        st.session_state[STATE_UPLOADED_PDFS] = []

    # Initialize architectural components placeholders
    if "embedding_manager" not in st.session_state:
        st.session_state.embedding_manager = EmbeddingManager(config.embedding_model_name)
        
    if "vector_store_manager" not in st.session_state:
        st.session_state.vector_store_manager = VectorStoreManager(config.chroma_db_path, "default")
        
    if STATE_CONVERSATION_MEMORY not in st.session_state:
        st.session_state[STATE_CONVERSATION_MEMORY] = ConversationMemory(st.session_state[STATE_SESSION_ID])
        
    if "pdf_loader" not in st.session_state:
        st.session_state.pdf_loader = PDFLoader(config.chroma_db_path, config.max_upload_size_mb)
        
    if "llm_client" not in st.session_state:
        st.session_state.llm_client = LLMClient(config.model_name, config.temperature)
        
    if "prompt_manager" not in st.session_state:
        st.session_state.prompt_manager = PromptManager()
        
    if "rag_engine" not in st.session_state:
        st.session_state.rag_engine = RAGEngine(st.session_state.vector_store_manager, st.session_state.embedding_manager)
        
    if "tool_manager" not in st.session_state:
        st.session_state.tool_manager = ToolManager()
        
    if "agent" not in st.session_state:
        st.session_state.agent = AIAgent(
            st.session_state.llm_client,
            st.session_state.prompt_manager,
            st.session_state[STATE_CONVERSATION_MEMORY],
            st.session_state.rag_engine,
            st.session_state.tool_manager
        )

    # Tracking metrics
    if STATE_CURRENT_MODEL not in st.session_state:
        st.session_state[STATE_CURRENT_MODEL] = config.model_name
        
    if STATE_CURRENT_TOOL not in st.session_state:
        st.session_state[STATE_CURRENT_TOOL] = "None"
        
    if STATE_AGENT_STATUS not in st.session_state:
        st.session_state[STATE_AGENT_STATUS] = "Project Architecture Initialized"


def main() -> None:
    """
    Main application entrypoint.
    """
    # Page setup
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🎓",
        layout="wide"
    )

    # Run state configurations
    init_state()

    # Instantiate and draw visual layout
    ui = UIController()
    ui.inject_custom_styles()
    ui.render_header()
    ui.render_sidebar()
    ui.render_chat_window()
    ui.render_footer()
    
    logger.info("UI rendered successfully. Application waiting for interactions.")


if __name__ == "__main__":
    main()
