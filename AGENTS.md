# AGENTS.md

## このリポジトリの位置づけ

このリポジトリは、SaaS におけるなりすまし・アカウント乗っ取り・スパム系アカウント検知のための、検知モデル育成パイプラインを学ぶための個人学習用プロジェクトです。

本番システムではありません。

このリポジトリでは、実データ・顧客データ・社内DB・本番Snowflake・秘密情報には接続しません。最初は合成データ、fixture CSV、toy example のみを使います。

## 学習目的

このプロジェクトの主目的は、次の流れを手を動かしながら理解することです。

```text
feature row -> scoring_fn -> risk_score -> threshold sweep -> precision/recall -> error analysis
```

特に、次の責務分離を理解することを重視します。

1. Feature generation

   * 特徴量行、つまり feature row を作る。
   * 実運用では Snowflake / SQL / dbt で作る想定。
   * この学習リポジトリでは、まず fixture CSV と dbt skeleton から始める。

2. Scoring function

   * `feature row -> risk_score` の純粋関数として扱う。
   * DBに接続しない。
   * ファイルを読まない。
   * ネットワークAPIを呼ばない。
   * ラベルを見ない。

3. Evaluation harness

   * ラベル付き feature row を読み込む。
   * `scoring_fn` を適用する。
   * threshold を動かす。
   * precision / recall / TP / FP / FN を計算する。
   * false positive と false negative を観察する。

4. Notebook

   * 評価ワークフローを手で回すための作業台。
   * 大量の特徴量生成SQLを置く場所ではない。
   * fixture CSV や準備済み feature row を読み、評価結果を表示する。

5. dbt

   * 特徴量生成SQLの置き場所を表す。
   * この学習リポジトリでは、最初は実DB接続なしの skeleton でよい。
   * label events、evaluation targets、point-in-time feature rows の考え方をSQLファイルで表現する。

## 基本方針

このプロジェクトでは、次の境界を守ります。

* `src/abuse_detection/scoring.py`

  * `scoring_fn(features) -> float` を定義する。
  * feature row から risk_score を返す。

* `src/abuse_detection/metrics.py`

  * precision / recall / TP / FP / FN の計算ロジックを定義する。

* `src/abuse_detection/evaluation.py`

  * feature rows に scoring_fn を適用し、評価結果を返す。

* `fixtures/`

  * 小さな合成データCSVのみを置く。
  * 実ユーザー情報は置かない。

* `notebooks/`

  * 評価ワークフローを実行する notebook を置く。
  * scoring logic の本体は置かない。

* `dbt/`

  * 特徴量生成SQLの概念的な skeleton を置く。
  * 将来 Snowflake に接続する場合の構造を表す。

## 作業の進め方

このリポジトリは学習用プロジェクトなので、coding agent は実装速度よりも、所有者が設計意図を理解できることを優先します。

作業では、次の順序を守ります。

1. 何を作るか説明する
2. なぜそれが必要か説明する
3. 小さく実装する
4. 実装したコードを一緒に読むための説明をする
5. テストで何を確認しているか説明する
6. `docs/progress/` に学びを残す
7. `docs/tasks.md` を更新する

詳細な進め方は `docs/agent_workflow.md` を参照します。

## セッション再開時の手順

ユーザーが「続きから始めよう」「前回の続き」などと言った場合は、まず現在地を復元します。

最低限、次を確認します。

1. `git status --short`
2. `docs/tasks.md`
3. `docs/progress/` の最新日付ファイル
4. 未コミット変更の内容

未コミット変更がある場合は、勝手に完成扱いせず、何が作成途中かを説明してから再開します。

## 推奨リポジトリ構成

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

## Python 実装方針

Python 3.11 以上を想定します。

優先すること:

* 小さな関数
* 型ヒント
* pandas ベースのシンプルな評価コード
* pytest によるテスト
* 明示的なカラム名
* 賢すぎる抽象化より読みやすさ

避けること:

* 早すぎるMLフレームワーク導入
* 実DB接続
* secret / credential の追加
* 本番システム前提の実装
* hidden global state
* 過度に汎用的な抽象化

