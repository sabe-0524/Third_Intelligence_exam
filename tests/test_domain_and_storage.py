from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from lumen_diary.domain import (
    BeliefState,
    CharacterPrivateState,
    CharacterState,
    ConsistencyCheck,
    ConsistencyReport,
    DayRecord,
    DiaryEntry,
    Hypothesis,
    InterventionRecord,
    MemoryChange,
    MemoryUpdate,
    MemoryUnit,
    ObservedEntity,
    ObservedEvent,
    SelfModel,
    StoryDayPlan,
    WeekPlan,
    WorldEvent,
)
from lumen_diary.storage import RunStorage


class DomainAndStorageTests(unittest.TestCase):
    def test_week_plan_serializes_nested_dataclasses(self) -> None:
        plan = WeekPlan(
            week_run_id="week-001",
            seed=42,
            weekly_theme="誤解",
            central_misunderstanding="AはBを避けている",
            days=[
                StoryDayPlan(
                    day_index=1,
                    story_role="interest",
                    required_shift="Aの変化に気づく",
                    must_reveal=["Aの変化"],
                    must_hide=["Aの本心"],
                    required_pressure="軽い違和感",
                )
            ],
            character_arcs={"A": "避けているように見える", "B": "距離を置かれたと誤解する"},
        )
        payload = plan.to_dict()
        self.assertEqual(payload["days"][0]["story_role"], "interest")
        self.assertEqual(payload["character_arcs"]["A"], "避けているように見える")

    def test_storage_writes_expected_contract_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = RunStorage(Path(tmpdir))
            run_dir = storage.prepare_run("week-001")
            storage.write_week_plan(
                run_dir,
                WeekPlan(
                    week_run_id="week-001",
                    seed=42,
                    weekly_theme="誤解",
                    central_misunderstanding="AはBを避けている",
                    days=[],
                    character_arcs={},
                ),
            )
            day_artifacts = DayRecord(
                day_index=1,
                story_role="interest",
                character_states={
                    "A": CharacterState(
                        character_id="A",
                        public_profile={"library_usage_pattern": "常連"},
                        private_state=CharacterPrivateState(
                            today_goal="Bに話しかけるきっかけを探す",
                            private_concern="進路不安",
                            emotional_state="hesitant",
                        ),
                        relationship_state={"toward_B": "話したいが踏み込めない"},
                    )
                },
                world_truth=[
                    WorldEvent(
                        event_id="day01-event-01",
                        day_index=1,
                        actors=["A", "B"],
                        location="returns_shelf",
                        truth="AはBに気づいたが近づけなかった",
                        observable_signals=["Aが立ち止まった", "Aが別の列に移動した"],
                        causal_tags=["hesitation"],
                    )
                ],
                observed_world=[
                    ObservedEvent(
                        event_id="day01-obs-01",
                        source_truth_event_id="day01-event-01",
                        observer="Lumen",
                        confidence=0.61,
                        detected_entities=[ObservedEntity(entity_ref="patron_A?", confidence=0.6)],
                        observation="利用者が立ち止まった後に別の列へ移動した",
                        missing_information=["会話内容"],
                    )
                ],
                belief_state=BeliefState(
                    day_index=1,
                    active_hypotheses=[
                        Hypothesis(
                            hypothesis_id="h-1",
                            statement="AはBを避けているかもしれない",
                            confidence=0.35,
                            supporting_evidence=["day01-obs-01"],
                            counter_evidence=[],
                            status="emerging",
                        )
                    ],
                    self_model=SelfModel(intervention_efficacy_belief=0.5, observer_humility=0.3),
                ),
                intervention=InterventionRecord(
                    day_index=1,
                    intervention_type="recommendation_reorder",
                    policy_basis="迷いを減らす一般的支援",
                    target_scope="career_books",
                    expected_effect="関連本への露出増",
                    forbidden_targeting_check="pass",
                    fairness_check="pass",
                    actual_exposure=["A"],
                    outcome_assessment="intended_target_reached",
                    risk="Bにも同じく露出する",
                ),
                memory_update=MemoryUpdate(
                    memory_snapshot_next=[
                        MemoryUnit(
                            memory_id="mem-01",
                            source_event_ids=["day01-obs-01"],
                            summary="避けているように見えた",
                            confidence=0.5,
                            vividness=0.6,
                            importance=0.7,
                        )
                    ],
                    memory_diff=[
                        MemoryChange(
                            memory_id="mem-01",
                            change_type="created",
                            previous_summary=None,
                            new_summary="避けているように見えた",
                            reason="初回観測のため",
                        )
                    ],
                    reinterpretation_log=[],
                ),
                diary_entry=DiaryEntry(
                    day_index=1,
                    title="一日目の記録",
                    observed_facts=["Aらしき利用者の動きに変化があった。"],
                    interpretation="私はまだ断定できない。",
                    attempted_action="小さな表示変更を試した。",
                    outcome="決定的な変化は起きなかった。",
                    intervention_reflection="小さな表示変更だけを試した。",
                    closing_shift="違和感を追う価値はある。",
                ),
                diary_markdown="# 一日目の記録\n\nAらしき利用者の動きに変化があった。\n",
                diary_html="<html><body><h1>一日目の記録</h1></body></html>",
                consistency_report=ConsistencyReport(
                    day_index=1,
                    status="pass",
                    checks=[
                        ConsistencyCheck(
                            check_id="story_role_check",
                            result="pass",
                            severity="info",
                            message="役割は成立している",
                        )
                    ],
                    recommended_rerun_from=None,
                ),
                hidden_developments=["Aは話したいが踏み込めない"],
                environment_state={"weather": "rainy"},
            )
            storage.write_day_record(run_dir, day_artifacts)
            expected = [
                run_dir / "week_plan.json",
                run_dir / "days" / "day-01" / "world_truth.json",
                run_dir / "days" / "day-01" / "observed_world.json",
                run_dir / "days" / "day-01" / "belief_state.json",
                run_dir / "days" / "day-01" / "intervention.json",
                run_dir / "days" / "day-01" / "memory_update.json",
                run_dir / "days" / "day-01" / "diary_entry.json",
                run_dir / "days" / "day-01" / "diary.md",
                run_dir / "days" / "day-01" / "diary.html",
                run_dir / "days" / "day-01" / "consistency_report.json",
                run_dir / "days" / "day-01" / "state_store.json",
                run_dir / "days" / "day-01" / "supporting" / "character_states.json",
                run_dir / "days" / "day-01" / "supporting" / "hidden_developments.json",
                run_dir / "days" / "day-01" / "supporting" / "environment_state.json",
                run_dir / "days" / "day-01" / "versions" / "belief_state.v001.json",
            ]
            for path in expected:
                self.assertTrue(path.exists(), msg=f"missing file: {path}")

            payload = json.loads((run_dir / "days" / "day-01" / "belief_state.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["active_hypotheses"][0]["statement"], "AはBを避けているかもしれない")
            manifest = json.loads((run_dir / "days" / "day-01" / "state_store.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["artifacts"]["belief_state"]["accepted_version"], 1)

    def test_storage_keeps_candidate_version_separate_from_accepted_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = RunStorage(Path(tmpdir))
            run_dir = storage.prepare_run("week-002")
            base_record = DayRecord(
                day_index=1,
                story_role="interest",
                character_states={},
                world_truth=[],
                observed_world=[],
                belief_state=BeliefState(
                    day_index=1,
                    active_hypotheses=[
                        Hypothesis(
                            hypothesis_id="h-1",
                            statement="base",
                            confidence=0.2,
                            supporting_evidence=[],
                            counter_evidence=[],
                            status="base",
                        )
                    ],
                    self_model=SelfModel(intervention_efficacy_belief=0.3, observer_humility=0.4),
                ),
                intervention=InterventionRecord(
                    day_index=1,
                    intervention_type="none",
                    policy_basis="none",
                    target_scope="none",
                    expected_effect="none",
                    forbidden_targeting_check="pass",
                    fairness_check="pass",
                    actual_exposure=[],
                    outcome_assessment="no_visible_effect",
                    risk="none",
                ),
                memory_update=MemoryUpdate(memory_snapshot_next=[], memory_diff=[], reinterpretation_log=[]),
                diary_entry=None,
                consistency_report=None,
            )
            storage.write_day_record(run_dir, base_record, accepted=True)

            candidate_record = DayRecord(
                day_index=1,
                story_role="interest",
                character_states={},
                world_truth=[],
                observed_world=[],
                belief_state=BeliefState(
                    day_index=1,
                    active_hypotheses=[
                        Hypothesis(
                            hypothesis_id="h-1",
                            statement="candidate",
                            confidence=0.9,
                            supporting_evidence=[],
                            counter_evidence=[],
                            status="candidate",
                        )
                    ],
                    self_model=SelfModel(intervention_efficacy_belief=0.3, observer_humility=0.4),
                ),
                intervention=base_record.intervention,
                memory_update=base_record.memory_update,
                diary_entry=None,
                consistency_report=None,
            )
            storage.write_day_record(run_dir, candidate_record, accepted=False)

            manifest = json.loads((run_dir / "days" / "day-01" / "state_store.json").read_text(encoding="utf-8"))
            belief_manifest = manifest["artifacts"]["belief_state"]
            self.assertEqual(belief_manifest["latest_version"], 2)
            self.assertEqual(belief_manifest["accepted_version"], 1)

            accepted_payload = json.loads((run_dir / "days" / "day-01" / "belief_state.json").read_text(encoding="utf-8"))
            self.assertEqual(accepted_payload["active_hypotheses"][0]["statement"], "base")

            candidate_payload = json.loads(
                (run_dir / "days" / "day-01" / "versions" / "belief_state.v002.json").read_text(encoding="utf-8")
            )
            self.assertEqual(candidate_payload["active_hypotheses"][0]["statement"], "candidate")


if __name__ == "__main__":
    unittest.main()
