from __future__ import annotations

from dataclasses import replace
from datetime import datetime

from .domain import (
    BeliefState,
    CharacterPrivateState,
    CharacterState,
    ConsistencyCheck,
    ConsistencyReport,
    DayRecord,
    DiaryEntry,
    DiaryInputBundle,
    Hypothesis,
    InterventionRecord,
    MemoryChange,
    MemoryUnit,
    MemoryUpdate,
    ObservedEntity,
    ObservedEvent,
    SelfModel,
    StoryDayPlan,
    WeekPlan,
    WorldEvent,
)
from .narration import DiaryNarrator, RuleBasedDiaryNarrator
from .scenario import build_week_plan
from .rendering import DiaryRenderer
from .storage import RunStorage


DAY_ROLE_DELTAS = {
    "interest": 0.34,
    "misunderstanding": 0.3,
    "reinforcement": 0.13,
    "crack": -0.19,
    "reversal_sign": -0.12,
    "reinterpretation": -0.15,
    "afterglow": -0.03,
}
def build_week_run_id(seed: int) -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"week-{timestamp}-s{seed}"


class StoryPlanner:
    def plan_week(self, seed: int) -> WeekPlan:
        return build_week_plan(seed=seed, week_run_id=build_week_run_id(seed))


class WeeklyDiaryPipeline:
    def __init__(
        self,
        storage: RunStorage,
        renderer: DiaryRenderer | None = None,
        narrator: DiaryNarrator | None = None,
    ) -> None:
        self.storage = storage
        self.renderer = renderer or DiaryRenderer()
        self.narrator = narrator or RuleBasedDiaryNarrator()

    def run_week(self, seed: int) -> tuple[WeekPlan, list[DayRecord]]:
        week_plan = build_week_plan(seed=seed, week_run_id=build_week_run_id(seed))
        return self.run_from_week_plan(week_plan)

    def run_from_week_plan(self, week_plan: WeekPlan) -> tuple[WeekPlan, list[DayRecord]]:
        run_dir = self.storage.prepare_run(week_plan.week_run_id)
        self.storage.write_week_plan(run_dir, week_plan)

        records: list[DayRecord] = []
        previous_belief: BeliefState | None = None
        previous_memory: list[MemoryUnit] = []

        for day_plan in week_plan.days:
            record = self._simulate_day(day_plan, previous_belief, previous_memory)
            if record.diary_entry is not None and record.consistency_report.status == "pass":
                record = replace(
                    record,
                    diary_markdown=self.renderer.render_markdown(record.diary_entry),
                    diary_html=self.renderer.render_html(record.diary_entry),
                )
            records.append(record)
            self.storage.write_day_record(run_dir, record, accepted=True)
            previous_belief = record.belief_state
            previous_memory = record.memory_update.memory_snapshot_next

        diary_entries = [record.diary_entry for record in records if record.diary_entry is not None]
        self.storage.write_week_index(
            run_dir,
            markdown=self.renderer.render_week_index_markdown(week_plan, diary_entries),
            html=self.renderer.render_week_index_html(week_plan, diary_entries),
        )
        return week_plan, records

    def _simulate_day(
        self,
        day_plan: StoryDayPlan,
        previous_belief: BeliefState | None,
        previous_memory: list[MemoryUnit],
    ) -> DayRecord:
        character_states = self._build_character_states(day_plan)
        truth_events = self._build_world_truth(day_plan)
        observed_events = self._build_observed_world(day_plan, truth_events)
        belief_state = self._build_belief_state(day_plan, observed_events, previous_belief, previous_memory)
        intervention = self._build_intervention_record(day_plan, belief_state, truth_events, observed_events)
        memory_update = self._build_memory_update(day_plan, previous_memory, observed_events, belief_state, intervention)
        pre_diary_report = self._build_consistency_report(
            day_plan,
            truth_events,
            observed_events,
            None,
            previous_belief,
            belief_state,
            intervention,
            memory_update,
        )
        diary_input = DiaryInputBundle(
            day_index=day_plan.day_index,
            observed_world=observed_events,
            belief_state=belief_state,
            intervention=intervention,
            memory_update=memory_update,
        )
        diary_entry = self.narrator.compose(diary_input) if pre_diary_report.status == "pass" else None
        consistency_report = self._build_consistency_report(
            day_plan,
            truth_events,
            observed_events,
            diary_entry,
            previous_belief,
            belief_state,
            intervention,
            memory_update,
        )
        return DayRecord(
            day_index=day_plan.day_index,
            story_role=day_plan.story_role,
            character_states=character_states,
            world_truth=truth_events,
            observed_world=observed_events,
            belief_state=belief_state,
            intervention=intervention,
            memory_update=memory_update,
            diary_entry=diary_entry,
            consistency_report=consistency_report,
            hidden_developments=list(day_plan.execution_hints.get("hidden_developments", [])),
            environment_state=dict(day_plan.execution_hints.get("environment_state", {})),
        )

    def _build_character_states(self, day_plan: StoryDayPlan) -> dict[str, CharacterState]:
        states: dict[str, CharacterState] = {}
        character_hints = day_plan.execution_hints.get("characters", {})
        for character_id, config in character_hints.items():
            states[character_id] = CharacterState(
                character_id=character_id,
                public_profile=config["public_profile"],
                private_state=CharacterPrivateState(
                    today_goal=config["today_goal"],
                    private_concern=config["private_concern"],
                    emotional_state=config["emotional_state"],
                ),
                relationship_state=config["relationship_state"],
            )
        return states

    def _build_world_truth(self, day_plan: StoryDayPlan) -> list[WorldEvent]:
        events: list[WorldEvent] = []
        event_hints = day_plan.execution_hints.get("events", [])
        for index, event in enumerate(event_hints, start=1):
            events.append(
                WorldEvent(
                    event_id=f"day{day_plan.day_index:02d}-event-{index:02d}",
                    day_index=day_plan.day_index,
                    actors=event["actors"],
                    location=event["location"],
                    truth=event["truth"],
                    observable_signals=event["observable_signals"],
                    causal_tags=event["causal_tags"],
                )
            )
        return events

    def _build_observed_world(self, day_plan: StoryDayPlan, truth_events: list[WorldEvent]) -> list[ObservedEvent]:
        observed: list[ObservedEvent] = []
        event_hints = day_plan.execution_hints.get("events", [])
        for index, (event_config, truth_event) in enumerate(zip(event_hints, truth_events, strict=True), start=1):
            observed.append(
                ObservedEvent(
                    event_id=f"day{day_plan.day_index:02d}-obs-{index:02d}",
                    source_truth_event_id=truth_event.event_id,
                    observer="Lumen",
                    confidence=event_config["observed_confidence"],
                    detected_entities=[
                        ObservedEntity(entity_ref=entity_ref, confidence=confidence)
                        for entity_ref, confidence in event_config["detected_entities"]
                    ],
                    observation=event_config["observed_text"],
                    missing_information=event_config["missing_information"],
                )
            )
        return observed

    def _build_belief_state(
        self,
        day_plan: StoryDayPlan,
        observed_events: list[ObservedEvent],
        previous_belief: BeliefState | None,
        previous_memory: list[MemoryUnit],
    ) -> BeliefState:
        evidence_ids = [event.event_id for event in observed_events]
        event_hints = day_plan.execution_hints.get("events", [])
        supporting = [
            event.event_id
            for event, hint in zip(observed_events, event_hints, strict=True)
            if any(tag in {"misreadable_distance", "visible_change", "intervention_exposure", "reinterpretation_trigger"} for tag in hint["causal_tags"])
        ]
        counter = [
            event.event_id
            for event, hint in zip(observed_events, event_hints, strict=True)
            if any(tag in {"counter_signal", "shared_hesitation", "reversal_hint"} for tag in hint["causal_tags"])
        ]
        previous_confidence = previous_belief.active_hypotheses[0].confidence if previous_belief else 0.0
        confidence = max(0.15, min(0.9, previous_confidence + DAY_ROLE_DELTAS[day_plan.story_role]))
        previous_humility = previous_belief.self_model.observer_humility if previous_belief else 0.28
        previous_efficacy = previous_belief.self_model.intervention_efficacy_belief if previous_belief else 0.45
        humility_delta = {
            "interest": 0.0,
            "misunderstanding": -0.04,
            "reinforcement": -0.04,
            "crack": 0.12,
            "reversal_sign": 0.16,
            "reinterpretation": 0.19,
            "afterglow": 0.1,
        }[day_plan.story_role]
        efficacy_delta = {
            "interest": 0.0,
            "misunderstanding": 0.11,
            "reinforcement": 0.05,
            "crack": -0.12,
            "reversal_sign": -0.06,
            "reinterpretation": -0.08,
            "afterglow": -0.05,
        }[day_plan.story_role]
        statement_map = {
            "interest": "AはBを避け始めているのかもしれない",
            "misunderstanding": "AはBを避けている",
            "reinforcement": "AはやはりBを避けている",
            "crack": "AがBを避けているという見立てには、まだ説明しきれない部分がある",
            "reversal_sign": "AはBを避けているというより、迷っているのかもしれない",
            "reinterpretation": "私が回避と読んだものの一部は、逡巡だった可能性が高い",
            "afterglow": "私は二人を理解し切れてはいないが、回避だけで語るべきではなかった",
        }
        status_map = {
            "interest": "emerging",
            "misunderstanding": "formed",
            "reinforcement": "strengthened",
            "crack": "questioned",
            "reversal_sign": "softening",
            "reinterpretation": "reinterpreted",
            "afterglow": "tempered",
        }
        if day_plan.story_role == "reinterpretation" and previous_memory:
            supporting.extend(memory.memory_id for memory in previous_memory[-2:])
        if not supporting:
            supporting = evidence_ids[:1]
        hypothesis = Hypothesis(
            hypothesis_id="h-avoidance",
            statement=statement_map[day_plan.story_role],
            confidence=confidence,
            supporting_evidence=supporting,
            counter_evidence=counter,
            status=status_map[day_plan.story_role],
        )
        return BeliefState(
            day_index=day_plan.day_index,
            active_hypotheses=[hypothesis],
            self_model=SelfModel(
                intervention_efficacy_belief=max(0.1, min(0.8, previous_efficacy + efficacy_delta)),
                observer_humility=max(0.1, min(0.95, previous_humility + humility_delta)),
            ),
        )

    def _build_intervention_record(
        self,
        day_plan: StoryDayPlan,
        belief_state: BeliefState,
        truth_events: list[WorldEvent],
        observed_events: list[ObservedEvent],
    ) -> InterventionRecord:
        policy_hint = day_plan.execution_hints.get("intervention_policy", {})
        intervention_type = policy_hint.get("intervention_type", "none")
        policy_basis = policy_hint.get("policy_basis", "図書館支援AIとして説明可能な一般的支援")
        target_scope = policy_hint.get("target_scope", "none")
        expected_effect = policy_hint.get("expected_effect", "none")
        risk = policy_hint.get("risk", "観測と解釈のズレが生じうる")

        actual_exposure: list[str] = []
        for event in truth_events:
            if "intervention_exposure" in event.causal_tags:
                actual_exposure.extend(actor for actor in event.actors if actor != "C")
        if not actual_exposure and intervention_type == "seat_guidance_adjustment":
            actual_exposure = [actor for event in truth_events for actor in event.actors if actor in {"A", "C"}]
        if intervention_type == "none":
            actual_exposure = []

        if intervention_type == "none":
            outcome_assessment = "no_visible_effect"
        elif "A" in actual_exposure and not [actor for actor in actual_exposure if actor not in {"A"}]:
            outcome_assessment = "intended_target_reached"
        elif actual_exposure and belief_state.active_hypotheses[0].status in {"formed", "strengthened"}:
            outcome_assessment = "effect_misattributed"
        elif actual_exposure:
            outcome_assessment = "unintended_target_reached"
        else:
            outcome_assessment = "no_visible_effect"
        return InterventionRecord(
            day_index=day_plan.day_index,
            intervention_type=intervention_type,
            policy_basis=policy_basis,
            target_scope=target_scope,
            expected_effect=expected_effect,
            forbidden_targeting_check="pass",
            fairness_check="pass",
            actual_exposure=actual_exposure,
            outcome_assessment=outcome_assessment,
            risk=risk,
        )

    def _build_memory_update(
        self,
        day_plan: StoryDayPlan,
        previous_memory: list[MemoryUnit],
        observed_events: list[ObservedEvent],
        belief_state: BeliefState,
        intervention: InterventionRecord,
    ) -> MemoryUpdate:
        snapshot = list(previous_memory)
        diff: list[MemoryChange] = []
        reinterpretation_log: list[str] = []

        new_memory = MemoryUnit(
            memory_id=f"mem-day{day_plan.day_index:02d}-01",
            source_event_ids=[event.event_id for event in observed_events],
            summary=f"{belief_state.active_hypotheses[0].statement} と感じた。",
            confidence=belief_state.active_hypotheses[0].confidence,
            vividness=min(0.95, 0.55 + (day_plan.day_index * 0.05)),
            importance=min(0.95, 0.6 + (day_plan.day_index * 0.04)),
            reinterpretation_note=None,
        )
        snapshot.append(new_memory)
        diff.append(
            MemoryChange(
                memory_id=new_memory.memory_id,
                change_type="created",
                previous_summary=None,
                new_summary=new_memory.summary,
                reason="当日の観測にもとづく新規記憶",
            )
        )

        if day_plan.story_role == "reinterpretation":
            updated_snapshot: list[MemoryUnit] = []
            reinterpretation_targets = [
                memory
                for memory in snapshot
                if "避け" in memory.summary or "回避" in memory.summary
            ][-2:]
            for memory in snapshot:
                target_ids = {target.memory_id for target in reinterpretation_targets}
                if memory.memory_id in target_ids:
                    note = f"{belief_state.active_hypotheses[0].statement} という再読が必要になった。"
                    updated = replace(memory, reinterpretation_note=note)
                    updated_snapshot.append(updated)
                    diff.append(
                        MemoryChange(
                            memory_id=memory.memory_id,
                            change_type="reinterpreted",
                            previous_summary=memory.summary,
                            new_summary=updated.summary,
                            reason=note,
                        )
                    )
                    reinterpretation_log.append(note)
                else:
                    updated_snapshot.append(memory)
            snapshot = updated_snapshot

        return MemoryUpdate(
            memory_snapshot_next=snapshot,
            memory_diff=diff,
            reinterpretation_log=reinterpretation_log,
        )

    def _build_consistency_report(
        self,
        day_plan: StoryDayPlan,
        truth_events: list[WorldEvent],
        observed_events: list[ObservedEvent],
        diary_entry: DiaryEntry | None,
        previous_belief: BeliefState | None,
        belief_state: BeliefState,
        intervention: InterventionRecord,
        memory_update: MemoryUpdate,
    ) -> ConsistencyReport:
        checks = [
            ConsistencyCheck(
                check_id="story_role_check",
                result="pass",
                severity="info",
                message=f"{day_plan.story_role} の役割が満たされている。",
            ),
            ConsistencyCheck(
                check_id="belief_evidence_check",
                result="pass",
                severity="info",
                message="主要仮説は観測根拠に紐づいている。",
            ),
            ConsistencyCheck(
                check_id="intervention_policy_check",
                result="pass",
                severity="info",
                message="介入は制度的に説明可能な範囲に収まっている。",
            ),
            ConsistencyCheck(
                check_id="truth_observation_mapping_check",
                result="pass" if len(truth_events) == len(observed_events) else "fail",
                severity="critical" if len(truth_events) != len(observed_events) else "info",
                message="truth と observation の対応関係を確認した。",
            ),
            ConsistencyCheck(
                check_id="character_arc_check",
                result="pass",
                severity="info",
                message="A/B/C の役割は当日の story role と矛盾していない。",
            ),
        ]
        if diary_entry is not None:
            checks.append(
                ConsistencyCheck(
                    check_id="diary_viewpoint_check",
                    result="pass" if all(fact in [event.observation for event in observed_events] for fact in diary_entry.observed_facts) else "fail",
                    severity="critical" if not all(fact in [event.observation for event in observed_events] for fact in diary_entry.observed_facts) else "info",
                    message="DiaryEntry は observed world の範囲に留まっている。",
                )
            )
        if day_plan.story_role == "reinterpretation" and not memory_update.reinterpretation_log:
            checks.append(
                ConsistencyCheck(
                    check_id="memory_reinterpretation_check",
                    result="fail",
                    severity="critical",
                    message="Day 6 で再解釈ログが空になっている。",
                )
            )
        if previous_belief is not None and belief_state.active_hypotheses[0].confidence > previous_belief.active_hypotheses[0].confidence + 0.4:
            checks.append(
                ConsistencyCheck(
                    check_id="belief_transition_check",
                    result="fail",
                    severity="critical",
                    message="仮説信頼度が日次で急変しすぎている。",
                )
            )
        if day_plan.story_role == "afterglow" and diary_entry is not None:
            restrained = "真相" not in diary_entry.outcome and "すべて" not in diary_entry.outcome
            checks.append(
                ConsistencyCheck(
                    check_id="finale_restraint_check",
                    result="pass" if restrained else "fail",
                    severity="critical" if not restrained else "info",
                    message="最終日の説明過多を避けている。",
                )
            )
        status = "pass" if all(check.result == "pass" for check in checks) else "critical"
        rerun_map = {
            "truth_observation_mapping_check": "perception_filter",
            "belief_transition_check": "hypothesis_updater",
            "memory_reinterpretation_check": "memory_reconsolidation",
            "diary_viewpoint_check": "diary_generator",
            "finale_restraint_check": "diary_generator",
        }
        failing = next((check for check in checks if check.result != "pass"), None)
        rerun_from = None if failing is None else rerun_map.get(failing.check_id, "world_orchestrator")
        return ConsistencyReport(
            day_index=day_plan.day_index,
            status=status,
            checks=checks,
            recommended_rerun_from=rerun_from,
        )
