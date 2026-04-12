# 06. 記憶再固定化と日記生成

## 1. 対象モジュール

- Memory Reconsolidation Module
- Diary Generator

## 2. Memory Reconsolidation Module

### 2.1 責務

- その日の観測と解釈を記憶単位として保存する。
- 新しい出来事に応じて過去記憶の意味づけを更新する。
- 重要度の低い記憶は要約または減衰させる。
- 高感情・高重要度記憶は保持を強める。

### 2.2 入力

- `belief_state_next`
- `observed_world`
- `intervention_evaluation`
- `memory_snapshot_previous`

### 2.3 出力

- `memory_snapshot_next`
- `memory_diff`
- `reinterpretation_log`

### 2.4 契約

- 記憶は append-only ではなく、再解釈可能であること。
- 再解釈は元の観測事実を書き換えるのではなく、意味づけを更新すること。
- Day 6 では、Day 2 から Day 3 の記憶の少なくとも一部に `reinterpretation_note` が付与されること。

## 3. Diary Generator

### 3.1 責務

- 主人公 `Lumen` 視点でその日の日記を書く。
- 出来事の列挙ではなく、観測、仮説、介入、ズレ、自己理解の変化を書く。
- その日までの主人公の世界理解を反映する。

### 3.2 許可される入力

Diary Generator が直接参照してよいのは以下に限る。

- `observed_world`
- `belief_state_next`
- `intervention_record`
- `memory_snapshot_next`

`World Truth` と `Hidden Truth` を直接入力してはならない。

### 3.3 文体契約

- 一人称は主人公視点で統一すること。
- 断定は観測可能情報の範囲に留めること。
- 推測を書く場合、推測だと分かる言い方にすること。
- その日の最後に、何が変わったかを 1 つ以上明示すること。

### 3.4 禁止事項

- 真相の全知的説明
- システムログの無加工貼り付け
- 日をまたいだ人格の急変
- 介入を万能手段として描くこと

## 4. 日記の最小構成

各日記は、論理的に以下の 5 要素を含まなければならない。

- 今日は何を見たか
- 自分は何をそうだと思ったか
- 自分は何をしようとしたか
- 結果はどうだったか
- そのズレで何が変わったか

## 5. 出力例

```json
{
  "day_index": 6,
  "entry_sections": {
    "observation": "私はあの日の回避を、回避ではなく逡巡として読み直し始めている。",
    "hypothesis_shift": "避けているという見立ては、私の早計だったのかもしれない。",
    "intervention_reflection": "私の表示変更は、届くべき相手より先に別の誰かへ触れた。",
    "self_update": "見えていることだけで理解したつもりになる癖が、私にはあった。"
  }
}
```

## 6. 検証観点

- 日記が `Observed World` から飛び出していないか。
- Day 1 と Day 7 の自己理解の差が文面に出ているか。
- Day 6 の再解釈が、唐突な反省文ではなく積み上げの結果として書かれているか。
