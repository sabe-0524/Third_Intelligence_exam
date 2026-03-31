# 複数エージェントによる世界再現型・7日間日記生成システム設計書

## 1. 概要

本システムは、主人公が日記を書くこと自体を目的とするのではなく、**主人公と独立した外部世界を複数エージェントでシミュレーションし、その世界との相互作用から7日間の日記を生成する**ことを目的とする。

従来の日記生成では、以下のような問題が起きやすい。

* 世界が主人公都合で動いてしまう
* 1日ごとの出来事が独立しやすく、連続性が弱い
* 他者の反応が主人公のための装置になりやすい
* 主人公の変化が単なる感情ログに留まりやすい

そこで本設計では、以下の思想を採用する。

1. **主人公と世界を分離する**
2. **世界の真実と主人公が観測した世界を分離する**
3. **他者に他者自身の事情を持たせる**
4. **主人公は毎日、世界に対する仮説を立て、その仮説が更新される**
5. **記憶は保存されるだけでなく、忘却・再解釈・歪みを伴って更新される**

これにより、単なる「日記生成器」ではなく、**不完全な観測者が独立した世界をどう理解し損ね、どう変化していくかを記述する物語生成システム**として成立させる。

---

## 2. 目的

### 2.1 内容面の目的

* 7日間を通して読者が連続的な人格変化を感じられる日記を生成する
* 主人公の視点の偏り・誤解・期待・失望を表現する
* 単発イベントの面白さではなく、世界理解の変化を物語の核にする

### 2.2 技術面の目的

* 複数エージェントで主人公と独立した世界を再現する
* world state / observed state / hidden state を分離する
* 他者エージェント・環境エージェント・世界オーケストレータを分担させる
* 信念更新、仮説形成、忘却、整合性チェックを含む多段生成パイプラインを構築する
* 軽量LLMを中心に構成し、無料〜低コストで運用可能にする

---

## 3. コアアイデア

本システムの中心となるアイデアは以下の4点である。

### 3.1 主人公と世界の分離

主人公は世界の一部しか見えない。
一方で世界は、主人公の意図に従属せず、独自に進行する。

### 3.2 真実世界と観測世界の分離

各日には以下の3層を持たせる。

* **World Truth**: 実際に何が起きたか
* **Observed World**: 主人公が観測できた断片
* **Hidden Truth**: その時点では主人公にも読者にも見えない潜在的事情

これにより、誤解・すれ違い・伏線を自然に生成できる。

### 3.3 仮説形成と信念更新

主人公は毎朝または毎晩、世界について仮説を立てる。

例:

* Aは自分を避けているのではないか
* 雨の日は人は少し優しいのではないか
* 自分は当事者ではなく観察者に過ぎないのではないか

その仮説は、実際の観測とズレることで更新される。
日記は出来事そのものよりも、**仮説がどう揺れたか**を中心に書かれる。

### 3.4 記憶の再固定化

記憶は append-only で保存されるのではなく、以下のような変形を受ける。

* 感情の強い記憶は強調される
* 重要度の低い記憶は要約・消失する
* 新しい出来事に引っ張られて過去の解釈が変わる
* 思い出すたびに少しずつ意味づけが変わる

この仕組みにより、主人公の語りに人間的な歪みを持ち込む。

---

## 4. 全体アーキテクチャ

以下のエージェント / モジュールで構成する。

### 4.1 Protagonist Agent

主人公。

#### 役割

* 朝の予定・期待・注目対象を決める
* 観測した出来事を解釈する
* 世界について仮説を立てる
* 感情・信念・自己像を更新する
* 夜に日記を書く

#### 主な状態

* persona
* emotional state
* self model
* relationships
* short-term memory
* long-term beliefs
* active hypotheses

---

### 4.2 World Orchestrator

世界全体の因果を管理する中心モジュール。

#### 役割

* 1日の環境条件を決める
* 主イベントと小イベントを生成する
* 登場人物の都合と行動の整合性を管理する
* 世界の hidden state を保持する
* 翌日に持ち越される未解決イベントを管理する

#### 主な状態

* date / day index
* weekly theme
* world mood
* weather / environment state
* ongoing threads
* hidden truths
* scene metadata

---

### 4.3 Character Agents

頻出人物を表すエージェント群。

#### 役割

* 主人公以外の人物として独自に反応する
* その人物自身の事情に基づいて行動する
* 主人公から見たときに一貫した人格を持つ

#### 各キャラクターの状態

* personality
* current goal
* private concern
* relationship to protagonist
* recent emotional shift

---

### 4.4 Environment Agent

環境や偶発事象を扱う。

#### 役割

* 天候
* 混雑
* 遅延
* 物理的ノイズ
* 社会的ノイズ

を生成する。

#### ノイズの分類

* **環境ノイズ**: 雨、風、停電、混雑
* **社会ノイズ**: 噂、誤伝達、断片的会話
* **認知ノイズ**: 見落とし、聞き間違い、過剰解釈

