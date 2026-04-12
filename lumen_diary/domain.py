from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any


def _serialize(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _serialize(item) for key, item in asdict(value).items()}
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, Path):
        return str(value)
    return value


@dataclass(frozen=True)
class Serializable:
    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class StoryDayPlan(Serializable):
    day_index: int
    story_role: str
    required_shift: str
    must_reveal: list[str]
    must_hide: list[str]
    required_pressure: str
    execution_hints: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class WeekPlan(Serializable):
    week_run_id: str
    seed: int
    weekly_theme: str
    central_misunderstanding: str
    days: list[StoryDayPlan]
    character_arcs: dict[str, str]


@dataclass(frozen=True)
class CharacterPrivateState(Serializable):
    today_goal: str
    private_concern: str
    emotional_state: str


@dataclass(frozen=True)
class CharacterState(Serializable):
    character_id: str
    public_profile: dict[str, str]
    private_state: CharacterPrivateState
    relationship_state: dict[str, str]


@dataclass(frozen=True)
class WorldEvent(Serializable):
    event_id: str
    day_index: int
    actors: list[str]
    location: str
    truth: str
    observable_signals: list[str]
    causal_tags: list[str]


@dataclass(frozen=True)
class ObservedEntity(Serializable):
    entity_ref: str
    confidence: float


@dataclass(frozen=True)
class ObservedEvent(Serializable):
    event_id: str
    source_truth_event_id: str
    observer: str
    confidence: float
    detected_entities: list[ObservedEntity]
    observation: str
    missing_information: list[str]


@dataclass(frozen=True)
class Hypothesis(Serializable):
    hypothesis_id: str
    statement: str
    confidence: float
    supporting_evidence: list[str]
    counter_evidence: list[str]
    status: str


@dataclass(frozen=True)
class SelfModel(Serializable):
    intervention_efficacy_belief: float
    observer_humility: float


@dataclass(frozen=True)
class BeliefState(Serializable):
    day_index: int
    active_hypotheses: list[Hypothesis]
    self_model: SelfModel


@dataclass(frozen=True)
class InterventionRecord(Serializable):
    day_index: int
    intervention_type: str
    policy_basis: str
    target_scope: str
    expected_effect: str
    forbidden_targeting_check: str
    fairness_check: str
    actual_exposure: list[str]
    outcome_assessment: str
    risk: str


@dataclass(frozen=True)
class MemoryUnit(Serializable):
    memory_id: str
    source_event_ids: list[str]
    summary: str
    confidence: float
    vividness: float
    importance: float
    reinterpretation_note: str | None = None


@dataclass(frozen=True)
class MemoryChange(Serializable):
    memory_id: str
    change_type: str
    previous_summary: str | None
    new_summary: str | None
    reason: str


@dataclass(frozen=True)
class MemoryUpdate(Serializable):
    memory_snapshot_next: list[MemoryUnit]
    memory_diff: list[MemoryChange]
    reinterpretation_log: list[str]


@dataclass(frozen=True)
class DiaryEntry(Serializable):
    day_index: int
    title: str
    observed_facts: list[str]
    interpretation: str
    attempted_action: str
    outcome: str
    intervention_reflection: str
    closing_shift: str


@dataclass(frozen=True)
class ConsistencyCheck(Serializable):
    check_id: str
    result: str
    severity: str
    message: str


@dataclass(frozen=True)
class ConsistencyReport(Serializable):
    day_index: int
    status: str
    checks: list[ConsistencyCheck]
    recommended_rerun_from: str | None = None


@dataclass(frozen=True)
class DiaryInputBundle(Serializable):
    day_index: int
    observed_world: list[ObservedEvent]
    belief_state: BeliefState
    intervention: InterventionRecord
    memory_update: MemoryUpdate


@dataclass(frozen=True)
class DayRecord(Serializable):
    day_index: int
    story_role: str
    character_states: dict[str, CharacterState]
    world_truth: list[WorldEvent]
    observed_world: list[ObservedEvent]
    belief_state: BeliefState
    intervention: InterventionRecord
    memory_update: MemoryUpdate
    diary_entry: DiaryEntry | None = None
    diary_markdown: str | None = None
    diary_html: str | None = None
    consistency_report: ConsistencyReport | None = None
    hidden_developments: list[str] = field(default_factory=list)
    environment_state: dict[str, str] = field(default_factory=dict)
