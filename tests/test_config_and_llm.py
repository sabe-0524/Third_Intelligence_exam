from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from lumen_diary.config import load_config
from lumen_diary.llm import StructuredOutputError, build_llm_client
from lumen_diary.llm.providers import LLMProviderError
from lumen_diary.cli import main
from lumen_diary.llm.base import LLMMessage, LLMRequest
from lumen_diary.llm.providers import GeminiLLMClient


class ConfigAndLLMTests(unittest.TestCase):
    def test_load_config_uses_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = load_config(root_dir=tmpdir, output_dir="outputs")
        self.assertEqual(config.llm.provider, "stub")
        self.assertEqual(config.llm.model, "stub-v1")
        self.assertEqual(config.seed, 42)

    def test_stub_llm_returns_json_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = load_config(root_dir=tmpdir, output_dir="outputs", provider="stub")
        client = build_llm_client(config.llm)
        payload = client.generate_json("system", "user prompt")
        self.assertEqual(payload["provider"], "stub")
        self.assertEqual(payload["mode"], "stub-json")

    def test_provider_factory_requires_key_for_network_providers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = load_config(root_dir=tmpdir, output_dir="outputs", provider="gemini")
            with self.assertRaises(LLMProviderError):
                build_llm_client(config.llm)

    def test_stub_text_generation_mentions_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = load_config(root_dir=tmpdir, output_dir="outputs", provider="stub")
        client = build_llm_client(config.llm)
        result = client.generate_text("sys", "hello world")
        self.assertIn("hello world", result.text)

    def test_output_dir_is_resolved_from_root_dir(self) -> None:
        config = load_config(root_dir="/tmp/lumen-root", output_dir="nested/outputs", provider="stub")
        self.assertEqual(config.output_dir, Path("/tmp/lumen-root/nested/outputs").resolve())

    def test_invalid_json_raises_structured_output_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = load_config(root_dir=tmpdir, output_dir="outputs", provider="stub")
        client = build_llm_client(config.llm)
        result = client.generate_text("sys", "hello world")
        with self.assertRaises(StructuredOutputError):
            result.json_object()

    def test_cli_run_bootstrap_creates_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            exit_code = main(["run", "--output-dir", tmpdir, "--provider", "stub", "--seed", "7"])
            self.assertEqual(exit_code, 0)
            generated_dirs = [path for path in Path(tmpdir).iterdir() if path.is_dir()]
            self.assertEqual(len(generated_dirs), 1)
            run_dir = generated_dirs[0]
            self.assertTrue((run_dir / "week_plan.json").exists())
            self.assertTrue((run_dir / "days" / "day-01" / "diary.md").exists())

    def test_cli_falls_back_to_rule_based_when_network_provider_cannot_initialize(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            exit_code = main(["run", "--output-dir", tmpdir, "--provider", "gemini", "--seed", "7"])
            self.assertEqual(exit_code, 0)
            generated_dirs = [path for path in Path(tmpdir).iterdir() if path.is_dir()]
            self.assertEqual(len(generated_dirs), 1)
            self.assertTrue((generated_dirs[0] / "days" / "day-01" / "diary.md").exists())

    def test_gemini_preserves_non_user_roles_as_user_annotated_text(self) -> None:
        client = GeminiLLMClient(model="gemini-test", api_key="key", timeout_seconds=1.0)
        request = LLMRequest(
            system_prompt="system",
            messages=[
                LLMMessage(role="user", content="hello"),
                LLMMessage(role="assistant", content="world"),
                LLMMessage(role="tool", content="payload"),
            ],
        )
        payload = client._payload(request)
        self.assertEqual(payload["contents"][0]["role"], "user")
        self.assertEqual(payload["contents"][1]["role"], "model")
        self.assertEqual(payload["contents"][2]["role"], "user")
        self.assertIn("[tool]", payload["contents"][2]["parts"][0]["text"])

    def test_load_config_reads_repo_dotenv(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text(
                "\n".join(
                    [
                        "LUMEN_LLM_MODEL=gemini-2.5-flash",
                        "LUMEN_LLM_API_KEY=test-key",
                    ]
                ),
                encoding="utf-8",
            )
            config = load_config(root_dir=root, output_dir="outputs", provider="gemini")
            self.assertEqual(config.llm.provider, "gemini")
            self.assertEqual(config.llm.model, "gemini-2.5-flash")
            self.assertEqual(config.llm.api_key, "test-key")


if __name__ == "__main__":
    unittest.main()
