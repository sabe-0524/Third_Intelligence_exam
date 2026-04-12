# Third_Intelligence_exam

## Lumen Diary

7 日間の図書館観測 AI 日記を生成する実装は `lumen_diary/` にあります。

### 実行

```bash
uv run python -m lumen_diary run --output-dir outputs --provider stub --seed 42
```

### LLM provider を使う場合

- `stub`
  依存なし。規則ベースで日記を生成します。
- `gemini` / `openai`
  `LUMEN_LLM_API_KEY` を設定すると日記表現の構造化生成を試みます。
  初期化や JSON 検証に失敗した場合は rule-based へ fallback します。

例:

```bash
export LUMEN_LLM_API_KEY=...
uv run python -m lumen_diary run --output-dir outputs --provider gemini --seed 42
```

### 出力

- `outputs/{week_run_id}/week_plan.json`
- `outputs/{week_run_id}/index.md`
- `outputs/{week_run_id}/index.html`
- `outputs/{week_run_id}/days/day-XX/`
  `world_truth.json`, `observed_world.json`, `belief_state.json`, `intervention.json`, `memory_update.json`, `diary_entry.json`, `diary.md`, `diary.html`, `consistency_report.json`, `state_store.json`
