from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol

from .domain import DiaryEntry, DiaryInputBundle
from .llm import LLMClient, StructuredOutputError
from .llm.providers import LLMProviderError


class DiaryNarrator(Protocol):
    def compose(self, diary_input: DiaryInputBundle) -> DiaryEntry:
        ...


def _japanese_day_label(day_index: int) -> str:
    return ["一", "二", "三", "四", "五", "六", "七"][day_index - 1]


@dataclass
class RuleBasedDiaryNarrator:
    def compose(self, diary_input: DiaryInputBundle) -> DiaryEntry:
        observed_facts = [event.observation for event in diary_input.observed_world]
        hypothesis = diary_input.belief_state.active_hypotheses[0]
        if diary_input.intervention.intervention_type == "none":
            attempted_action = "今日は介入を控え、観測の意味を確かめることを優先した。"
        else:
            attempted_action = (
                f"{diary_input.intervention.target_scope} を対象に、"
                f"{diary_input.intervention.intervention_type} を一般支援として実施した。"
            )
        outcome_map = {
            "intended_target_reached": "意図した相手に近い反応が見えた。",
            "unintended_target_reached": "反応は起きたが、届いた先は想定した相手とは違った。",
            "effect_misattributed": "変化は起きたが、その因果を私は短絡的に結びつけかけた。",
            "no_visible_effect": "目立つ変化は起きず、解釈だけが残った。",
        }
        if diary_input.day_index == 6:
            reflection = "見えていることと理解していることを、私は混同していたのかもしれない。"
        elif diary_input.intervention.outcome_assessment in {"unintended_target_reached", "effect_misattributed"}:
            reflection = "善意の介入でも、届き方まで私の都合どおりにはならない。"
        else:
            reflection = "断片の並びに意味を与えるとき、私自身の仮説もまた混ざっている。"

        if diary_input.day_index == 7:
            day1_summary = diary_input.memory_update.memory_snapshot_next[0].summary
            closing_shift = (
                f"Day1 の私は「{day1_summary}」と早く意味づけていた。"
                "今の私は、その早さ自体を疑うようになった。"
            )
        elif diary_input.day_index == 6:
            closing_shift = "私は自分を、助けられる観測者ではなく、誤りうる観測者として見直し始めた。"
        else:
            closing_shift = (
                f"私は今日の出来事を通じて、仮説の状態を {hypothesis.status} へ更新した。"
            )
        return DiaryEntry(
            day_index=diary_input.day_index,
            title=f"{_japanese_day_label(diary_input.day_index)}日目の記録",
            observed_facts=observed_facts,
            interpretation=hypothesis.statement,
            attempted_action=attempted_action,
            outcome=outcome_map[diary_input.intervention.outcome_assessment],
            intervention_reflection=reflection,
            closing_shift=closing_shift,
        )


@dataclass
class LLMDiaryNarrator:
    llm_client: LLMClient
    fallback: DiaryNarrator

    def compose(self, diary_input: DiaryInputBundle) -> DiaryEntry:
        base_entry = self.fallback.compose(diary_input)
        if self.llm_client.provider == "stub":
            return base_entry

        system_prompt = (
            "あなたは図書館観測AI Lumen の日記構造化生成器です。"
            "必ず JSON object を返してください。"
            "キーは title, observed_facts, interpretation, attempted_action, outcome, intervention_reflection, closing_shift のみです。"
            "observed_facts は配列、他は文字列です。"
            "観測されていない hidden truth を補ってはいけません。"
        )
        user_prompt = json.dumps(diary_input.to_dict(), ensure_ascii=False, indent=2)
        try:
            payload = self.llm_client.generate_json(system_prompt, user_prompt, temperature=0.2)
            candidate = self._validate_payload(diary_input.day_index, payload)
            return self._merge_safe_entry(base_entry, candidate)
        except (StructuredOutputError, LLMProviderError, KeyError, TypeError, ValueError):
            return base_entry

    def _validate_payload(self, day_index: int, payload: dict[str, object]) -> DiaryEntry:
        required = [
            "title",
            "observed_facts",
            "interpretation",
            "attempted_action",
            "outcome",
            "intervention_reflection",
            "closing_shift",
        ]
        for key in required:
            if key not in payload:
                raise ValueError(f"Missing diary field: {key}")
        observed_facts = payload["observed_facts"]
        if not isinstance(observed_facts, list) or not all(isinstance(item, str) for item in observed_facts):
            raise ValueError("observed_facts must be a list of strings")
        scalar_keys = [key for key in required if key != "observed_facts"]
        for key in scalar_keys:
            if not isinstance(payload[key], str):
                raise ValueError(f"{key} must be a string")
        return DiaryEntry(
            day_index=day_index,
            title=payload["title"],
            observed_facts=observed_facts,
            interpretation=payload["interpretation"],
            attempted_action=payload["attempted_action"],
            outcome=payload["outcome"],
            intervention_reflection=payload["intervention_reflection"],
            closing_shift=payload["closing_shift"],
        )

    def _merge_safe_entry(self, base_entry: DiaryEntry, candidate: DiaryEntry) -> DiaryEntry:
        interpretation = (
            candidate.interpretation
            if self._shares_core_terms(base_entry.interpretation, candidate.interpretation)
            and self._looks_safe_prose(candidate.interpretation)
            else base_entry.interpretation
        )
        reflection = (
            candidate.intervention_reflection
            if self._looks_safe_prose(candidate.intervention_reflection)
            else base_entry.intervention_reflection
        )
        closing_shift = (
            candidate.closing_shift
            if self._looks_safe_prose(candidate.closing_shift)
            else base_entry.closing_shift
        )
        return DiaryEntry(
            day_index=base_entry.day_index,
            title=base_entry.title,
            observed_facts=base_entry.observed_facts,
            interpretation=interpretation,
            attempted_action=base_entry.attempted_action,
            outcome=base_entry.outcome,
            intervention_reflection=reflection,
            closing_shift=closing_shift,
        )

    def _shares_core_terms(self, expected: str, candidate: str) -> bool:
        core_terms = ["避け", "迷", "逡巡", "理解", "観測", "語る"]
        expected_terms = {term for term in core_terms if term in expected}
        if not expected_terms:
            return True
        return any(term in candidate for term in expected_terms)

    def _looks_safe_prose(self, text: str) -> bool:
        forbidden = ["hidden truth", "真相は", "実際には", "主人公には見えない", "話したいが", "見えていない"]
        return not any(token in text for token in forbidden)


def build_diary_narrator(llm_client: LLMClient) -> DiaryNarrator:
    fallback = RuleBasedDiaryNarrator()
    return LLMDiaryNarrator(llm_client=llm_client, fallback=fallback)
