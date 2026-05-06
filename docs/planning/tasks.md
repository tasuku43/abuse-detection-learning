# Tasks

このファイルは、学習プロジェクトの作業チェックリストです。

## Phase 0: Project Setup

- [x] README を作る
- [x] AGENTS.md を作る
- [x] roadmap を作る
- [x] progress log を作る
- [x] task list を作る
- [x] 実装前説明を省略しないための pre-implementation checklist を作る

## Phase 1: Minimal Evaluation Harness

- [x] `pyproject.toml` を作る
- [x] `src/abuse_detection/__init__.py` を作る
- [x] `src/abuse_detection/schema.py` で必須カラムを定義する
- [x] `src/abuse_detection/scoring.py` で `scoring_fn` を作る
- [x] `src/abuse_detection/metrics.py` で precision / recall を計算する
- [x] `src/abuse_detection/evaluation.py` で評価 pipeline を作る
- [x] `fixtures/feature_rows_sample.csv` を作る
- [x] `tests/test_schema.py` を作る
- [x] `tests/test_scoring.py` を作る
- [x] `tests/test_metrics.py` を作る
- [x] `tests/test_evaluation.py` を作る
- [x] `pytest -q` を通す
- [x] Mermaid 図で evaluation flow を説明する doc を作る

## Phase 2: Notebook Workflow

- [x] 実装前に `docs/process/pre_implementation_checklist.md` に沿って説明する
- [x] `notebooks/01_evaluate_scoring.ipynb` を作る
- [x] fixture CSV を読み込む
- [x] `scoring_fn` を適用する
- [x] threshold 0 から 100 まで 10 刻みで sweep する
- [x] precision / recall を表で表示する
- [x] threshold 80 の false positives / false negatives を表示する
- [x] scoring_fn / feature 改善候補を考察する
- [x] fixture CSV の合成データを増やす
- [x] fixture CSV を100件の合成ユーザーに増やす
- [x] account takeover / spam 観察用の特徴量を追加する
- [x] 複数の scoring_fn 候補を作る
- [x] 単一 notebook で scoring_fn 候補を比較する
- [x] Phase 2 の学びを docs にまとめる

## Phase 3: dbt Skeleton

- [x] 実装前に `docs/process/pre_implementation_checklist.md` に沿って説明する
- [x] `dbt/dbt_project.yml` を作る
- [x] staging model skeleton を作る
- [x] human label source skeleton を作る
- [x] evaluation target skeleton を作る
- [x] point-in-time feature row skeleton を作る
- [x] 自動検知システムの停止結果を teacher label に混ぜない方針を書く
- [x] `event_time < as_of_time` の未来情報防止を表現する
- [x] Phase 3 の学びを docs にまとめる

## Phase 3.5: Local SQLite Warehouse

- [x] 実装前に `docs/process/pre_implementation_checklist.md` に沿って説明する
- [x] SQLite raw table schema を作る
- [x] synthetic account attributes を seed する
- [x] synthetic user behavior logs を seed する
- [x] synthetic operator action logs を seed する
- [x] human label source 相当の SQL を作る
- [x] evaluation target 相当の SQL を作る
- [x] point-in-time feature row SQL を作る
- [x] SQLite から feature rows CSV を書き出す script を作る
- [x] 生成した feature rows を既存 evaluation harness で評価する
- [x] SQLite warehouse の学びを docs にまとめる

## Phase 4: Error Analysis

- [x] 実装前に `docs/process/pre_implementation_checklist.md` に沿って説明する
- [x] false positives を取り出す helper を作る
- [x] false negatives を取り出す helper を作る
- [x] score bucket ごとの観察方法を考える
- [x] error analysis 用 notebook を作る
- [x] scoring_fn 改善メモを残す

## Phase 5: ML Baseline

- [x] 実装前に `docs/process/pre_implementation_checklist.md` に沿って説明する
- [x] `src/abuse_detection/ml_baseline.py` を作る
- [x] logistic regression で fixture feature rows を学習する
- [x] ML model の出力を 0 から 100 の `risk_score` に変換する
- [x] `tests/test_ml_baseline.py` を作る
- [x] rule-based scoring_fn と ML-based scoring_fn を同じ evaluation harness で比較する
- [x] `notebooks/02_compare_rule_vs_ml.ipynb` を作る
- [x] false positives / false negatives を rule-based と ML-based で比較する
- [x] ML baseline の学びを docs にまとめる

## Phase 6: Iteration Ideas

- [x] ML baseline をファイルベースで保存する
- [x] 保存済み ML baseline を読み込んで評価する
- [x] model artifact の metadata を保存する
- [x] ML baseline に train / validation split を追加する
- [x] validation rows で saved model を評価できるようにする
- [x] scoring_fn / model の versioning を考える
- [x] 評価結果に `score_source` / `score_version` を付けられるようにする
- [x] negative sampling を考える
- [x] stable negative candidate を選ぶ helper を作る
- [x] negative sampling の除外理由を観察する script を作る
- [x] rolling window evaluation を考える
- [x] `as_of_time` window ごとの metrics helper を作る
- [x] rolling window 評価 script を作る
- [x] score calibration を考える
- [x] score bucket ごとの observed positive rate を見る helper を作る
- [x] calibration と threshold sweep の違いを docs にまとめる

