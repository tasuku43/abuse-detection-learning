# Phase 6: Scoring Versioning

Scoring versioning は、評価結果がどの scoring function または model から出たものかを追えるようにするための仕組みである。

`risk_score = 87` だけを保存しても、後から次のことが分からない。

* rule-based score なのか ML score なのか
* どの version の rule / model なのか
* 同じ row を今の model で再評価したら同じ score になるのか

## 今回の実装

`ScoreSource` を追加し、評価時に `score_source` と `score_version` を付けられるようにした。

```python
ScoreSource(name="rule_based", version="rule_baseline_v001")
```

これを `evaluate_feature_rows` に渡すと、scored rows と metrics の両方に次の列が入る。

```text
score_source
score_version
```

ML model の場合は、`models/ml_baseline_v001/metadata.json` から `model_name` と `model_version` を読み込んで `ScoreSource` に変換する。

## なぜ必要か

不正検知では、後から false positive / false negative を調べることが多い。

そのとき、どの version がその判定を出したのかが分からないと、改善の比較ができない。

```text
same feature row
  -> rule_baseline_v001 score
  -> ml_baseline v001 score
  -> future_model v002 score
```

このように並べて初めて、model の変更が誤検知や見逃しにどう影響したかを追える。

## 今回やらないこと

このリポジトリでは、本格的な model registry は作らない。

まずは評価結果に `score_source` と `score_version` が残ることを確認する。
