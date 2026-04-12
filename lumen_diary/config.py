from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LLMConfig:
    provider: str = "stub"
    model: str = "stub-v1"
    api_key: str | None = None
    base_url: str | None = None
    temperature: float = 0.2
    timeout_seconds: float = 30.0


@dataclass(frozen=True)
class AppConfig:
    root_dir: Path
    output_dir: Path
    llm: LLMConfig
    seed: int = 42


def _default_model_for(provider: str) -> str:
    defaults = {
        "stub": "stub-v1",
        "gemini": "gemini-2.5-flash",
        "openai": "gpt-4.1-mini",
    }
    return defaults.get(provider, "stub-v1")


def _resolve_output_dir(root: Path, output_dir: str | Path | None) -> Path:
    candidate = Path(output_dir or os.getenv("LUMEN_OUTPUT_DIR") or "outputs")
    if not candidate.is_absolute():
        candidate = root / candidate
    return candidate.resolve()


def load_config(
    *,
    root_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
    provider: str | None = None,
    model: str | None = None,
    seed: int | None = None,
) -> AppConfig:
    root = Path(root_dir or os.getenv("LUMEN_ROOT_DIR") or Path.cwd()).resolve()
    selected_provider = (provider or os.getenv("LUMEN_LLM_PROVIDER") or "stub").lower()
    selected_model = model or os.getenv("LUMEN_LLM_MODEL") or _default_model_for(selected_provider)
    llm = LLMConfig(
        provider=selected_provider,
        model=selected_model,
        api_key=os.getenv("LUMEN_LLM_API_KEY"),
        base_url=os.getenv("LUMEN_LLM_BASE_URL"),
        temperature=float(os.getenv("LUMEN_LLM_TEMPERATURE", "0.2")),
        timeout_seconds=float(os.getenv("LUMEN_LLM_TIMEOUT_SECONDS", "30")),
    )
    return AppConfig(
        root_dir=root,
        output_dir=_resolve_output_dir(root, output_dir),
        llm=llm,
        seed=seed if seed is not None else int(os.getenv("LUMEN_SEED", "42")),
    )
