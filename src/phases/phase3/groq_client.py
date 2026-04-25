from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib import request

from src.phases.phase1.settings import Settings


@dataclass(frozen=True)
class GroqResponse:
    text: str
    raw: dict[str, Any]


class GroqClient:
    def __init__(self, settings: Settings, timeout_seconds: int = 30) -> None:
        if not settings.llm_api_key:
            raise ValueError("LLM_API_KEY is required for Groq client")
        self._api_key = settings.llm_api_key
        self._model = settings.llm_model
        self._timeout_seconds = timeout_seconds
        self._endpoint = "https://api.groq.com/openai/v1/chat/completions"

    @property
    def model(self) -> str:
        return self._model

    def chat(self, user_prompt: str, system_prompt: str = "You are a helpful assistant.") -> GroqResponse:
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
        }
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self._endpoint,
            data=body,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with request.urlopen(req, timeout=self._timeout_seconds) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        text = data["choices"][0]["message"]["content"]
        return GroqResponse(text=text, raw=data)
