from __future__ import annotations

import argparse

from .config import load_config
from .llm import build_llm_client
from .llm.providers import LLMProviderError
from .narration import build_diary_narrator
from .pipeline import WeeklyDiaryPipeline
from .rendering import DiaryRenderer
from .storage import RunStorage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lumen-diary",
        description="Generate a seven-day diary from a multi-agent library world simulation.",
    )
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run the diary generation pipeline.")
    run_parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Directory where generated runs are written.",
    )
    run_parser.add_argument(
        "--provider",
        default=None,
        help="LLM provider override. One of: stub, gemini, openai.",
    )
    run_parser.add_argument(
        "--model",
        default=None,
        help="Model name override for the configured provider.",
    )
    run_parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Deterministic seed for the weekly run.",
    )
    return parser


def _run_bootstrap(*, output_dir: str, provider: str | None, model: str | None, seed: int) -> int:
    config = load_config(output_dir=output_dir, provider=provider, model=model, seed=seed)
    config.output_dir.mkdir(parents=True, exist_ok=True)
    try:
        llm_client = build_llm_client(config.llm)
        narrator = build_diary_narrator(llm_client)
    except LLMProviderError as error:
        print(f"LLM initialization failed, falling back to rule-based narration: {error}")
        from .narration import RuleBasedDiaryNarrator

        narrator = RuleBasedDiaryNarrator()
    pipeline = WeeklyDiaryPipeline(
        storage=RunStorage(config.output_dir),
        renderer=DiaryRenderer(),
        narrator=narrator,
    )
    week_plan, _ = pipeline.run_week(config.seed)
    run_dir = config.output_dir / week_plan.week_run_id
    print(f"Generated run: {run_dir}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "run":
        return _run_bootstrap(
            output_dir=args.output_dir,
            provider=args.provider,
            model=args.model,
            seed=args.seed,
        )

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
