# 04. 日次シミュレーション設計

## 1. 目的

この文書は、1 日分の世界生成を担当するモジュール群の責務境界を定義する。対象は以下である。

- World Orchestrator
- Character Agents
- Environment Agent
- Perception Filter

## 2. 日次パイプライン

1 日の処理順は以下を `MUST` 基本形とする。

1. 前日状態の読込
2. 当日 Story 制約の読込
3. World Orchestrator によるその日の真実世界生成
4. Character Agents による人物行動計画生成
5. Environment Agent による環境ノイズ注入
6. 真実イベント列の確定
7. Perception Filter による観測断片への変換
8. 後段モジュールへの引き渡し

この順序を変える場合、`Observed World` が先にあり `World Truth` を後付けする構造にはしてはならない。

## 3. World Orchestrator

### 3.1 責務

- Story Planner の日別制約を満たす世界イベントの骨格を作る。
- 主要イベントと補助イベントの因果順序を決める。
- 介入前の真実状態を定義する。
- hidden developments を保持する。

### 3.2 入力

- `week_plan`
- `previous_day_state`
- `active_threads`
- `seed`

### 3.3 出力

- `day_world_frame`
- `candidate_truth_events`
- `hidden_developments`

### 3.4 契約

- 主要イベントは 2 件以上 `MUST` 存在する。
- 少なくとも 1 件は中心誤解に関わるイベントであることを `MUST` とする。
- 補助イベントは主要イベントを覆い隠すノイズとして機能してよいが、主筋を破壊してはならない。

## 4. Character Agents

### 4.1 責務

- A/B/C 各人物の当日目的を決める。
- 私的事情にもとづく行動候補を作る。
- 他人物との距離感の変化を提案する。

### 4.2 入力

- `character_state_previous`
- `day_world_frame`
- `story_role_constraints`

### 4.3 出力

- `behavior_plan`
- `emotional_state`
- `relationship_shift`

### 4.4 契約

- A/B/C は主人公のために行動してはならない。
- `behavior_plan` は private state によって説明可能でなければならない。
- Day 1 から Day 7 へ向けて、変化量は段階的であることを `SHOULD` とする。

## 5. Environment Agent

### 5.1 責務

- 環境ノイズを生成する。
- 社会ノイズと認知ノイズを追加する。
- 観測密度の偏りを作る。

### 5.2 代表ノイズ

- 環境ノイズ: 雨、混雑、照明変化、閉館前の慌ただしさ
- 社会ノイズ: 他利用者の滞留、偶然の遮蔽、別目的利用者の介在
- 認知ノイズ: ログ欠落、人物同定の曖昧さ、推測誘発的な断片

### 5.3 契約

- ノイズは因果破壊の免罪符にしてはならない。
- ノイズは `Observed World` の曖昧さを増やしてよいが、`World Truth` まで不定にしてはならない。

## 6. Truth Event 確定

`World Orchestrator` と `Character Agents` と `Environment Agent` の結果を統合し、その日の真実イベント列を確定する。

Truth Event 列は以下を満たすこと。

- 時系列順であること。
- 各イベントに actor と location があること。
- A/B/C の private motive と矛盾しないこと。
- 後続の Perception Filter が観測断片を作れるだけの observable signal を持つこと。

## 7. Perception Filter

### 7.1 責務

- 真実イベント列を、`Lumen` が観測可能な断片に変換する。
- 欠落情報を明示的に生成する。
- 曖昧さを含んだ観測文を作る。

### 7.2 入力

- `truth_events`
- `environment_noise`
- `sensor_constraints`
- `identity_ambiguity_profile`

### 7.3 出力

- `observed_events`
- `missing_information_report`
- `entity_resolution_candidates`

### 7.4 契約

- 会話内容を観測結果へ含めることは `MUST NOT`。
- 人物識別は deterministic な真名参照に落としてはならない。
- 真実の 100% を観測に写像してはならない。
- 少なくとも 1 つは誤読の余地を持つ観測を含めることを `SHOULD` とする。

## 8. 日次出力の最低形

```json
{
  "day_index": 4,
  "truth_events": [],
  "observed_events": [],
  "character_states": {},
  "environment_state": {},
  "hidden_developments": []
}
```

## 9. 検証観点

- `Observed World` だけを見ると、主人公の誤解がもっともらしく見えるか。
- `World Truth` まで見ると、その誤解が誤りだと説明できるか。
- 介入前の世界がすでに破綻していないか。
- C が説明役になりすぎていないか。
