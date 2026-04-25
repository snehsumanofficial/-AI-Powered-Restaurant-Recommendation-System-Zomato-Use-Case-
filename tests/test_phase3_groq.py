import os

import pytest

from src.phases.phase1.settings import load_settings
from src.phases.phase3.groq_client import GroqClient


def test_groq_client_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.setenv("LLM_MODEL", "llama-3.3-70b-versatile")
    settings = load_settings()
    with pytest.raises(ValueError):
        GroqClient(settings)


def test_groq_client_uses_configured_model() -> None:
    settings = load_settings()
    if not settings.llm_api_key:
        pytest.skip("LLM_API_KEY not set")
    client = GroqClient(settings)
    assert settings.llm_model
    assert client.model == settings.llm_model


def test_groq_live_chat_connection() -> None:
    settings = load_settings()
    if not settings.llm_api_key:
        pytest.skip("LLM_API_KEY not set")
    if os.getenv("RUN_GROQ_LIVE", "1") != "1":
        pytest.skip("Live Groq test disabled")
    client = GroqClient(settings, timeout_seconds=45)
    response = client.chat("Reply with exactly: GROQ_OK")
    assert isinstance(response.text, str)
    assert len(response.text.strip()) > 0
