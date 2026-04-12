from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from lumen_diary.domain import WeekPlan
from lumen_diary.pipeline import StoryPlanner, WeeklyDiaryPipeline
from lumen_diary.storage import RunStorage


class PipelineTests(unittest.TestCase):
    def test_story_planner_returns_seven_days_in_contract_order(self) -> None:
        planner = StoryPlanner()
        plan = planner.plan_week(seed=42)
        self.assertEqual(len(plan.days), 7)
        self.assertEqual(
            [day.story_role for day in plan.days],
            [
                "interest",
                "misunderstanding",
                "reinforcement",
                "crack",
                "reversal_sign",
                "reinterpretation",
                "afterglow",
            ],
        )

    def test_weekly_pipeline_produces_required_state_transitions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = WeeklyDiaryPipeline(storage=RunStorage(Path(tmpdir)))
            week_plan, records = pipeline.run_week(seed=42)
            self.assertEqual(len(records), 7)
            self.assertTrue((Path(tmpdir) / week_plan.week_run_id / "week_plan.json").exists())

            day2 = records[1]
            day3 = records[2]
            day6 = records[5]
            day7 = records[6]

            self.assertEqual(day2.belief_state.active_hypotheses[0].statement, "AはBを避けている")
            self.assertEqual(day3.intervention.outcome_assessment, "effect_misattributed")
            self.assertGreater(len(day6.memory_update.reinterpretation_log), 0)
            self.assertIn("Day1", day7.diary_entry.closing_shift)
            self.assertIn("finale_restraint_check", [check.check_id for check in day7.consistency_report.checks])
            self.assertGreater(len(day2.belief_state.active_hypotheses[0].supporting_evidence), 0)

            day7_dir = Path(tmpdir) / week_plan.week_run_id / "days" / "day-07"
            self.assertTrue((day7_dir / "diary_entry.json").exists())
            self.assertTrue((day7_dir / "consistency_report.json").exists())

    def test_pipeline_respects_supplied_week_plan_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            planner = StoryPlanner()
            original = planner.plan_week(seed=7)
            custom = WeekPlan(
                week_run_id=original.week_run_id + "-custom",
                seed=original.seed,
                weekly_theme=original.weekly_theme,
                central_misunderstanding=original.central_misunderstanding,
                days=list(reversed(original.days[:2])),
                character_arcs=original.character_arcs,
            )
            pipeline = WeeklyDiaryPipeline(storage=RunStorage(Path(tmpdir)))
            _, records = pipeline.run_from_week_plan(custom)
            self.assertEqual([record.day_index for record in records], [2, 1])


if __name__ == "__main__":
    unittest.main()
