# 08. ランタイムとモジュール境界

## 1. 目的

この文書は、「どのように実装してよいか」の自由度を限定する。目的は実装言語を固定することではなく、1 本の巨大プロンプトに全責務を押し込んで設計意図を壊すことを防ぐことにある。

## 2. ランタイム構成

実装は詳細を自由に選べるが、論理構成として以下を分離しなければならない。

- `Application Orchestrator`
  週次実行を管理し、各モジュールの入出力を束ねる。
- `State Store`
  日次スナップショット、検証結果、再生成履歴を保存する。
- `Generation Modules`
  Story Planner、World Orchestrator、Hypothesis Updater、Diary Generator などの生成担当。
- `Validation Modules`
  構造検証と意味検証を担う。

## 3. モジュール境界

### 3.1 Orchestrator

- 実行順序を管理する。
- 上流成果物を下流へ受け渡す。
- 再生成時に戻る開始点を決める。
- hidden truth を Diary Generator へ直接渡してはならない。

### 3.2 Generation Module

- 受け取った入力のみを使って出力することを `MUST` 基本とする。
- 出力は構造化データで返すこと。
- 自然言語を返すモジュールでも、要約とは別に machine-readable なメタデータを返すことを `MUST` とする。

### 3.3 Validation Module

- 入力アーティファクトを破壊せず、検証結果のみを返す。
- pass/fail だけでなく、原因フェーズと修復開始点を返す。

## 4. 推奨インターフェース

関数名や API 名は自由だが、責務の切り方は以下に近いことを `SHOULD` とする。

```text
plan_week(input) -> week_plan
simulate_day(world_input) -> day_world_state
derive_observation(day_world_state) -> observed_world
update_beliefs(observed_world, prior_state) -> belief_state
plan_intervention(belief_state) -> intervention_plan
execute_intervention(intervention_plan, day_world_state) -> intervention_record
reconsolidate_memory(day_state, prior_memory) -> memory_state
generate_diary(observed_state_bundle) -> diary_entry
validate_day(day_artifacts) -> consistency_report
```

## 5. 永続化契約

- 各フェーズ後の成果物は上書きではなく version を持つことを `SHOULD` とする。
- 少なくとも「最新 accepted」と「再生成前の直前 version」を追跡できること。
- 日記本文だけでなく、生成に使った構造化入力も保存すること。

## 6. 秘匿情報の受け渡し契約

- `Hidden Truth` は World Orchestrator、Character Agents、Consistency Checker では利用してよい。
- `Hidden Truth` は Hypothesis Updater の直接入力にしてはならない。
- `Hidden Truth` は Diary Generator の直接入力にしてはならない。
- `Observed World` は Diary Generator の主要入力でなければならない。

## 7. 禁止アーキテクチャ

以下は設計意図に反するため採用してはならない。

- 週全体を 1 回のプロンプトで生成し、後から状態を逆算する構成
- Day ごとの真実状態を保存せず、日記本文だけを正とする構成
- Diary Generator が `World Truth` を読んだ上で「知らないふり」をする構成
- 検証器が失敗時に勝手に成果物を書き換える構成

## 8. 実装言語と依存関係

- 実装言語は固定しない。
- ただし、型定義、JSON Schema、または同等の契約記述を用いて、モジュール間データを機械検証可能にすることを `SHOULD` とする。
- LLM 依存実装であっても、検証器のすべてを LLM 任せにしてはならない。

## 9. 受け入れ観点

- Diary Generator が hidden truth 非依存で動作するか。
- 再生成時に上流成果物と下流成果物の境界が壊れていないか。
- 検証結果から rerun 開始点を一意に決められるか。
