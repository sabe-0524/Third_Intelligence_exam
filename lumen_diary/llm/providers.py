from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from ..config import LLMConfig
from .base import LLMClient, LLMRequest, LLMResult


class LLMProviderError(RuntimeError):
    """Raised when an LLM provider cannot produce a result."""


@dataclass
class StubLLMClient(LLMClient):
    model: str = "stub-v1"
    provider: str = "stub"

    def generate(self, request: LLMRequest) -> LLMResult:
        prompt = "\n\n".join(message.content for message in request.messages)
        if request.response_format == "json":
            text = json.dumps(
                {
                    "provider": self.provider,
                    "model": self.model,
                    "summary": prompt[:120],
                    "mode": "stub-json",
                },
                ensure_ascii=False,
                indent=2,
            )
        else:
            text = (
                "This is a stub LLM response.\n\n"
                f"System prompt: {request.system_prompt[:120]}\n"
                f"User prompt: {prompt[:240]}"
            )
        return LLMResult(text=text, provider=self.provider, model=self.model, raw_response={"stub": True})


@dataclass(kw_only=True)
class HTTPJSONLLMClient(LLMClient):
    provider: str
    model: str
    api_key: str
    timeout_seconds: float = 30.0

    def _headers(self) -> dict[str, str]:
        return {"Content-Type": "application/json"}

    def _url(self) -> str:
        raise NotImplementedError

    def _payload(self, request: LLMRequest) -> dict[str, Any]:
        raise NotImplementedError

    def _extract_text(self, response_json: dict[str, Any]) -> str:
        raise NotImplementedError

    def generate(self, request: LLMRequest) -> LLMResult:
        payload = json.dumps(self._payload(request), ensure_ascii=False).encode("utf-8")
        http_request = urllib.request.Request(
            self._url(),
            data=payload,
            headers=self._headers(),
            method="POST",
        )
        try:
            with urllib.request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as error:  # pragma: no cover - network path
            body = error.read().decode("utf-8", errors="replace")
            raise LLMProviderError(f"{self.provider} request failed: {error.code} {body}") from error
        except urllib.error.URLError as error:  # pragma: no cover - network path
            raise LLMProviderError(f"{self.provider} request failed: {error.reason}") from error

        response_json = json.loads(raw)
        return LLMResult(
            text=self._extract_text(response_json),
            provider=self.provider,
            model=self.model,
            raw_response=response_json,
        )


def _gemini_message_role(role: str) -> str:
    if role == "assistant":
        return "model"
    return "user"


def _gemini_message_text(role: str, content: str) -> str:
    if role in {"user", "assistant"}:
        return content
    return f"[{role}]\n{content}"


@dataclass(kw_only=True)
class GeminiLLMClient(HTTPJSONLLMClient):
    provider: str = "gemini"

    def _headers(self) -> dict[str, str]:
        return {"Content-Type": "application/json"}

    def _url(self) -> str:
        return f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def _payload(self, request: LLMRequest) -> dict[str, Any]:
        return {
            "systemInstruction": {
                "parts": [{"text": request.system_prompt}],
            },
            "contents": [
                {
                    "role": _gemini_message_role(message.role),
                    "parts": [{"text": _gemini_message_text(message.role, message.content)}],
                }
                for message in request.messages
            ],
            "generationConfig": {
                "temperature": request.temperature,
                "responseMimeType": "application/json" if request.response_format == "json" else "text/plain",
            },
        }

    def _extract_text(self, response_json: dict[str, Any]) -> str:
        candidates = response_json.get("candidates", [])
        if not candidates:
            raise LLMProviderError("gemini returned no candidates")
        parts = candidates[0].get("content", {}).get("parts", [])
        texts = [part.get("text", "") for part in parts if part.get("text")]
        if not texts:
            raise LLMProviderError("gemini returned no text parts")
        return "\n".join(texts)


@dataclass(kw_only=True)
class OpenAILLMClient(HTTPJSONLLMClient):
    provider: str = "openai"
    base_url: str = "https://api.openai.com/v1/responses"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _url(self) -> str:
        return self.base_url

    def _payload(self, request: LLMRequest) -> dict[str, Any]:
        input_items: list[dict[str, Any]] = []
        if request.system_prompt:
            input_items.append(
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": request.system_prompt}],
                }
            )
        for message in request.messages:
            input_items.append(
                {
                    "role": message.role,
                    "content": [{"type": "input_text", "text": message.content}],
                }
            )
        payload: dict[str, Any] = {
            "model": self.model,
            "input": input_items,
            "temperature": request.temperature,
        }
        if request.response_format == "json":
            payload["text"] = {"format": {"type": "json_object"}}
        return payload

    def _extract_text(self, response_json: dict[str, Any]) -> str:
        output = response_json.get("output", [])
        texts: list[str] = []
        for item in output:
            for content in item.get("content", []):
                if content.get("type") in {"output_text", "text"} and content.get("text"):
                    texts.append(content["text"])
        if not texts:
            raise LLMProviderError("openai returned no text output")
        return "\n".join(texts)


def build_llm_client(config: LLMConfig) -> LLMClient:
    provider = config.provider.lower()
    if provider == "stub":
        return StubLLMClient(model=config.model)
    if provider == "gemini":
        if not config.api_key:
            raise LLMProviderError("Gemini provider requires LUMEN_LLM_API_KEY.")
        return GeminiLLMClient(model=config.model, api_key=config.api_key, timeout_seconds=config.timeout_seconds)
    if provider == "openai":
        if not config.api_key:
            raise LLMProviderError("OpenAI provider requires LUMEN_LLM_API_KEY.")
        base_url = config.base_url or "https://api.openai.com/v1/responses"
        return OpenAILLMClient(
            model=config.model,
            api_key=config.api_key,
            timeout_seconds=config.timeout_seconds,
            base_url=base_url,
        )
    raise LLMProviderError(f"Unsupported LLM provider: {config.provider}")
