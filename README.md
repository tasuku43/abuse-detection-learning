# SaaS不正検知・評価基盤 学習用リポジトリ

## このリポジトリについて

このリポジトリは本番システムではありません。

目的は、実データや本番環境を使わずに、次の基本構造を手を動かしながら理解することです。

```text
feature row -> scoring_fn -> risk_score -> threshold sweep -> precision/recall -> error analysis
```

最初は、合成データと toy example だけを使って進めます。

## 学びたいこと

このプロジェクトでは、主に次を学びます。

* feature row とは何か
* scoring_fn とは何か
* risk_score をどう出すか
* threshold を動かすと precision / recall がどう変わるか
* false positive / false negative をどう観察するか
* notebook は何のために使うのか
* dbt は特徴量生成のどこに関わるのか
* 評価基盤をどう育てていくのか

## 中心となる考え方

このプロジェクトでは、次の3つを分けて考えます。

```text
Feature Builder
  raw data / event data から feature row を作る

Scoring Function
  feature row を受け取って risk_score を返す

Evaluation Harness
  risk_score と label を比較して性能を見る
```

最初から高度な機械学習モデルを作るのではなく、まずはシンプルなルールベースの scoring function から始めます。

## 想定ディレクトリ構成

```text
abuse-detection-learning/
  README.md
  AGENTS.md
  pyproject.toml

  src/
    abuse_detection/
      __init__.py
      scoring.py
      metrics.py
      evaluation.py
      schema.py

  fixtures/
    feature_rows_sample.csv

  tests/
    test_scoring.py
    test_metrics.py
    test_evaluation.py
    test_schema.py

  notebooks/
    01_evaluate_scoring.ipynb

  dbt/
    dbt_project.yml
    models/
      staging/
        stg_account_attributes.sql
        stg_user_behavior_logs.sql
        stg_operator_action_logs.sql
      labels/
        label_events_human.sql
      features/
        evaluation_targets.sql
        fct_abuse_feature_rows.sql
```

## 各要素の役割

### `src/abuse_detection/`

scoring function、metrics、evaluation harness などの Python 実装を置きます。

### `fixtures/`

合成データを置きます。最初は Snowflake なしで評価を回せるようにします。

### `notebooks/`

評価ワークフローを手で回すための notebook を置きます。

notebook は、実験・観察・理解のための作業台です。scoring logic の本体や大量の特徴量生成SQLは置かない方針です。

### `dbt/`

将来的な特徴量生成SQLの置き場所です。

最初は実DBに接続せず、conceptual skeleton として使います。

### `AGENTS.md`

Codex などの coding agent 向けの作業指示書です。

細かい実装方針、テスト方針、禁止事項、責務分離のルールは `AGENTS.md` に寄せます。

## 最初のゴール

最初のゴールは、本番接続ではなく、ローカルでこの流れが動くことです。

```text
fixture CSV
  ↓
scoring_fn
  ↓
risk_score
  ↓
threshold sweep
  ↓
precision / recall
  ↓
false positive / false negative の確認
```

## 実行方法

依存関係をインストールします。

```bash
pip install -e ".[dev]"
```

テストを実行します。

```bash
pytest -q
```

notebook を使う場合:

```bash
jupyter notebook notebooks/01_evaluate_scoring.ipynb
```

または VS Code / Cursor / JupyterLab などで開いて実行します。

## このリポジトリに含めないもの

このリポジトリには、次のものを含めません。

* 実データ
* 顧客データ
* 社内データ
* 本番Snowflake接続情報
* API key
* credentials
* 実際の停止ルール
* 実際の検知閾値
* 実ユーザーを特定できる情報

public repo にできるよう、学習用の抽象化された toy project として扱います。

## Codex に依頼するとき

Codex に依頼するときは、まず `AGENTS.md` を読ませます。

例:

```text
AGENTS.md を読んで、この学習リポジトリの方針に従ってください。
まずはローカルで動く最小の evaluation harness を作ってください。
実データ・実DB接続・secret は使わないでください。
```

## 今後やりたいこと

* feature schema の明示
* scoring_fn のバージョン管理
* false positive / false negative の分析補助
* dbt skeleton の具体化
* Snowflake 接続の検討
* label_events_human の設計
* negative sampling の設計
* rolling window evaluation
* scoring_fn のMLモデル化
