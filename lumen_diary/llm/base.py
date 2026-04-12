from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


class StructuredOutputError(ValueError):
    """Raised when a provider response cannot be parsed into structured output."""

    def __init__(self, message: str, *, raw_text: str, provider: str, model: str) -> None:
        super().__init__(message)
        self.raw_text = raw_text
        self.provider = provider
        self.model = model


@dataclass(frozen=True)
class LLMMessage:
    role: str
    content: str


@dataclass(frozen=True)
class LLMRequest:
    system_prompt: str
    messages: list[LLMMessage]
    temperature: float = 0.2
    response_format: str = "text"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LLMResult:
    text: str
    provider: str
    model: str
    raw_response: dict[str, Any] | None = None

    def json_object(self) -> dict[str, Any]:
        try:
            return json.loads(self.text)
        except json.JSONDecodeError as error:
            raise StructuredOutputError(
                "Provider response was not valid JSON.",
                raw_text=self.text,
                provider=self.provider,
                model=self.model,
            ) from error


class LLMClient(ABC):
    provider: str
    model: str

    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResult:
        raise NotImplementedError

    def generate_text(self, system_prompt: str, user_prompt: str, *, temperature: float = 0.2) -> LLMResult:
        request = LLMRequest(
            system_prompt=system_prompt,
            messages=[LLMMessage(role="user", content=user_prompt)],
            temperature=temperature,
        )
        return self.generate(request)

    def generate_json(self, system_prompt: str, user_prompt: str, *, temperature: float = 0.1) -> dict[str, Any]:
        request = LLMRequest(
            system_prompt=system_prompt,
            messages=[LLMMessage(role="user", content=user_prompt)],
            temperature=temperature,
            response_format="json",
        )
        return self.generate(request).json_object()
