# 図書館観測AI 7日間日記システム仕様群

このディレクトリは、[元の設計メモ](/Users/abesouichirou/Documents/third_exam/docs/multi_agent_world_diary_design.md) を、実装時の判断を揺らさないための要件書・設計書へ分解した正本である。

目的は「雰囲気の良い設計メモ」を残すことではなく、実装者がどこまで自由に決めてよく、どこから先は勝手に変えてはいけないかを明文化することにある。

## 契約語

- `MUST`: 実装必須。満たさない実装は不適合とみなす。
- `SHOULD`: 強い推奨。理由なく外してはいけない。
- `MUST NOT`: 禁止。実装意図を壊すため採用不可。

## 読み順

1. [01-system-requirements.md](/Users/abesouichirou/Documents/third_exam/docs/multi-agent-world-diary/01-system-requirements.md)
2. [02-domain-model.md](/Users/abesouichirou/Documents/third_exam/docs/multi-agent-world-diary/02-domain-model.md)
3. [03-weekly-story-planner.md](/Users/abesouichirou/Documents/third_exam/docs/multi-agent-world-diary/03-weekly-story-planner.md)
4. [04-daily-simulation.md](/Users/abesouichirou/Documents/third_exam/docs/multi-agent-world-diary/04-daily-simulation.md)
5. [05-belief-and-intervention.md](/Users/abesouichirou/Documents/third_exam/docs/multi-agent-world-diary/05-belief-and-intervention.md)
6. [06-memory-and-diary.md](/Users/abesouichirou/Documents/third_exam/docs/multi-agent-world-diary/06-memory-and-diary.md)
7. [07-consistency-and-regeneration.md](/Users/abesouichirou/Documents/third_exam/docs/multi-agent-world-diary/07-consistency-and-regeneration.md)
8. [08-runtime-and-module-contracts.md](/Users/abesouichirou/Documents/third_exam/docs/multi-agent-world-diary/08-runtime-and-module-contracts.md)

## 文書マップ

- [01-system-requirements.md](/Users/abesouichirou/Documents/third_exam/docs/multi-agent-world-diary/01-system-requirements.md)
  この作品の固定設定、スコープ、非スコープ、成果物、受け入れ基準を定義する。
- [02-domain-model.md](/Users/abesouichirou/Documents/third_exam/docs/multi-agent-world-diary/02-domain-model.md)
  状態レイヤー、共通エンティティ、ID と JSON 契約を定義する。
- [03-weekly-story-planner.md](/Users/abesouichirou/Documents/third_exam/docs/multi-agent-world-diary/03-weekly-story-planner.md)
  7日間全体のアークを固定する Story Planner の責務と出力を定義する。
- [04-daily-simulation.md](/Users/abesouichirou/Documents/third_exam/docs/multi-agent-world-diary/04-daily-simulation.md)
  World Orchestrator、Character Agents、Environment Agent、Perception Filter を含む日次生成の責務を定義する。
- [05-belief-and-intervention.md](/Users/abesouichirou/Documents/third_exam/docs/multi-agent-world-diary/05-belief-and-intervention.md)
  仮説更新、介入計画、実行、評価の契約と禁止事項を定義する。
- [06-memory-and-diary.md](/Users/abesouichirou/Documents/third_exam/docs/multi-agent-world-diary/06-memory-and-diary.md)
  記憶の再固定化と日記生成の入力、出力、文体制約を定義する。
- [07-consistency-and-regeneration.md](/Users/abesouichirou/Documents/third_exam/docs/multi-agent-world-diary/07-consistency-and-regeneration.md)
  整合性検証、エラー分類、再生成ポリシーを定義する。
- [08-runtime-and-module-contracts.md](/Users/abesouichirou/Documents/third_exam/docs/multi-agent-world-diary/08-runtime-and-module-contracts.md)
  ランタイム構成、モジュール境界、永続化、禁止アーキテクチャを定義する。

## 実装原則

- 物語本文と状態遷移を分離し、先に状態を確定させてから日記を書くこと。
- 各モジュールは構造化データを入出力し、自然言語だけを唯一の状態源にしないこと。
- `World Truth`、`Observed World`、`Hidden Truth` を混同しないこと。
- 主人公の介入は常に制度的に説明可能でなければならず、露骨な個別誘導をしてはならないこと。
- 整合性エラーを日記生成でごまかさず、原因段階まで戻って再生成すること。

## 元メモとの関係

- [multi_agent_world_diary_design.md](/Users/abesouichirou/Documents/third_exam/docs/multi_agent_world_diary_design.md)
  構想の出発点。世界観やテーマの意図を確認するために参照してよい。
- この仕様群
  実装時に従う正本。競合した場合は、この仕様群を優先する。
