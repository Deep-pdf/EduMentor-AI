import pytest
from config import config
from modules.prompts import PromptManager
from modules.llm import LLMClient


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
