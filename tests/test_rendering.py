from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from lumen_diary.pipeline import WeeklyDiaryPipeline
from lumen_diary.rendering import DiaryRenderer
from lumen_diary.storage import RunStorage


class RenderingTests(unittest.TestCase):
    def test_pipeline_writes_markdown_html_and_week_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = WeeklyDiaryPipeline(storage=RunStorage(Path(tmpdir)), renderer=DiaryRenderer())
            week_plan, records = pipeline.run_week(seed=42)
            self.assertEqual(len(records), 7)

            day1_dir = Path(tmpdir) / week_plan.week_run_id / "days" / "day-01"
            self.assertTrue((day1_dir / "diary.md").exists())
            self.assertTrue((day1_dir / "diary.html").exists())
            markdown = (day1_dir / "diary.md").read_text(encoding="utf-8")
            html = (day1_dir / "diary.html").read_text(encoding="utf-8")
            self.assertIn("## 観測", markdown)
            self.assertIn("<h2>観測</h2>", html)
            self.assertIn(records[0].diary_entry.interpretation, markdown)
            self.assertIn(records[0].diary_entry.closing_shift, markdown)
            self.assertNotIn("実際の露出", markdown)
            self.assertNotIn("話したいが", markdown)

            run_dir = Path(tmpdir) / week_plan.week_run_id
            self.assertTrue((run_dir / "index.md").exists())
            self.assertTrue((run_dir / "index.html").exists())
            index_markdown = (run_dir / "index.md").read_text(encoding="utf-8")
            self.assertIn("7日間日記インデックス", index_markdown)
            self.assertIn("- Day 1: 一日目の記録", index_markdown)


if __name__ == "__main__":
    unittest.main()
