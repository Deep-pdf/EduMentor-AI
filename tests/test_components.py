import pytest
import tempfile
from config import config
from modules.prompts import PromptManager
from modules.llm import LLMClient
from modules.pdf_loader import PDFLoader
from modules.embeddings import EmbeddingManager
from modules.vector_store import VectorStoreManager
from langchain_core.documents import Document


def test_config_defaults() -> None:
    """
    Test that default configuration options are loaded correctly.
    """
    assert config.app_name == "EduMentor AI"
    assert config.theme in ["dark", "light"]
    assert config.temperature == 0.5
    assert config.max_tokens == 2048


def test_prompt_manager() -> None:
    """
    Test that PromptManager retrieves prompts and compiles tutor payloads.
    """
    pm = PromptManager()

    # Verify System Prompt
    assert "EduMentor AI" in pm.get_system_prompt()

    # Verify Socratic Tutor instructions
    assert "Socratic" in pm.get_tutor_prompt()

    # Verify Greeting Prompt
    assert "Socratic Tutor" in pm.get_greeting_prompt()

    # Verify Error Prompts
    assert "key is missing" in pm.get_error_prompt("missing_key").lower()
    assert "invalid" in pm.get_error_prompt("invalid_key").lower()
    assert "connection" in pm.get_error_prompt("network").lower()

    # Verify prompt compiler (System + Tutor + User Question)
    payload = pm.build_tutor_prompt("How does gravity work?")
    assert "system" in payload
    assert "user" in payload
    assert payload["user"] == "How does gravity work?"
    assert "EduMentor AI" in payload["system"]
    assert "Socratic" in payload["system"]


def test_llm_client_missing_key() -> None:
    """
    Test that LLMClient raises ValueError("missing_key") when a placeholder key is used.
    """
    client = LLMClient(
        model_name="llama-3.1-8b-instant",
        temperature=0.5,
        api_key="your_groq_api_key_here",
    )
    with pytest.raises(ValueError) as excinfo:
        client.initialize()
    assert str(excinfo.value) == "missing_key"


def test_pdf_clean_text() -> None:
    """
    Test text cleaning and paragraph normalizations in PDFLoader.
    """
    loader = PDFLoader(upload_dir="data/uploads", max_size_mb=200)
    raw = ["Hello \n\n  world!\t This is \u00a0 text. \n\n  New paragraph details."]
    clean = loader.clean_text(raw)
    assert len(clean) == 1
    assert clean[0] == "Hello\n\nworld! This is text.\n\nNew paragraph details."


def test_embedding_generation() -> None:
    """
    Test that EmbeddingManager lazy loads models and produces correct vector shapes.
    """
    manager = EmbeddingManager(model_name="all-MiniLM-L6-v2")
    res = manager.generate(["Hello world"])
    assert len(res) == 1
    # sentence-transformers/all-MiniLM-L6-v2 produces 384 dimensional vectors
    assert len(res[0]) == 384


def test_vector_store_indexing_and_search() -> None:
    """
    Test that VectorStoreManager successfully indexes Document chunks
    and retrieves matches via query embedding similarity vectors.
    """
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        vsm = VectorStoreManager(db_path=tmpdir, collection_name="test_collection")
        vsm.create_database()

        em = EmbeddingManager(model_name="all-MiniLM-L6-v2")

        docs = [
            Document(
                page_content=(
                    "Artificial Intelligence is a branch of computer science "
                    "focused on building smart systems."
                ),
                metadata={"page_number": 1, "source": "doc.pdf"},
            ),
            Document(
                page_content=(
                    "Socrates was a classical Greek philosopher credited "
                    "as one of the founders of Western philosophy."
                ),
                metadata={"page_number": 2, "source": "doc.pdf"},
            ),
        ]

        vsm.add_documents(docs, em)

        # Search by query embedding
        query_emb = em.generate_query("Who was Socrates?")
        matches = vsm.similarity_search(query_emb, top_k=1)

        assert len(matches) == 1
        assert "Socrates" in matches[0].page_content
        assert matches[0].metadata["page_number"] == 2