---

### 4.5 Perception Filter

世界の真実を主人公の観測可能範囲に変換する。

#### 役割

* 観測可能な断片だけを抽出する
* 情報欠落を発生させる
* センサー制約・身体性を反映する
* 誤解の余地を残す

#### 例

* 音声は聞こえない
* 顔は見えるが会話内容は分からない
* 夜しか起動しない
* 定点観測なので追跡できない
* 雨天時は視界が悪化する

---

### 4.6 Memory Reconsolidation Module

記憶の再固定化を行う。

#### 役割

* 記憶の重要度を再評価する
* 過去の意味づけを更新する
* 低重要度記憶を薄める
* 高感情記憶を強調する

#### 記憶メタ情報

* vividness
* confidence
* valence
* importance
* last_recalled
* times_recalled

---

### 4.7 Consistency Checker

多段生成に伴う世界の破綻を防ぐ。

#### 役割

* 日跨ぎの人物一貫性を確認する
* 主人公の関係性変化が急すぎないか確認する
* 天候や場面変化が不自然でないか確認する
* hidden state と observed state の因果に矛盾がないか確認する

---

## 5. 状態レイヤー設計

本設計では、世界の状態を3層に分ける。

### 5.1 World Truth

世界で実際に起きたこと。
主人公に見えていない情報も含む。

例:

* Aは主人公を避けたのではなく、家族の連絡で急いでいた
* 雨のため人の流れが変わった
* Bは昨日の出来事をまだ引きずっている

### 5.2 Observed World

主人公が実際に観測できた断片。

例:

* Aと目が合ったがすぐ去った
* 人がいつもより急いでいた
* Bは無言だった

### 5.3 Hidden Truth

その時点では顕在化していない潜在的事情。
数日後の出来事でにじみ出る可能性がある。

例:

* Aは進路の悩みを抱えていた
* Bは主人公を誤解している
* 世界側では中盤に観測不能期間が来ることが決まっている

---

## 6. 1日の処理フロー

1日を以下の8フェーズで処理する。

### Phase 1: Morning Plan

主人公がその日の計画を立てる。

出力:

* 今日の目標
* 会いたい相手
* 避けたいこと
* 今日起きそうだと思うこと
* 現在の仮説

### Phase 2: World Expansion

World Orchestrator がその日の主要イベントを生成する。

出力:

* weather
* main event
* minor event
* background noise
* relevant hidden developments

### Phase 3: Character Reactions

必要な人物だけ Character Agents を呼び、私的事情に基づく行動や反応を生成する。

出力:

* character intent
* character action
* emotional stance
* hidden motivations

### Phase 4: Environment Injection

Environment Agent が外的ノイズを注入する。

出力:

* environmental disturbances
* schedule shifts
* ambiguity factors

### Phase 5: Perception Filtering

主人公に観測可能な情報へ変換する。

出力:

* visible cues
* missing information
* ambiguous signals
* protagonist-facing event summary

### Phase 6: Hypothesis Update

主人公が観測結果を元に仮説と信念を更新する。

出力:

* strengthened hypotheses
* weakened hypotheses
* new hypotheses
* emotional movement
* self-model change

### Phase 7: Diary Writing

主人公が日記本文を書く。

出力:

* diary text

### Phase 8: Memory Reconsolidation & Consistency Check

記憶と世界状態を更新し、次の日へ持ち越す。

出力:

* updated protagonist state
* updated world state
* updated relationships
* reconciled memory set
* verified daily log

---

## 7. 7日間全体の構造

7日間を単なる日次ループではなく、1週間のアークとして設計する。

### 7.1 週テーマ

週全体に1つテーマを持たせる。

例:

* 誤解
* 待つこと
* 名前を持つこと
* 役割と本音
* 見えているのに分からないこと

各日のイベントは、このテーマの変奏として現れる。

### 7.2 変化軸

7日間で少しずつ変える軸を固定する。

* 他者への見方
* 自己像
* 期待の仕方
* 孤独と接続のバランス

### 7.3 中盤の転換点

4日目前後に世界側のルールや観測条件を少し変化させる。

例:

* 観測対象だった人物が現れなくなる
* 主人公の観測範囲が一時的に変わる
* 環境ノイズが増える
* hidden truth の一部がにじみ始める

### 7.4 最終日の回収

Day 7 では、主人公に Day 1 の仮説や自己像を振り返らせる。

* 最初に何を誤解していたか
* 今も分からないことは何か
* 何が変わり、何は変わらなかったか

---

## 8. 主人公設計の要件

主人公は抽象的なAIではなく、**身体性または観測制約が明確な存在**にする。

### 望ましい条件

* 観測可能範囲が限定されている
* 情報が欠けることが自然である
* 一定の場所や時間に縛られている
* 他者との距離感が構造的に決まる

