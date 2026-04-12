from __future__ import annotations

import unittest

from lumen_diary.domain import (
    BeliefState,
    DiaryInputBundle,
    Hypothesis,
    InterventionRecord,
    MemoryUpdate,
    ObservedEntity,
    ObservedEvent,
    SelfModel,
)
from lumen_diary.llm.base import LLMClient, LLMRequest, LLMResult
from lumen_diary.narration import LLMDiaryNarrator, RuleBasedDiaryNarrator


class FakeLLMClient(LLMClient):
    provider = "openai"
    model = "fake-model"

    def __init__(self, text: str) -> None:
        self.text = text

    def generate(self, request: LLMRequest) -> LLMResult:
        return LLMResult(text=self.text, provider=self.provider, model=self.model, raw_response={"fake": True})


def _sample_diary_input() -> DiaryInputBundle:
    return DiaryInputBundle(
        day_index=2,
        observed_world=[
            ObservedEvent(
                event_id="obs-1",
                source_truth_event_id="event-1",
                observer="Lumen",
                confidence=0.6,
                detected_entities=[ObservedEntity(entity_ref="patron_A?", confidence=0.6)],
                observation="Aらしき利用者はBらしき利用者の近くまで来た後、触れずに離れた。",
                missing_information=["会話内容"],
            )
        ],
        belief_state=BeliefState(
            day_index=2,
            active_hypotheses=[
                Hypothesis(
                    hypothesis_id="h-avoidance",
                    statement="AはBを避けている",
                    confidence=0.6,
                    supporting_evidence=["obs-1"],
                    counter_evidence=[],
                    status="formed",
                )
            ],
            self_model=SelfModel(intervention_efficacy_belief=0.5, observer_humility=0.3),
        ),
        intervention=InterventionRecord(
            day_index=2,
            intervention_type="recommendation_reorder",
            policy_basis="一般的支援",
            target_scope="career_transition_books",
            expected_effect="関連本への露出増",
            forbidden_targeting_check="pass",
            fairness_check="pass",
            actual_exposure=["A"],
            outcome_assessment="intended_target_reached",
            risk="第三者へも露出する",
        ),
        memory_update=MemoryUpdate(memory_snapshot_next=[], memory_diff=[], reinterpretation_log=[]),
    )


class NarrationTests(unittest.TestCase):
    def test_llm_narrator_uses_structured_json_response(self) -> None:
        client = FakeLLMClient(
            """
            {
              "title": "二日目の記録",
              "observed_facts": ["Aらしき利用者はBらしき利用者の近くまで来た後、触れずに離れた。"],
              "interpretation": "AはBを避けている",
              "attempted_action": "棚の提示順を調整した。",
              "outcome": "意図した相手に近い反応が見えた。",
              "intervention_reflection": "私はまだ自分の見立てを信じている。",
              "closing_shift": "私は観測者であるだけでは足りないと感じ始めた。"
            }
            """.strip()
        )
        narrator = LLMDiaryNarrator(llm_client=client, fallback=RuleBasedDiaryNarrator())
        entry = narrator.compose(_sample_diary_input())
        self.assertEqual(entry.title, "二日目の記録")
        self.assertEqual(entry.observed_facts[0], "Aらしき利用者はBらしき利用者の近くまで来た後、触れずに離れた。")

    def test_llm_narrator_falls_back_when_json_is_invalid(self) -> None:
        client = FakeLLMClient("not-json")
        narrator = LLMDiaryNarrator(llm_client=client, fallback=RuleBasedDiaryNarrator())
        entry = narrator.compose(_sample_diary_input())
        self.assertEqual(entry.day_index, 2)
        self.assertIn("AはBを避けている", entry.interpretation)

    def test_llm_narrator_rejects_observed_fact_rewrites_by_merging_base_entry(self) -> None:
        client = FakeLLMClient(
            """
            {
              "title": "別の題名",
              "observed_facts": ["主人公には見えていない事実を追加した。"],
              "interpretation": "AはBを避けている。実際には話したいが隠している。",
              "attempted_action": "勝手な介入をした。",
              "outcome": "真相は分かった。",
              "intervention_reflection": "穏当な反省だった。",
              "closing_shift": "主人公には見えないが、話したいが理由だった。"
            }
            """.strip()
        )
        narrator = LLMDiaryNarrator(llm_client=client, fallback=RuleBasedDiaryNarrator())
        entry = narrator.compose(_sample_diary_input())
        self.assertEqual(entry.observed_facts[0], "Aらしき利用者はBらしき利用者の近くまで来た後、触れずに離れた。")
        self.assertEqual(entry.interpretation, "AはBを避けている")
        self.assertNotIn("話したいが", entry.closing_shift)


if __name__ == "__main__":
    unittest.main()
