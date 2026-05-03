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

- [x] 実装前に `docs/pre_implementation_checklist.md` に沿って説明する
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

- [x] 実装前に `docs/pre_implementation_checklist.md` に沿って説明する
- [x] `dbt/dbt_project.yml` を作る
- [x] staging model skeleton を作る
- [x] human label source skeleton を作る
- [x] evaluation target skeleton を作る
- [x] point-in-time feature row skeleton を作る
- [x] 自動検知システムの停止結果を teacher label に混ぜない方針を書く
- [x] `event_time < as_of_time` の未来情報防止を表現する
- [x] Phase 3 の学びを docs にまとめる

## Phase 3.5: Local SQLite Warehouse

- [x] 実装前に `docs/pre_implementation_checklist.md` に沿って説明する
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

- [x] 実装前に `docs/pre_implementation_checklist.md` に沿って説明する
- [x] false positives を取り出す helper を作る
- [x] false negatives を取り出す helper を作る
- [x] score bucket ごとの観察方法を考える
- [x] error analysis 用 notebook を作る
- [x] scoring_fn 改善メモを残す

## Phase 5: ML Baseline

- [x] 実装前に `docs/pre_implementation_checklist.md` に沿って説明する
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
- [ ] scoring_fn / model の versioning を考える
- [x] negative sampling を考える
- [x] stable negative candidate を選ぶ helper を作る
- [x] negative sampling の除外理由を観察する script を作る
- [x] rolling window evaluation を考える
- [x] `as_of_time` window ごとの metrics helper を作る
- [x] rolling window 評価 script を作る
- [x] score calibration を考える
- [x] score bucket ごとの observed positive rate を見る helper を作る
- [x] calibration と threshold sweep の違いを docs にまとめる
