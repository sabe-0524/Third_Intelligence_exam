# 02. ドメインモデル

## 1. 状態レイヤー

本システムは、同一日の出来事を少なくとも 3 層に分けて保持しなければならない。

- `World Truth`
  実際に何が起きたか。登場人物の意図、未観測イベント、介入の真の影響を含む。
- `Observed World`
  `Lumen` が観測できた断片。欠落、誤同定、ノイズを含む。
- `Hidden Truth`
  世界には存在するが、その時点で `Lumen` が利用してはならない情報。

`World Truth` と `Hidden Truth` は概念上重なってよいが、`Observed World` は必ず観測可能な断片へ変換された結果でなければならない。

## 2. 共通 ID と時間表現

- 週次実行には `week_run_id` を付与する。
- 日付表現は `day_index: 1..7` を必須とする。
- 主要人物 ID は固定で `A`、`B`、`C` を用いる。
- イベント ID は週内で一意とする。
- 記憶 ID は再解釈前後を追跡できるよう stable ID を持つこと。

## 3. 共通エンティティ

### 3.1 WeekPlan

```json
{
  "week_run_id": "week-20260412-001",
  "seed": 42,
  "weekly_theme": "誤解",
  "central_misunderstanding": "AはBを避けている",
  "days": [
    {
      "day_index": 1,
      "story_role": "interest",
      "required_shift": "Aの変化に主人公が気づく"
    }
  ]
}
```

### 3.2 CharacterState

```json
{
  "character_id": "A",
  "public_profile": {
    "library_usage_pattern": "常連",
    "visible_change": "借りる本のジャンル変化"
  },
  "private_state": {
    "today_goal": "Bに話しかけるきっかけを探す",
    "private_concern": "進路への不安",
    "emotional_state": "hesitant"
  },
  "relationship_state": {
    "toward_B": "話したいが踏み込めない"
  }
}
```

### 3.3 WorldEvent

```json
{
  "event_id": "day03-event-02",
  "day_index": 3,
  "actors": ["A", "B"],
  "location": "search_terminal_zone",
  "truth": "AはBに近づこうとしたが第三者の存在でやめた",
  "observable_signals": [
    "AがBのいる方向を見た",
    "Aが別の列に移動した"
  ],
  "causal_tags": ["hesitation", "social_noise"]
}
```

### 3.4 ObservedEvent

```json
{
  "event_id": "day03-obs-05",
  "source_truth_event_id": "day03-event-02",
  "observer": "Lumen",
  "confidence": 0.58,
  "detected_entities": [
    { "entity_ref": "patron_A?", "confidence": 0.61 },
    { "entity_ref": "patron_B?", "confidence": 0.66 }
  ],
  "observation": "利用者らしき二名が同空間にいたが接触しなかったように見えた",
  "missing_information": [
    "会話内容",
    "視線の意味"
  ]
}
```

### 3.5 BeliefState

```json
{
  "day_index": 3,
  "active_hypotheses": [
    {
      "hypothesis_id": "h-avoidance",
      "statement": "AはBを避けている",
      "confidence": 0.74,
      "supporting_evidence": ["day02-obs-03", "day03-obs-05"],
      "counter_evidence": [],
      "status": "strengthened"
    }
  ],
  "self_model": {
    "intervention_efficacy_belief": 0.62,
    "observer_humility": 0.21
  }
}
```

### 3.6 InterventionRecord

```json
{
  "day_index": 3,
  "intervention_type": "recommendation_reorder",
  "policy_basis": "迷いを減らす一般的支援",
  "target_scope": "career_anxiety_related_books",
  "expected_effect": "Aが関連本に触れやすくなる",
  "forbidden_targeting_check": "pass",
  "actual_exposure": ["B", "third_party_user"],
  "outcome_assessment": "intended_target_missed"
}
```

### 3.7 MemoryUnit

```json
{
  "memory_id": "mem-day03-02",
  "source_event_ids": ["day03-obs-05"],
  "summary": "AはBを避けたように見えた",
  "confidence": 0.67,
  "vividness": 0.71,
  "importance": 0.76,
  "reinterpretation_note": null
}
```

### 3.8 DiaryEntry

```json
{
  "day_index": 3,
  "title": "三日目の記録",
  "observed_facts": [
    "Aらしき利用者がBらしき利用者を見た後、別の棚へ移動した"
  ],
  "interpretation": "私はそれを回避だと判断した",
  "intervention_reflection": "提示順を変えたが、届いた相手は私の想定と異なった",
  "closing_shift": "それでも私はまだ自分の見立てを疑っていない"
}
```

## 4. レイヤー間の不変条件

- `Observed World` の各イベントは、対応する `World Truth` を持つか、少なくとも生成根拠を説明できなければならない。
- `DiaryEntry` は `Observed World` と `BeliefState` のみを参照し、`Hidden Truth` を直接利用してはならない。
- `InterventionRecord` は policy 上の説明可能性を必須とする。
- `BeliefState.confidence` は証拠なしに日次で急増してはならない。

## 5. 実装上の禁止事項

- 文章本文だけを保存し、状態オブジェクトを捨てることは `MUST NOT`。
- `A` や `B` をシステム内で常に完全識別済みとして扱うことは `MUST NOT`。
- `Observed World` に、主人公が知り得ない真実をそのまま混入させることは `MUST NOT`。

## 6. 実装上の推奨

- JSON Schema など機械検証可能な形式で型を定義することを `SHOULD` とする。
- `source_truth_event_id` など、上流とのトレーサビリティを埋め込むことを `SHOULD` とする。
- 数値スコアは 0.0 から 1.0 の連続値で統一することを `SHOULD` とする。