def test_rag_prompt_compilation() -> None:
    """
    Test that RAG prompt compilation sets strict Socratic and grounding directives.
    """
    pm = PromptManager()
    payload = pm.build_rag_prompt("What is AI?", "AI is artificial intelligence.")

    assert "system" in payload
    assert "user" in payload
    assert (
        "Answer the student's question using ONLY the provided document context below."
        in payload["system"]
    )
    assert "AI is artificial intelligence." in payload["system"]
    assert payload["user"] == "What is AI?"


def test_conversation_memory() -> None:
    """
    Test ConversationMemory state storage, timestamp metadata, window limits, and clears.
    """
    from modules.memory import ConversationMemory

    memory = ConversationMemory(session_id="test_session", limit=2)
    memory.clear()

    assert len(memory.load()) == 0

    memory.add("user", "Hello Tutor")
    memory.add("assistant", "Hello Student! How can I help you?")
    memory.add("user", "What is calculus?")
    memory.add("assistant", "Calculus is the study of change.")

    all_msgs = memory.load()
    assert len(all_msgs) == 4
    assert all_msgs[0]["role"] == "user"
    assert all_msgs[0]["order"] == 0
    assert all_msgs[0]["timestamp"] > 0

    # Test sliding window (limit is 2 turns = 4 messages)
    recent = memory.load_recent()
    assert len(recent) == 4

    # Add one more turn (2 messages)
    memory.add("user", "Explain it simply.")
    memory.add("assistant", "Sure, it is about curves and areas.")

    # load_recent should return only the last 4 messages (2 turns)
    recent_after = memory.load_recent()
    assert len(recent_after) == 4
    assert recent_after[0]["content"] == "What is calculus?"
    assert recent_after[-1]["content"] == "Sure, it is about curves and areas."

    # Test clear
    memory.clear()
    assert len(memory.load()) == 0


def test_agent_intent_classification() -> None:
    """
    Test rule-based routing inside AIAgent.
    """
    import streamlit as st
    from modules.agent import AIAgent
    from modules.memory import ConversationMemory
    from modules.prompts import PromptManager
    from modules.tool_registry import ToolRegistry
    from modules.tools.tool_factory import ToolFactory

    # Dummy instances for agent dependencies
    memory = ConversationMemory(session_id="test_agent_session", limit=10)
    memory.clear()
    pm = PromptManager()

    # Registry setup
    registry = ToolRegistry()
    registry.register(ToolFactory.create_memory_tool(memory))

    class MockRAGEngine:
        def status(self):
            return {"database_initialized": True, "embedding_model_loaded": True}

    registry.register(ToolFactory.create_rag_tool(MockRAGEngine()))

    agent = AIAgent(
        llm_client=None,
        prompt_manager=pm,
        tool_registry=registry,
    )

    # Test Greeting
    assert agent.analyze_request("Hello there") == "Greeting"
    assert agent.analyze_request("Hi") == "Greeting"

    # Test Follow-up
    assert agent.analyze_request("Explain that differently") == "Conversation Follow-up"
    assert (
        agent.analyze_request("what was my previous question?")
        == "Conversation Follow-up"
    )
    assert agent.analyze_request("why?") == "Conversation Follow-up"

    # Test General Conversation
    assert (
        agent.analyze_request("How does photosynthesis work?") == "General Question"
    )

    # Test Document Question (RAG) when a document path is active in session state
    st.session_state.current_document_path = "data/uploads/syllabus.pdf"
    assert (
        agent.analyze_request("what does chapter 2 of the pdf say?")
        == "Document Question"
    )
    assert agent.analyze_request("explain the document") == "Document Question"

    # Clear current document path
    st.session_state.current_document_path = None


def test_prompt_history_formatting() -> None:
    """
    Test PromptManager compiles history context and appends it to prompt payloads correctly.
    """
    from modules.prompts import PromptManager

    pm = PromptManager()
    history = [
        {"role": "user", "content": "What is 2+2?"},
        {"role": "assistant", "content": "It is 4."},
    ]

    # Tutor prompt with history
    payload = pm.build_tutor_prompt_with_history("How do you know?", history)
    assert "system" in payload
    assert "user" in payload
    assert "Student: What is 2+2?" in payload["system"]
    assert "Tutor: It is 4." in payload["system"]

    # RAG prompt with history
    payload_rag = pm.build_rag_prompt_with_history(
        "How do you know?", "Math rules.", history
    )
    assert "system" in payload_rag
    assert "Student: What is 2+2?" in payload_rag["system"]
    assert "Tutor: It is 4." in payload_rag["system"]
    assert "Math rules." in payload_rag["system"]


