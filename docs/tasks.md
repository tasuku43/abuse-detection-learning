# Tasks

このファイルは、学習プロジェクトの作業チェックリストです。

## Phase 0: Project Setup

- [x] README を作る
- [x] AGENTS.md を作る
- [x] roadmap を作る
- [x] progress log を作る
- [x] task list を作る

## Phase 1: Minimal Evaluation Harness

- [ ] `pyproject.toml` を作る
- [ ] `src/abuse_detection/__init__.py` を作る
- [ ] `src/abuse_detection/schema.py` で必須カラムを定義する
- [ ] `src/abuse_detection/scoring.py` で `scoring_fn` を作る
- [ ] `src/abuse_detection/metrics.py` で precision / recall を計算する
- [ ] `src/abuse_detection/evaluation.py` で評価 pipeline を作る
- [ ] `fixtures/feature_rows_sample.csv` を作る
- [ ] `tests/test_schema.py` を作る
- [ ] `tests/test_scoring.py` を作る
- [ ] `tests/test_metrics.py` を作る
- [ ] `tests/test_evaluation.py` を作る
- [ ] `pytest -q` を通す

## Phase 2: Notebook Workflow

- [ ] `notebooks/01_evaluate_scoring.ipynb` を作る
- [ ] fixture CSV を読み込む
- [ ] `scoring_fn` を適用する
- [ ] threshold 0 から 100 まで 10 刻みで sweep する
- [ ] precision / recall を表で表示する
- [ ] threshold 80 の false positives / false negatives を表示する
- [ ] scoring_fn / feature 改善候補を考察する

## Phase 3: dbt Skeleton

- [ ] `dbt/dbt_project.yml` を作る
- [ ] staging model skeleton を作る
- [ ] human label source skeleton を作る
- [ ] evaluation target skeleton を作る
- [ ] point-in-time feature row skeleton を作る
- [ ] auto actor の停止結果を teacher label に混ぜない方針を書く
- [ ] `event_time < as_of_time` の未来情報防止を表現する

## Phase 4: Error Analysis

- [ ] false positives を取り出す helper を作る
- [ ] false negatives を取り出す helper を作る
- [ ] score bucket ごとの観察方法を考える
- [ ] scoring_fn 改善メモを残す

## Phase 5: Iteration Ideas

- [ ] scoring_fn の versioning を考える
- [ ] negative sampling を考える
- [ ] rolling window evaluation を考える
- [ ] simple ML model との比較を考える
