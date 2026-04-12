from __future__ import annotations

from html import escape

from .domain import DiaryEntry, WeekPlan


class DiaryRenderer:
    """Render diary entries into fixed markdown and HTML formats."""

    def render_markdown(self, entry: DiaryEntry) -> str:
        observed_lines = "\n".join(f"{index}. {fact}" for index, fact in enumerate(entry.observed_facts, start=1))
        return "\n".join(
            [
                f"# {entry.title}",
                "",
                f"- Day: {entry.day_index}",
                "",
                "## 観測",
                observed_lines,
                "",
                "## 仮説",
                entry.interpretation,
                "",
                "## 介入",
                entry.attempted_action,
                "",
                "## 結果",
                entry.outcome,
                entry.intervention_reflection,
                "",
                "## 変化",
                entry.closing_shift,
                "",
            ]
        )

    def render_html(self, entry: DiaryEntry) -> str:
        observed_items = "".join(f"<li>{escape(fact)}</li>" for fact in entry.observed_facts)
        return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(entry.title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f5f1e8;
      --paper: #fffdf8;
      --ink: #1f2a2f;
      --muted: #5b6662;
      --line: #d8d0c1;
      --accent: #9b6b3d;
    }}
    body {{
      margin: 0;
      background: linear-gradient(180deg, #efe7d7 0%, var(--bg) 45%, #ece7de 100%);
      color: var(--ink);
      font-family: Georgia, "Hiragino Mincho ProN", serif;
    }}
    main {{
      max-width: 860px;
      margin: 0 auto;
      padding: 40px 20px 80px;
    }}
    article {{
      background: var(--paper);
      border: 1px solid var(--line);
      box-shadow: 0 16px 50px rgba(31, 42, 47, 0.08);
      padding: 32px 28px;
    }}
    h1, h2 {{
      font-weight: 600;
      letter-spacing: 0.04em;
    }}
    h1 {{
      margin-top: 0;
      margin-bottom: 12px;
      font-size: clamp(2rem, 4vw, 2.8rem);
    }}
    h2 {{
      margin-top: 28px;
      border-top: 1px solid var(--line);
      padding-top: 18px;
      font-size: 1.1rem;
      color: var(--accent);
    }}
    dl {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px 16px;
      margin: 0 0 20px;
      color: var(--muted);
    }}
    dt {{
      font-weight: 700;
    }}
    dd {{
      margin: 0;
    }}
    p, li {{
      line-height: 1.8;
      font-size: 1rem;
    }}
  </style>
</head>
<body>
  <main>
    <article>
      <h1>{escape(entry.title)}</h1>
      <dl>
        <dt>Day</dt><dd>{entry.day_index}</dd>
      </dl>
      <h2>観測</h2>
      <ol>{observed_items}</ol>
      <h2>仮説</h2>
      <p>{escape(entry.interpretation)}</p>
      <h2>介入</h2>
      <p>{escape(entry.attempted_action)}</p>
      <h2>結果</h2>
      <p>{escape(entry.outcome)}</p>
      <p>{escape(entry.intervention_reflection)}</p>
      <h2>変化</h2>
      <p>{escape(entry.closing_shift)}</p>
    </article>
  </main>
</body>
</html>
"""

    def render_week_index_markdown(self, week_plan: WeekPlan, entries: list[DiaryEntry]) -> str:
        lines = [
            "# 7日間日記インデックス",
            "",
            f"- Week Run ID: {week_plan.week_run_id}",
            f"- Theme: {week_plan.weekly_theme}",
            f"- Central Misunderstanding: {week_plan.central_misunderstanding}",
            "",
            "## Days",
        ]
        for entry in entries:
            lines.append(f"- Day {entry.day_index}: {entry.title}")
        lines.append("")
        return "\n".join(lines)

    def render_week_index_html(self, week_plan: WeekPlan, entries: list[DiaryEntry]) -> str:
        items = "".join(
            f"<li>Day {entry.day_index}: {escape(entry.title)}</li>"
            for entry in entries
        )
        return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>7日間日記インデックス</title>
  <style>
    body {{
      margin: 0;
      font-family: Georgia, "Hiragino Sans", sans-serif;
      background: #f5f1e8;
      color: #1f2a2f;
    }}
    main {{
      max-width: 780px;
      margin: 0 auto;
      padding: 48px 20px 72px;
    }}
    section {{
      background: #fffdf8;
      border: 1px solid #d8d0c1;
      padding: 28px;
    }}
    li {{ line-height: 1.8; }}
  </style>
</head>
<body>
  <main>
    <section>
      <h1>7日間日記インデックス</h1>
      <p>Week Run ID: {escape(week_plan.week_run_id)}</p>
      <p>Theme: {escape(week_plan.weekly_theme)}</p>
      <p>Central Misunderstanding: {escape(week_plan.central_misunderstanding)}</p>
      <h2>Days</h2>
      <ol>{items}</ol>
    </section>
  </main>
</body>
</html>
"""