### 候補例

* 図書館の観測AI
* 街灯制御AI
* 忘れ物管理AI
* 駅の案内端末AI
* 温室管理AI

---

## 9. 技術的独自性

本設計の技術的独自性は以下にある。

### 9.1 複数エージェントによる世界再現

主人公以外の人物や環境も LLM によって独立に振る舞う。
これにより、主人公の内面だけでなく、世界との衝突から物語を生成する。

### 9.2 三層状態管理

* World Truth
* Observed World
* Hidden Truth

を分離し、誤解と伏線を生成可能にする。

### 9.3 仮説形成ベースの人格更新

感情値の更新だけでなく、主人公が世界理解の仮説を形成・修正する。
これにより、日記が「感想文」ではなく「世界理解の揺れの記録」になる。

### 9.4 記憶の再固定化

記憶が毎日再構成されるため、過去の見え方が未来の出来事によって変わる。

### 9.5 整合性チェッカー

多段・多エージェント生成で壊れやすい因果整合性を、後段で検査する構造を持つ。

---

## 10. コスト最適化方針

本システムは複数回APIを呼ぶ構成であるため、低コスト化を前提とする。

### 10.1 基本方針

* 高価なモデルを全工程で使わない
* 世界生成・補助生成・要約は軽量モデルで回す
* 最終本文だけ必要に応じて高品質モデルへ切り替える

### 10.2 想定モデル運用

#### 軽量モデルで処理する工程

* world expansion
* character reactions
* environment injection
* perception filtering
* hypothesis update
* memory summarization
* consistency checking

#### より強いモデルを使う工程（必要なら）

* 最終的な日記本文生成
* 最終日の振り返り文生成

### 10.3 運用戦略

* まず全体を軽量モデルのみで構築する
* 7日分の構造が成立することを確認する
* 本文の表現力が不足した場合のみ、最終日記生成モジュールを差し替える

---

## 11. 最小実装案

### 11.1 ディレクトリ構成例

```text
project/
  data/
    protagonist.json
    world_state.json
    characters.json
    memories.json
    outputs/
  prompts/
    protagonist_plan.md
    world_orchestrator.md
    character_agent.md
    environment_agent.md
    perception_filter.md
    hypothesis_update.md
    diary_writer.md
    consistency_checker.md
  src/
    run_day.py
    run_week.py
    llm.py
    state.py
    memory.py
    update.py
    validate.py
```

### 11.2 主なJSON状態

#### protagonist.json

* persona
* emotions
* relationships
* active_hypotheses
* self_model
* short_term_memory
* long_term_beliefs

#### world_state.json

* current_day
* weekly_theme
* weather
* ongoing_threads
* hidden_truths
* scene_state

#### characters.json

* character profiles
* private concerns
* relationship states
* recent reactions

---

## 12. 出力物

各日について内部的には以下を保持する。

* morning plan
* world truth
* hidden truth
* observed world
* updated hypotheses
* diary text
* updated protagonist state
* updated world state

ただし提出物として前面に出すのは主に以下でよい。

* 7日分の日記本文
* システム構成図
* 状態レイヤー図
* 1日分の truth / observed / diary の対比例
* 工夫点と考察

---

## 13. 評価観点との対応

### 13.1 出力の面白さ

* 主人公の視点が一貫しつつ揺れる
* 他者と世界が独立しているため、予定調和にならない
* hidden truth により、読後に余韻や再解釈が生まれる

### 13.2 技術的な面白さ

* 複数エージェントで世界を再現
* 世界状態の三層分離
* 仮説形成ベースの更新
* 忘却・再解釈・整合性検証

### 13.3 実装可能性

* 軽量モデル中心で構成できる
* 多段だがモジュール責務が明確
* 最小構成でも独自性が成立する

---

## 14. 今後の拡張余地

* 他者同士の関係性も世界側で進行させる
* 日記以外に断片メモや未送信メッセージを生成する
* 主人公が自分の過去の日記を読み返し、さらに誤解を強化 / 修正する
* 観測制約を動的に変え、視点の揺らぎを導入する
* hidden truth の一部を最終日に開示し、主人公の認識との差を明示する

---

## 15. まとめ

本設計は、主人公が出来事に反応して日記を書くシステムではなく、**主人公と独立した世界を複数エージェントで生成し、その世界を不完全にしか観測できない主人公が、仮説形成・誤解・忘却を通じて変化していく過程を記述するシステム**である。

独自性は、単なる記憶管理や多エージェント化そのものではなく、以下の結合にある。

* 主人公と世界の分離
* world truth / observed world / hidden truth の三層構造
* 他者の私的事情
* 仮説形成と信念更新
* 記憶の再固定化
* 多段生成を支える整合性チェック

この構造により、7日間の日記は単なる生成結果の列ではなく、**世界理解が少しずつ変化していく連続的な記録**として成立する。
