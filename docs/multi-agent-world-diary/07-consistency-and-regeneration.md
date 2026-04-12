# 07. 整合性検証と再生成ポリシー

## 1. 目的

多段生成では、良い文章が出ても状態破綻が起きる。この文書は、文章の見た目で破綻を隠さないための検証ルールを定義する。

## 2. Consistency Checker の責務

- 7 日間の因果整合性を検証する。
- A/B/C の行動変化が急すぎないか確認する。
- 主人公の信念変化が観測証拠と結びついているか確認する。
- `World Truth` と `Observed World` の対応関係が壊れていないか確認する。
- 日記が全知視点へ逸脱していないか確認する。

## 3. エラー分類

### Critical

再生成が必須のエラー。

- hidden truth が日記へ直接漏れている
- 中心誤解が Day 2 以前に成立しない
- Day 6 以降も主要仮説が一切揺らがない
- 主要人物の行動が private motive と矛盾する

### Warning

再生成または人手確認を推奨するエラー。

- ノイズが弱く誤解の説得力が足りない
- 介入の副作用が薄く、テーマ表現が弱い
- C の役割が説明寄りに寄りすぎている

## 4. 最低検査項目

- `story_role_check`
- `truth_observation_mapping_check`
- `character_arc_check`
- `belief_evidence_check`
- `intervention_policy_check`
- `diary_viewpoint_check`
- `finale_restraint_check`

## 5. 再生成戦略

再生成は、原因がある最上流のフェーズからやり直す。下流だけを書き換えて整合したように見せてはならない。

### 5.1 フェーズ別ルール

- Story Planner 不整合
  Day 全体を無効化し、週計画からやり直す。
- Truth Event 不整合
  当日の World Orchestrator からやり直す。
- Observed World 不整合
  Perception Filter からやり直す。
- BeliefState 不整合
  Hypothesis Updater からやり直す。
- Diary だけの表現不良
  Diary Generator のみ再実行してよい。

### 5.2 禁止事項

- `World Truth` を変えずに都合よく日記だけ直して筋を合わせること。
- 評価を良く見せるために counter evidence を削除すること。

## 6. 検証レポート契約

```json
{
  "day_index": 6,
  "status": "warning",
  "checks": [
    {
      "check_id": "belief_evidence_check",
      "result": "fail",
      "severity": "critical",
      "message": "主要仮説の転換に十分な反証観測がない"
    }
  ],
  "recommended_rerun_from": "hypothesis_updater"
}
```

## 7. 受け入れライン

- 週全体で critical error は 0 件であること。
- warning は残ってよいが、最終成果物に反映する前に記録されていること。
- Day 7 の余韻を壊す過剰説明は `finale_restraint_check` で弾かれること。

## 8. 実装上の推奨

- 検証器は LLM に丸投げせず、構造チェックと意味チェックを分離することを `SHOULD` とする。
- 各チェックは pass/fail だけでなく、原因モジュールを返すことを `SHOULD` とする。
- 再生成回数の上限を設け、無限再試行を避けることを `SHOULD` とする。
