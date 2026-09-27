from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from dbfamiliarity.llm.interface import LLMBackend


class OpenAICompatibleBackend(LLMBackend):
    """Minimal stdlib-only client for OpenAI-compatible chat APIs."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None,
                 model: str | None = None, timeout: int = 120) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
        self.model = model or os.getenv("OPENAI_MODEL")
        self.timeout = timeout
        if not self.api_key or not self.model:
            raise ValueError("OPENAI_API_KEY and OPENAI_MODEL are required")

    def complete(self, prompt: str, **kwargs: Any) -> str:
        body = {"model": self.model, "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get("temperature", 0)}
        req = urllib.request.Request(
            self.base_url + "/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"LLM HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"LLM connection failed: {exc}") from exc
        try:
            return payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected chat-completion response: {payload}") from exc
