# SaaS不正検知アーキテクチャ理解用リポジトリ

## このリポジトリについて

このリポジトリは本番システムではありません。

目的は、実データや本番環境を使わずに、`docs/design/` にある SaaS 不正検知の設計ドキュメントを手を動かしながら理解することです。

最初の学習対象は、評価基盤の基本構造でした。

```text
feature row -> scoring_fn -> risk_score -> threshold sweep -> precision/recall -> error analysis
```

今後の学習対象は、評価済み scorer を本番寄りの運用に接続する流れです。

```text
scored rows -> ScoreResult -> Decision Policy -> ActionCandidate -> Review Queue / Dry-run Worker -> ActionExecution
```

合成データと toy example だけを使い、実停止や外部 API 呼び出しは行いません。

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
* ScoreResult とは何か
* Decision Policy は scorer と何が違うのか
* ActionCandidate / ActionExecution をなぜ score と分けるのか
* Review Queue や dry-run worker はどの責務を持つのか
* 本番で生成された結果を、どう評価基盤へ戻すのか

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

評価基盤の次の段階では、さらに次を分けて考えます。

```text
ScoreResult
  scorer が出した時点ごとの score 履歴

Decision Policy
  score を review_required / auto_suspend_candidate / no_action へ変換するルール

ActionCandidate
  後続対応の候補になったという履歴

ActionExecution
  worker または operator が candidate に対して行った結果
```

最初から高度な機械学習モデルや本番アプリケーションを作るのではなく、まずは設計上の責務分離をローカルで小さく再現します。

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
    feature_rows_from_sqlite.csv

  tests/
    test_scoring.py
    test_metrics.py
    test_evaluation.py
    test_schema.py
    test_sqlite_warehouse.py

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

  scripts/
    build_sqlite_warehouse.py
    export_sqlite_feature_rows.py

  sql/
    sqlite/
      human_label_source.sql
      evaluation_targets.sql
      feature_rows.sql
      labeled_feature_rows.sql

  docs/
    design/
      evaluation_harness_architecture_mermaid_ja.md
      production_scoring_architecture_mermaid_ja.md
    planning/
      roadmap.md
      tasks.md
    process/
      agent_workflow.md
      pre_implementation_checklist.md
    learning/
      evaluation_flow.md
      learning_review.md
      production_gap_analysis.md
      phases/
    progress/
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

### `scripts/` と `sql/sqlite/`

ローカル SQLite を使い、合成 raw table から feature rows CSV を作るための教材です。

単一DBの中で `app_*`、`warehouse_*`、`eval_*` のテーブルを分けます。

`app_*` は MySQL のようなアプリDB由来のユーザー属性・プロフィール・状態snapshot、`warehouse_*` は Snowflake / TD のようなwarehouse由来の行動ログ、`eval_*` は feature rows / labels / evaluation targets の評価基盤側テーブルを表します。

`event_time < as_of_time` と `snapshot_time <= as_of_time` の条件により、評価時点より未来の行動ログやユーザー状態を特徴量に混ぜないことを確認できます。

`eval_feature_rows` には `label_value` を入れず、評価時に `eval_labels` と join して `fixtures/feature_rows_from_sqlite.csv` を書き出します。

### `AGENTS.md`

Codex などの coding agent 向けの作業指示書です。

細かい実装方針、テスト方針、禁止事項、責務分離のルールは `AGENTS.md` に寄せます。

## 最初のゴール

最初のゴールは完了済みで、本番接続ではなく、ローカルでこの流れが動くことでした。

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

次のゴールは、`docs/design/production_scoring_architecture_mermaid_ja.md` を理解するために、次の流れをローカルで再現することです。

```text
score_results
  ↓
decision_policy
  ↓
action_candidates
  ↓
review queue simulation
  ↓
dry-run action worker
  ↓
action_executions
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

SQLite warehouse から feature rows CSV を作る場合:

```bash
python3 scripts/build_sqlite_warehouse.py
python3 scripts/export_sqlite_feature_rows.py
```

SQLite内には `eval_feature_rows` と `eval_labels` が作られます。

生成される `fixtures/feature_rows_from_sqlite.csv` は、評価用に両者をjoinしたCSVで、既存の evaluation harness で評価できます。

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
docs/design を理解するために、まず Phase 8 の design map を作ってください。
実データ・実DB接続・secret は使わないでください。
```

## 今後やりたいこと

次は `docs/planning/roadmap.md` の Phase 8 以降に沿って進めます。

1. `docs/design` と既存実装の対応表を作る
2. ScoreResult / Decision Policy / ActionCandidate を最小実装する
3. ローカルの append-only log を作る
4. Review Queue simulation で候補を眺める
5. Dry-run Action Worker で安全弁を確認する
6. Human review 結果を評価基盤へ戻す流れを整理する