## Fixture データ要件

`fixtures/feature_rows_sample.csv` には、合成データのみを入れます。

最低限、次のようなカラムを持たせます。

* `user_id`
* `as_of_time`
* `label_value`
* `account_age_minutes`
* `contacts_24h`
* `messages_1h`
* `profile_updates_24h`
* `plan`

fixture には、次のケースを含めます。

* 明らかな正例
* 明らかな負例
* false positive になりやすい例
* false negative になりやすい例

実ユーザー、実企業、実顧客の情報は入れません。

## scoring_fn の要件

最初はルールベースで実装します。

例:

* 登録直後ならリスク加点
* 直近24時間の contacts が多ければ加点
* 直近1時間の messages が多ければ加点
* profile updates が多ければ加点
* paid plan は少し減点してもよい

`risk_score` は 0 から 100 の範囲に clamp します。

`scoring_fn` はラベルを見てはいけません。

## metrics の要件

threshold sweep を実装します。

各 threshold について、次を計算します。

* `threshold`
* `precision`
* `recall`
* `tp`
* `fp`
* `fn`

ゼロ除算は安全に扱います。

## evaluation harness の要件

評価処理では、次の順序を明示します。

1. feature rows を読み込む
2. 必須カラムを検証する
3. 各行に `scoring_fn` を適用する
4. `risk_score` を付与する
5. threshold ごとに `predicted_abuse` を計算する
6. precision / recall / TP / FP / FN を計算する
7. false positives / false negatives を確認できるようにする

## notebook の要件

`notebooks/01_evaluate_scoring.ipynb` は、学習用 notebook として作ります。

notebook では以下を行います。

1. `fixtures/feature_rows_sample.csv` を読み込む
2. feature row の意味を説明する
3. `scoring_fn` を適用する
4. threshold を 0 から 100 まで 10 刻みで動かす
5. precision / recall を表で表示する
6. threshold=80 の false positives / false negatives を表示する
7. 次に改善すべき scoring_fn / feature の候補を考察する

notebook には、大量の特徴量生成SQLや scoring logic の本体を置かないこと。

## dbt skeleton の要件

`dbt/` は、将来の特徴量生成SQLの置き場所を表します。

最初は実DBに接続しなくてよいです。

SQLファイルでは、次の概念を表現します。

* オペレーター操作ログから label source を作る
* evaluation target を作る
* `user_id + as_of_time` の粒度で feature row を作る
* `event_time < as_of_time` により未来情報の混入を防ぐ
* 自動検知システムの停止結果を teacher label に混ぜない

## テスト要件

pytest を使います。

最低限、次をテストします。

* `scoring_fn` が 0 から 100 の範囲の数値を返す
* 明らかに怪しい row が、明らかに正常な row より高い score になる
* precision / recall 計算が既知の小さな例で正しい
* evaluation pipeline が `risk_score` と評価結果を返す
* 必須カラムが不足している場合に検知できる

作業完了前に、可能なら次を実行します。

```bash
pytest -q
```

テストが実行できない場合は、理由とエラー内容を明示します。

## README の方針

README は人間向けの入口として書きます。

README には次を含めます。

* このリポジトリが個人学習用であること
* 本番システムではないこと
* 実データを使わないこと
* feature row とは何か
* scoring_fn とは何か
* evaluation harness とは何か
* notebook の役割
* dbt の役割
* テストの実行方法
* 次に学ぶこと

## セキュリティとデータ取り扱い

* secrets を追加しない
* credentials を追加しない
* 実DBに接続しない
* 顧客データを追加しない
* 社内データを追加しない
* 実ユーザーを推測できる情報を追加しない

タスクが private data や credential を必要としそうな場合は、合成データで代替する方針を提案してください。

## Codex への期待

作業後の説明では、次を簡潔に報告してください。

* 何を作ったか
* なぜその構成にしたか
* どう実行するか
* どのファイルから読むべきか
* 次に何を試すと学びが深まるか

このリポジトリの所有者は、MLOps と不正検知評価設計を学習中です。
実装だけでなく、設計意図が理解できる説明を重視してください。
