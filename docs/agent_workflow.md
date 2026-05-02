# Agent Workflow

このリポジトリは学習用プロジェクトです。

coding agent は、実装速度よりも、所有者が設計意図を理解できることを優先します。

## 基本姿勢

作業者を置いていかない。

特に、評価基盤、不正検知、MLOps の概念が混ざりやすい箇所では、先に意図を説明してから実装します。

## 各ステップの進め方

1. 何を作るか説明する
2. なぜそれが必要か説明する
3. 小さく実装する
4. 実装したコードを一緒に読むための説明をする
5. テストで何を確認しているか説明する
6. `docs/progress/` に学びを残す
7. `docs/tasks.md` を更新する

## 説明の粒度

説明では、単に「何を変更したか」だけでなく、次を明確にします。

* そのファイルの責務
* 入力と出力
* なぜ別ファイルに分けるのか
* どの学習目的に対応しているのか
* 今はやらないこと

## Phase 1 で特に守ること

Phase 1 の目的は、最小 evaluation harness を理解することです。

実装を進めるときは、次の対応関係を説明します。

```text
fixtures/feature_rows_sample.csv
  -> 評価対象の合成 feature row

src/abuse_detection/schema.py
  -> feature row の必須カラム検証

src/abuse_detection/scoring.py
  -> feature row から risk_score を返す純粋関数

src/abuse_detection/metrics.py
  -> threshold ごとの precision / recall / TP / FP / FN 計算

src/abuse_detection/evaluation.py
  -> schema / scoring / metrics をつないだ評価 pipeline

tests/
  -> 期待する理解と挙動が壊れていないことの確認
```

## コードを書く前の確認

新しい概念やファイルを追加するときは、先に次を説明します。

* このステップで得られる学び
* 追加するファイル
* そのファイルを読む順番
* 完了後にどう動作確認するか

## セッション再開時の手順

ユーザーが「続きから始めよう」「前回の続き」などと言った場合は、すぐに実装へ進まず、現在地を復元します。

確認するもの:

1. `git status --short`
2. `docs/tasks.md`
3. `docs/progress/` の最新日付ファイル
4. 未コミット変更の内容

未コミット変更がある場合は、次を説明します。

* どのファイルが作成途中か
* その変更がどの Phase に対応しているか
* どの順番で一緒に確認するか
* すぐにコミットしてよい状態か、まだ説明や修正が必要な状態か

再開後は、`docs/tasks.md` の未完了タスクと `docs/progress/` の最新ログを見て、次の小さな単位から始めます。

Phase 1 の途中で未コミット実装がある場合は、まず次の順で確認します。

1. `fixtures/feature_rows_sample.csv`
2. `src/abuse_detection/schema.py`
3. `tests/test_schema.py`
4. `src/abuse_detection/scoring.py`
5. `tests/test_scoring.py`
6. `src/abuse_detection/metrics.py`
7. `tests/test_metrics.py`
8. `src/abuse_detection/evaluation.py`
9. `tests/test_evaluation.py`

## 進捗ログ

作業後は `docs/progress/YYYY-MM-DD.md` に、次を短く残します。

* やったこと
* 学んだこと
* 次にやること
* 疑問や保留

ログには、会社名、実案件、実データ、実運用上の検知条件、credential、secret を書きません。
