from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .domain import DayRecord, Serializable, WeekPlan


class RunStorage:
    def __init__(self, output_root: Path) -> None:
        self.output_root = output_root

    def prepare_run(self, week_run_id: str) -> Path:
        run_dir = self.output_root / week_run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "days").mkdir(exist_ok=True)
        return run_dir

    def day_dir(self, run_dir: Path, day_index: int) -> Path:
        day_dir = run_dir / "days" / f"day-{day_index:02d}"
        day_dir.mkdir(parents=True, exist_ok=True)
        return day_dir

    def write_json(self, path: Path, payload: Serializable | dict[str, Any] | list[Any]) -> None:
        if isinstance(payload, Serializable):
            content = payload.to_dict()
        else:
            content = payload
        path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")

    def write_text(self, path: Path, content: str) -> None:
        path.write_text(content, encoding="utf-8")

    def write_week_plan(self, run_dir: Path, week_plan: WeekPlan) -> None:
        self.write_json(run_dir / "week_plan.json", week_plan)

    def write_week_index(self, run_dir: Path, *, markdown: str, html: str) -> None:
        self.write_text(run_dir / "index.md", markdown)
        self.write_text(run_dir / "index.html", html)

    def _manifest_path(self, day_dir: Path) -> Path:
        return day_dir / "state_store.json"

    def _load_manifest(self, day_dir: Path) -> dict[str, Any]:
        manifest_path = self._manifest_path(day_dir)
        if not manifest_path.exists():
            return {"artifacts": {}}
        return json.loads(manifest_path.read_text(encoding="utf-8"))

    def _save_manifest(self, day_dir: Path, manifest: dict[str, Any]) -> None:
        self.write_json(self._manifest_path(day_dir), manifest)

    def _write_versioned_json(
        self,
        day_dir: Path,
        artifact_name: str,
        payload: Serializable | dict[str, Any] | list[Any],
        *,
        accepted: bool,
    ) -> None:
        versions_dir = day_dir / "versions"
        versions_dir.mkdir(exist_ok=True)
        manifest = self._load_manifest(day_dir)
        artifact_manifest = manifest["artifacts"].get(artifact_name, {})
        current_version = int(artifact_manifest.get("latest_version", 0)) + 1
        version_filename = f"{artifact_name}.v{current_version:03d}.json"
        version_path = versions_dir / version_filename
        self.write_json(version_path, payload)
        latest_path = day_dir / f"{artifact_name}.json"
        updated_manifest = {
            "latest_version": current_version,
            "latest_path": str(version_path.relative_to(day_dir)),
            "accepted_version": artifact_manifest.get("accepted_version"),
            "accepted_path": artifact_manifest.get("accepted_path"),
            "previous_accepted_version": artifact_manifest.get("previous_accepted_version"),
        }
        if accepted:
            latest_path.write_text(version_path.read_text(encoding="utf-8"), encoding="utf-8")
            updated_manifest["previous_accepted_version"] = artifact_manifest.get("accepted_version")
            updated_manifest["accepted_version"] = current_version
            updated_manifest["accepted_path"] = str(latest_path.relative_to(day_dir))
        manifest["artifacts"][artifact_name] = updated_manifest
        self._save_manifest(day_dir, manifest)

    def _write_versioned_text(
        self,
        day_dir: Path,
        artifact_name: str,
        extension: str,
        content: str,
        *,
        accepted: bool,
    ) -> None:
        versions_dir = day_dir / "versions"
        versions_dir.mkdir(exist_ok=True)
        manifest = self._load_manifest(day_dir)
        artifact_manifest = manifest["artifacts"].get(artifact_name, {})
        current_version = int(artifact_manifest.get("latest_version", 0)) + 1
        version_filename = f"{artifact_name}.v{current_version:03d}.{extension}"
        version_path = versions_dir / version_filename
        self.write_text(version_path, content)
        latest_path = day_dir / f"{artifact_name}.{extension}"
        updated_manifest = {
            "latest_version": current_version,
            "latest_path": str(version_path.relative_to(day_dir)),
            "accepted_version": artifact_manifest.get("accepted_version"),
            "accepted_path": artifact_manifest.get("accepted_path"),
            "previous_accepted_version": artifact_manifest.get("previous_accepted_version"),
        }
        if accepted:
            latest_path.write_text(content, encoding="utf-8")
            updated_manifest["previous_accepted_version"] = artifact_manifest.get("accepted_version")
            updated_manifest["accepted_version"] = current_version
            updated_manifest["accepted_path"] = str(latest_path.relative_to(day_dir))
        manifest["artifacts"][artifact_name] = updated_manifest
        self._save_manifest(day_dir, manifest)

    def write_day_record(self, run_dir: Path, day: DayRecord, *, accepted: bool = True) -> None:
        day_dir = self.day_dir(run_dir, day.day_index)
        self._write_versioned_json(day_dir, "world_truth", [event.to_dict() for event in day.world_truth], accepted=accepted)
        self._write_versioned_json(day_dir, "observed_world", [event.to_dict() for event in day.observed_world], accepted=accepted)
        self._write_versioned_json(day_dir, "belief_state", day.belief_state, accepted=accepted)
        self._write_versioned_json(day_dir, "intervention", day.intervention, accepted=accepted)
        self._write_versioned_json(day_dir, "memory_update", day.memory_update, accepted=accepted)
        if day.consistency_report is not None:
            self._write_versioned_json(day_dir, "consistency_report", day.consistency_report, accepted=accepted)
        if day.diary_entry is not None:
            self._write_versioned_json(day_dir, "diary_entry", day.diary_entry, accepted=accepted)
        if day.diary_markdown is not None:
            self._write_versioned_text(day_dir, "diary", "md", day.diary_markdown, accepted=accepted)
        if day.diary_html is not None:
            self._write_versioned_text(day_dir, "diary", "html", day.diary_html, accepted=accepted)

        supporting_dir = day_dir / "supporting"
        supporting_dir.mkdir(exist_ok=True)
        self.write_json(supporting_dir / "character_states.json", {key: value.to_dict() for key, value in day.character_states.items()})
        self.write_json(supporting_dir / "hidden_developments.json", day.hidden_developments)
        self.write_json(supporting_dir / "environment_state.json", day.environment_state)
