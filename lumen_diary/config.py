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


def _load_dotenv(root: Path) -> dict[str, str]:
    dotenv_path = root / ".env"
    if not dotenv_path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


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
    dotenv_values = _load_dotenv(root)

    def env_value(key: str) -> str | None:
        return os.getenv(key) or dotenv_values.get(key)

    env_provider = env_value("LUMEN_LLM_PROVIDER")
    selected_provider = (provider or env_provider or "stub").lower()
    env_model = env_value("LUMEN_LLM_MODEL")
    selected_model = model or (env_model if (provider is not None or env_provider is not None) else None) or _default_model_for(selected_provider)
    llm = LLMConfig(
        provider=selected_provider,
        model=selected_model,
        api_key=env_value("LUMEN_LLM_API_KEY"),
        base_url=env_value("LUMEN_LLM_BASE_URL"),
        temperature=float(env_value("LUMEN_LLM_TEMPERATURE") or "0.2"),
        timeout_seconds=float(env_value("LUMEN_LLM_TIMEOUT_SECONDS") or "30"),
    )
    return AppConfig(
        root_dir=root,
        output_dir=_resolve_output_dir(root, output_dir),
        llm=llm,
        seed=seed if seed is not None else int(env_value("LUMEN_SEED") or "42"),
    )
