# Phase 5: ML Baseline

Phase 5 では、rule-based scoring と ML-based scoring を同じ評価パイプラインで比較する。

重要なのは、ML を導入しても流れを変えないことである。

```text
feature row -> scoring function -> risk_score -> threshold sweep -> error analysis
```

rule-based scoring では、人間が条件と重みを決める。

ML baseline では、logistic regression が feature row から abuse probability を出す。その probability を 0 から 100 の `risk_score` に変換する。

## このフェーズで作った境界

`train_ml_baseline(feature_rows)` は、学習時に `label_value` を使う。

一方で、学習済みの `MLScoringModel.score_row(features)` は `label_value` を読まない。これは既存の `scoring_fn` と同じく、feature row だけから `risk_score` を返す関数として扱うためである。

## なぜ logistic regression から始めるか

logistic regression は、最初の ML baseline として十分に小さい。

複雑なモデルを使う前に、次の点を確認できる。

* ML model も `risk_score` を返す関数として扱える
* 既存の `evaluate_feature_rows` に `score_fn=model.score_row` を渡せる
* threshold sweep と false positive / false negative の観察を再利用できる
* 小さい fixture では、モデル性能より評価の形を学ぶことが重要である

## 注意点

今回の notebook では、同じ fixture CSV で学習と評価を行う。

これは学習用の最小 baseline としては分かりやすいが、性能を楽観的に見やすい。実務では train / validation を分け、未来情報の混入や negative sampling の設計も確認する必要がある。

## ファイルベースの保存

実行中の変数にある `ml_model` は、Python process が終了すると消える。

そのため、学習と評価を別の実行に分けるには、学習済みモデルを artifact として保存する。

このリポジトリでは、最小構成として次のファイルを作る。

```text
models/ml_baseline_v001/
  model.joblib
  metadata.json
```

`model.joblib` は scikit-learn pipeline を含む学習済みモデルである。

`metadata.json` は、人間が後から読むための説明である。model version、training data、feature columns、threshold=80 での precision / recall などを保存する。

`models/*/` は `.gitignore` している。これは、生成された model artifact を Git に直接入れないためである。リポジトリには保存先の形だけを `models/.gitkeep` で残す。

学習して保存するには次を実行する。

```bash
.venv/bin/python scripts/train_ml_baseline.py
```

この script は、fixture rows を train と validation に分ける。

default では、70% を train、30% を validation にする。モデルは train rows だけで学習し、`metadata.json` の precision / recall は validation rows で計算する。

保存済みモデルを読み込んで評価するには次を実行する。

```bash
.venv/bin/python scripts/evaluate_saved_ml_model.py
```

保存済みモデルを validation rows だけで評価するには次を実行する。

```bash
.venv/bin/python scripts/evaluate_saved_ml_model.py --validation-only
```

この分離により、次の違いを体験できる。

* training script は `label_value` を使ってモデルを作る
* evaluation script は保存済みモデルを読み込み、`score_fn=model.score_row` として使う
* scoring 時には `label_value` を読まず、feature row だけから `risk_score` を出す

## Train / Validation Split

同じ fixture rows で学習と評価を両方行うと、評価結果が楽観的に見えやすい。

そこで、`split_train_validation` で labeled feature rows を train と validation に分ける。

```text
feature rows
  ↓
train rows: モデル学習に使う
validation rows: 学習後の評価に使う
```

この分割は `label_value` の比率が大きく崩れないように stratify する。

今回の fixture は100行で、正例50行、負例50行である。default の `validation_size=0.3` では、train 70行、validation 30行に分かれる。

ただし、これはまだ実務評価としては最小形である。実務では、時間で分ける、ユーザー単位で分ける、攻撃キャンペーン単位の偏りを避ける、などを考える必要がある。
