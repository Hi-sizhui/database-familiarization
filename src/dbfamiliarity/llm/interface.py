from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LLMBackend(ABC):
    """Provider-neutral interface for frontier-model experiments."""

    @abstractmethod
    def complete(self, prompt: str, **kwargs: Any) -> str:
        raise NotImplementedError


class NotConfiguredBackend(LLMBackend):
    def complete(self, prompt: str, **kwargs: Any) -> str:
        raise RuntimeError(
            "No LLM backend is configured yet. Plug an OpenAI-compatible/local backend "
            "into this interface for model experiments."
        )
