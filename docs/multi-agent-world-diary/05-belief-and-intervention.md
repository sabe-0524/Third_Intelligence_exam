# 05. 仮説更新と介入設計

## 1. 対象モジュール

この文書は以下を対象とする。

- Hypothesis Updater
- Intervention Planner
- Action Executor
- Intervention Evaluator

## 2. Hypothesis Updater

### 2.1 責務

- その日の観測から主人公の仮説を生成または更新する。
- 仮説の強化、保留、反証、再解釈を明示的に記録する。
- 他者理解だけでなく自己理解も更新する。

### 2.2 入力

- `observed_world`
- `belief_state_previous`
- `memory_snapshot`

### 2.3 出力

- `belief_state_next`
- `hypothesis_deltas`

### 2.4 契約

- 仮説には supporting evidence と counter evidence を紐づけること。
- confidence の変化には説明根拠が必要であること。
- Day 2 では `AはBを避けている` 仮説を主要仮説として持つこと。
- Day 6 までに少なくとも 1 回、主要仮説を再解釈すること。

## 3. 介入ポリシー

介入は善意のある制度的支援として説明可能でなければならない。以下は全介入に共通する必須条件である。

- `policy_basis` を持つこと。
- `target_scope` は個人ではなく、ジャンル、棚、導線、時間帯など一般化された単位であること。
- `fairness_check` を通過すること。
- `risk` を事前に記述すること。

## 4. Intervention Planner

### 4.1 責務

- 主人公の信念にもとづいて当日の小さな介入を選ぶ。
- v1 では、許可された介入手段の中から 1 日あたり 0 件または 1 件を選ぶ。
- 想定効果と副作用仮説を定義する。

### 4.2 許可される介入

- 推薦本提示順変更
- 特集表示変更
- 関連棚強調
- 空席案内調整
- 通知タイミング調整

### 4.3 禁止される介入

- `A向け`、`B向け` のような個人名や個人推定ラベル付きの最適化
- 接触を直接促すような露骨な誘導
- 公平性理由を説明できない特例処理

## 5. Action Executor

### 5.1 責務

- 計画された介入を世界状態へ反映する。
- 介入による露出機会の変化を記録する。
- 後段の評価が可能なように実行ログを残す。

### 5.2 契約

- 実行ログは `planned_effect` と `actual_exposure` を分けて持つこと。
- 実行後の世界変化は `World Truth` 側へ反映されること。

## 6. Intervention Evaluator

### 6.1 責務

- 介入が誰にどう届いたかを評価する。
- 意図とのズレを分類する。
- 主人公の自己理解へフィードバックする。

### 6.2 最低評価項目

- `intended_target_reached`
- `unintended_target_reached`
- `no_visible_effect`
- `effect_misattributed`

### 6.3 契約

- 少なくとも 1 回、`unintended_target_reached` または `effect_misattributed` が起こること。
- 評価は主人公が知る評価と、真実としての評価を分けて持つことを `SHOULD` とする。

## 7. 仮説と介入の関係

- 主人公は誤った仮説にもとづき介入してよい。
- ただし、システム実装はその誤りを trace 可能にしなければならない。
- 介入後に仮説が強化されたとしても、それが偶然か因果かを evaluator で区別しなければならない。

## 8. 最低出力例

```json
{
  "day_index": 5,
  "selected_intervention": {
    "type": "feature_shelf_highlight",
    "policy_basis": "進路に迷う利用者全体への支援",
    "target_scope": "career_and_transition_books",
    "risk": "Bや第三者にも同等に露出する"
  },
  "evaluation": {
    "actual_exposure": ["B"],
    "outcome": "unintended_target_reached"
  }
}
```

## 9. 検証観点

- 介入がなくても物語が成立する日と、介入が効く日が区別されているか。
- 主人公の善意が制度制約の中でしか表現されていないか。
- 介入評価が後知恵の omniscient narration になっていないか。