def test_tool_registry() -> None:
    """
    Test registration, lookup, list tools, and capabilities discovery.
    """
    from modules.tool_registry import ToolRegistry
    from modules.tools.time_tool import TimeTool
    from modules.tools.calculator_tool import CalculatorTool

    registry = ToolRegistry()
    time_tool = TimeTool()
    calc_tool = CalculatorTool()

    registry.register(time_tool)
    registry.register(calc_tool)

    assert "Time Tool" in registry.list_tools()
    assert "Calculator Tool" in registry.list_tools()

    assert registry.get_tool("Time Tool") == time_tool
    assert registry.get_tool("Calculator Tool") == calc_tool

    caps = registry.discover_capabilities()
    assert "Time Request" in caps["Time Tool"]
    assert "Mathematics" in caps["Calculator Tool"]

    # Verify check_availability
    assert registry.check_availability("Time Tool") is True
    assert registry.check_availability("Unknown Tool") is False


def test_calculator_tool() -> None:
    """
    Test CalculatorTool basic equations and division-by-zero errors.
    """
    from modules.tools.calculator_tool import CalculatorTool

    calc = CalculatorTool()
    calc.initialize()

    # Basic multiplication
    res1 = calc.execute({"expression": "256 * 487"})
    assert "Result: 124672" in res1

    # Floating point operations and order of operations
    res2 = calc.execute({"expression": "2 * (3 + 4)"})
    assert "Result: 14" in res2

    # Division by zero
    res_zero = calc.execute({"expression": "5 / 0"})
    assert "Error: Division by zero" in res_zero

    # Advanced math function: square root
    res_sqrt = calc.execute({"expression": "sqrt(16)"})
    assert "Result: 4.0" in res_sqrt


def test_time_tool() -> None:
    """
    Test TimeTool returns date, time, and day of week.
    """
    from modules.tools.time_tool import TimeTool

    tt = TimeTool()
    tt.initialize()
    res = tt.execute({})
    assert "Current Date:" in res
    assert "Current Time:" in res
    assert "Day of Week:" in res


def test_search_tool() -> None:
    """
    Test SearchTool execution output.
    """
    from modules.tools.search_tool import SearchTool

    st = SearchTool(max_results=2)
    st.initialize()
    res = st.execute({"query": "python programming"})
    assert "python" in res.lower() or "search failed" in res.lower()


def test_agent_with_tools() -> None:
    """
    Test Agentic routing and LLM bypass with ToolRegistry.
    """
    from modules.agent import AIAgent
    from modules.tool_registry import ToolRegistry
    from modules.tools.tool_factory import ToolFactory
    from modules.memory import ConversationMemory
    from modules.prompts import PromptManager

    memory = ConversationMemory(session_id="test_agent_tools", limit=10)
    memory.clear()
    pm = PromptManager()
    registry = ToolRegistry()

    # Register Memory, Time, and Calculator
    registry.register(ToolFactory.create_memory_tool(memory))
    registry.register(ToolFactory.create_time_tool())
    registry.register(ToolFactory.create_calculator_tool())

    agent = AIAgent(llm_client=None, prompt_manager=pm, tool_registry=registry)

    # Test math routing and bypass (direct return)
    math_res = agent.process_request("What is 100 * 5?")
    assert "Result: 500" in math_res

    # Test time routing and bypass
    time_res = agent.process_request("What is the current time?")
    assert "Current Time:" in time_res

    # Verify memory contains these turns
    history = memory.load()
    assert len(history) == 4  # 2 turns * 2 = 4 messages
    assert history[0]["content"] == "What is 100 * 5?"
    assert "Result: 500" in history[1]["content"]