## Phase 7: Practical Evaluation Improvements

- [x] 複数時点の synthetic feature rows fixture を作る
- [x] rolling window evaluation を複数 window で確認できるようにする
- [x] ML baseline に time-based train / validation split を追加する
- [x] Phase 7 の学びを docs にまとめる

## Learning Review

- [x] Phase 0〜7 の学びを `docs/learning/learning_review.md` にまとめる

## Production Gap Analysis

- [x] 学習 repo と本番システムの差分を `docs/learning/production_gap_analysis.md` にまとめる

## Roadmap Repositioning

- [x] `docs/design/` の2本を読み、評価基盤設計と本番スコアリング運用設計の関係を整理する
- [x] `docs/design/` を public repo 前提の架空設計として、具体的な業務名詞を抽象表現へ寄せる
- [x] `docs/design/` の Mermaid 図にデータストア形状、判断ノード、処理ノード、色分けを追加する
- [x] `docs/design/` から学習プロセスや推奨実装タスクの節を外し、純粋な設計書として整理する
- [x] `docs/planning/roadmap.md` を `docs/design` 理解用のロードマップとして組み直す
- [x] `README.md` の位置づけを、評価基盤単体から設計理解用プロジェクトへ更新する
- [x] `AGENTS.md` の冒頭を Phase 8 以降の方針に合わせて更新する
- [x] `docs/` を `design/`、`planning/`、`process/`、`learning/`、`progress/` に整理する

## Phase 8: Design Map and Concept Alignment

- [x] `docs/learning/design_map.md` を作る
- [x] `docs/design/evaluation_harness_architecture_mermaid_ja.md` と既存実装の対応を表にする
- [x] `docs/design/production_scoring_architecture_mermaid_ja.md` と次に作る概念の対応を表にする
- [x] 評価基盤から本番スコアリング運用へ進む Mermaid 図を作る
- [x] `score_results` / `action_candidates` / `action_executions` を分ける理由を説明する

## Phase 9: ScoreResult and Decision Policy Simulation

- [ ] 実装前に `docs/process/pre_implementation_checklist.md` に沿って説明する
- [ ] `src/abuse_detection/production_schema.py` を作る
- [ ] `ScoreResult` / `DecisionResult` / `ActionCandidate` を定義する
- [ ] `src/abuse_detection/decision_policy.py` を作る
- [ ] ScoreResult から ActionCandidate を作れるようにする
- [ ] high score / low score / dry-run の decision policy をテストする
- [ ] `tests/test_production_schema.py` を作る
- [ ] `tests/test_decision_policy.py` を作る

## Phase 10: Local Append-only Log Simulation

- [ ] 実装前に `docs/process/pre_implementation_checklist.md` に沿って説明する
- [ ] `src/abuse_detection/local_log_store.py` を作る
- [ ] `scripts/build_action_candidates.py` を作る
- [ ] `score_results` JSONL を `data_lake/` 配下に出力する
- [ ] `action_candidates` JSONL を `data_lake/` 配下に出力する
- [ ] `_SUCCESS` または `manifest.json` 相当の完了 marker を作る
- [ ] local append-only log のテストを作る

## Phase 11: Review Queue Simulation

- [ ] 実装前に `docs/process/pre_implementation_checklist.md` に沿って説明する
- [ ] `scripts/review_queue_summary.py` を作る
- [ ] open な action candidates を一覧できるようにする
- [ ] risk_score 降順で並べられるようにする
- [ ] `decision` / `candidate_status` で filter できるようにする
- [ ] 外部管理画面 link を placeholder として表現する

## Phase 12: Dry-run Action Worker Simulation

- [ ] 実装前に `docs/process/pre_implementation_checklist.md` に沿って説明する
- [ ] `src/abuse_detection/action_worker.py` を作る
- [ ] `scripts/run_dry_run_worker.py` を作る
- [ ] action_candidates を読み込めるようにする
- [ ] `dry_run = true` の場合は execution log だけを出す
- [ ] 既に処理済みの candidate を skip する
- [ ] current status が open でない candidate を skip する
- [ ] skip reason を `action_executions` に残す
- [ ] dry-run worker のテストを作る

## Phase 13: Feedback Loop Back to Evaluation

- [ ] `docs/learning/production_to_evaluation_feedback.md` を作る
- [ ] synthetic review result fixture を作る
- [ ] human review result から `label_events_human` 相当を作る toy flow を整理する
- [ ] auto decision を teacher label に混ぜない流れを図解する
