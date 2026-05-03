# Roadmap

このロードマップは、SaaS 不正検知の評価パイプラインを段階的に学ぶための作業順序を表します。

このリポジトリは本番システムではありません。実データ、顧客データ、社内データ、credential、本番検知ロジックは使わず、合成データと toy example だけで進めます。

中心となる学習対象は次の流れです。

```text
feature row -> scoring_fn -> risk_score -> threshold sweep -> precision/recall -> error analysis
```

## Phase 0: Project Setup

目的: リポジトリの意図、作業方針、進捗管理の置き場所を明確にする。

このフェーズでは、実装そのものよりも、学習プロジェクトとして迷子にならないための土台を作る。

### 作るもの

* `README.md`
* `AGENTS.md`
* `docs/roadmap.md`
* `docs/tasks.md`
* `docs/progress/`
* `.gitignore`

### 完了条件

* `README.md` が人間向けの入口になっている
* `AGENTS.md` に coding agent 向けの方針がある
* `docs/roadmap.md` に学習フェーズが整理されている
* `docs/tasks.md` で次の作業を追える
* `docs/progress/` に日別の学習ログを残せる
* public repo にしても問題ないよう、実データや機密情報を含めない方針が明記されている

### 補足

`README.md` はシンプルに保つ。

細かい実装方針、テスト方針、責務分離、禁止事項は `AGENTS.md` に寄せる。

`docs/progress/` には、学習ログだけを残す。会社名、実案件、実データ、実運用上の検知条件などは書かない。

---

## Phase 1: Minimal Evaluation Harness

目的: 合成 feature rows から risk_score を出し、threshold sweep で precision / recall を確認できる最小構成を作る。

このフェーズでは、Snowflake、dbt、notebook には深入りしない。

まずはローカルの fixture CSV だけで、次の流れを動かす。

```text
fixture CSV
  ↓
feature schema validation
  ↓
scoring_fn
  ↓
risk_score
  ↓
threshold sweep
  ↓
precision / recall / TP / FP / FN
```

### 作るもの

* `pyproject.toml`
* `src/abuse_detection/__init__.py`
* `src/abuse_detection/schema.py`
* `src/abuse_detection/scoring.py`
* `src/abuse_detection/metrics.py`
* `src/abuse_detection/evaluation.py`
* `fixtures/feature_rows_sample.csv`
* `tests/test_schema.py`
* `tests/test_scoring.py`
* `tests/test_metrics.py`
* `tests/test_evaluation.py`

### 完了条件

* `pytest -q` が通る
* `feature row` の必須カラムを検証できる
* 必須 feature column が欠けている場合にエラーにできる
* `scoring_fn` が 0 から 100 の `risk_score` を返す
* 明らかに怪しい row が、明らかに正常な row より高い score になる
* threshold ごとの precision / recall / TP / FP / FN が計算できる
* false positive / false negative を取り出せる
* scoring_fn が DB、ファイル、ネットワーク、label に依存していない

### このフェーズでやらないこと

* Snowflake 接続
* dbt 実行
* 実データ利用
* notebook での本格分析
* MLモデル学習

---

## Phase 2: Notebook Workflow

目的: 評価の流れを notebook 上で手で回し、結果を観察できるようにする。

このフェーズでは、notebook を「評価ワークフローを手で回す作業台」として使う。

notebook は scoring logic の本体や、大量の特徴量生成SQLの置き場にしない。

### 作るもの

* `notebooks/01_evaluate_scoring.ipynb`

### notebook で行うこと

1. `fixtures/feature_rows_sample.csv` を読み込む
2. feature row の中身を確認する
3. `scoring_fn` を適用する
4. `risk_score` 付き feature rows を表示する
5. threshold を 0 から 100 まで 10 刻みで sweep する
6. precision / recall / TP / FP / FN を表示する
7. threshold 80 の false positives / false negatives を最低限確認する
8. scoring_fn や feature 改善の候補をメモする

### 完了条件

* fixture CSV を読み込める
* score 付き feature rows を表示できる
* threshold 0 から 100 まで 10 刻みで sweep できる
* precision / recall / TP / FP / FN を表で確認できる
* threshold 80 の false positives / false negatives を表示できる
* notebook の markdown cell に、各ステップの意味が簡潔に説明されている
* notebook に scoring logic の本体を持たせていない

### 補足

Phase 2 では、false positives / false negatives は「見える」状態でよい。

本格的な error analysis は Phase 4 で行う。

---

## Phase 3: dbt Skeleton

目的: 将来の特徴量生成SQLの置き場所と、point-in-time feature row の考え方を表現する。

このフェーズでは、dbt を実DBに接続しなくてよい。

目的は、dbt を「特徴量生成SQLを管理する場所」として理解すること。

### 作るもの

* `dbt/dbt_project.yml`
* `dbt/models/staging/stg_business_events.sql`
* `dbt/models/staging/stg_td_events.sql`
* `dbt/models/staging/stg_users.sql`
* `dbt/models/labels/label_events_human.sql`
* `dbt/models/features/evaluation_targets.sql`
* `dbt/models/features/fct_abuse_feature_rows.sql`

### 表現したい考え方

* human operator の停止イベントだけを teacher label として扱う
* auto actor の停止結果を teacher label に混ぜない
* 停止解除などの reversal を考慮できる余地を残す
* `user_id + as_of_time` 粒度で evaluation target を作る
* feature row は `as_of_time` 時点で見えていた情報だけから作る
* `event_time < as_of_time` により未来情報の混入を防ぐ
* event payload に含まれる属性 snapshot と、行動集計値を区別する

### 完了条件

* human operator の停止イベントだけを teacher label として扱う意図が SQL に表れている
* `user_id + as_of_time` 粒度の evaluation target が表現されている
* `event_time < as_of_time` により未来情報を混ぜない方針が表現されている
* feature row を作る SQL skeleton がある
* 実DB接続や credential を必要としない
* dbt run の成功を完了条件にしていない

### このフェーズでやらないこと

* Snowflake 接続
* 実テーブル名への接続
* credential 管理
* dbt Cloud / job 設定
* 本番 feature table の作成

---

## Phase 4: Error Analysis

目的: score の良し悪しを precision / recall だけでなく、誤検知例から観察する。

このフェーズでは、単に metrics を見るだけでなく、どのような行が false positive / false negative になっているかを確認する。

Phase 2 では FP/FN を最低限表示できればよかった。

Phase 4 では、FP/FN を分析しやすくする。

### 作るもの

* false positive / false negative の表示補助
* score bucket ごとの集計
* feature 値を並べた比較表
* 改善候補メモ欄
* notebook 上の error analysis section

### 観察したいこと

* 高スコアなのに負例だった行は何か
* 低スコアなのに正例だった行は何か
* 特定の feature が誤検知に寄与していないか
* paid plan や account age などで誤検知が偏っていないか
* threshold を上げ下げしたときに、どの行が判定境界をまたぐか

### 完了条件

* false positive 行を feature と一緒に確認できる
* false negative 行を feature と一緒に確認できる
* score bucket ごとに label 分布を確認できる
* scoring_fn の改善候補を具体的に書ける
* 次に追加すべき feature の仮説を立てられる

### このフェーズでやらないこと

* 本番適用判断
* 実ユーザー調査
* 実データに基づく運用判断
* 高度な可視化基盤構築

---

## Phase 5: ML Baseline

目的: rule-based scoring_fn と、最小の ML-based scoring_fn を同じ evaluation harness で比較する。

このフェーズでは、高度な ML モデルには進まない。

まず logistic regression だけを使い、ML も次の同じ流れに乗ることを確認する。

```text
feature row -> scoring_fn -> risk_score -> threshold sweep -> precision/recall -> error analysis
```

rule-based scoring_fn では、人間が条件と重みを書く。

ML-based scoring_fn では、学習済みモデルが feature row から `risk_score` を返す。

ただし、feature row の作り方、label leakage の防止、negative sample の設計、評価方法は人間が確認する。

### 作るもの

* `src/abuse_detection/ml_baseline.py`
* `tests/test_ml_baseline.py`
* `notebooks/02_compare_rule_vs_ml.ipynb`

### 学ぶこと

* ML model も `feature row -> risk_score` の関数として扱えること
* 同じ feature row を使って rule-based scoring_fn と logistic regression を比較できること
* ML に進んでも threshold sweep と error analysis が必要なこと
* train / validation を分けずに評価すると、性能を楽観的に見やすいこと
* small fixture では model の性能そのものより、評価の形を学ぶことが重要なこと

### 最初に使うモデル

logistic regression に絞る。

理由:

* feature と score の関係を説明しやすい
* 小さな合成データでも動かしやすい
* rule-based scoring_fn との違いを観察しやすい
* decision tree や random forest より、最初の比較対象として単純

### 完了条件

* logistic regression を fixture feature rows から学習できる
* ML model の出力を 0 から 100 の `risk_score` に変換できる
* rule-based scoring_fn と ML-based scoring_fn を同じ threshold sweep で比較できる
* false positives / false negatives を両方の scoring_fn で比較できる
* ML を使っても evaluation harness を再利用できることを説明できる

### このフェーズでやらないこと

* advanced ML model の導入
* hyperparameter tuning
* production model registry
* online inference
* 実データでの学習
* 本番適用判断

---

## Phase 6: Iteration

目的: scoring_fn、feature、評価方法を小さく改善しながら、検知モデル育成パイプラインの理解を深める。

このフェーズでは、rule-based scoring_fn と ML-based scoring_fn の両方を比較対象にしながら、小さな改善を繰り返す。

重要なのは、大きなMLモデルをいきなり導入することではなく、次のループを回すこと。

```text
評価する
  ↓
誤検知を見る
  ↓
仮説を立てる
  ↓
feature / scoring_fn を少し変える
  ↓
再評価する
```

### 優先順つき候補

1. scoring_fn の versioning
2. negative sampling の設計
3. rolling window evaluation
4. score calibration

### 6.1 scoring_fn の versioning

目的: どの scoring_fn で評価した結果なのかを追えるようにする。

候補:

* `SCORING_VERSION` を定義する
* evaluation result に scoring version を含める
* notebook に使用した scoring version を表示する

完了条件:

* 評価結果が、どの scoring_fn から出たものか分かる

### 6.2 negative sampling の設計

目的: 負例をどう作るかを理解する。

学ぶこと:

* 「停止されていない = 正常」とは単純に言えない理由
* 登録から一定日数経過したユーザーを負例候補にする理由
* 停止履歴やレビュー履歴をどう扱うか
* negative sample の偏り

完了条件:

* simple negative sampling の方針を説明できる
* negative sample の限界を説明できる

### 6.3 rolling window evaluation

目的: 時間による攻撃パターンの変化を評価に取り入れる。

学ぶこと:

* 評価期間を固定しすぎると見えない問題
* 攻撃者ドリフト
* 週次 / 月次で performance を比較する意味

完了条件:

* 複数 window で precision / recall を比較できる
* window によって性能が変わる可能性を説明できる

### 6.4 score calibration

目的: score を単なる順位付けではなく、確率らしい値として扱う場合の考え方を学ぶ。

このテーマは少し後回しでよい。

完了条件:

* score calibration が何を解決する話かを説明できる
* threshold sweep との違いを説明できる

---

## Optional Phase: CLI Runner

目的: notebook なしでも、ローカルで評価を実行できるようにする。

このフェーズは必須ではない。

Phase 1 または Phase 2 の後に追加してもよい。

### 作るもの

* `scripts/run_eval.py`

または

* `python -m abuse_detection.evaluation`

### 完了条件

* fixture CSV を読み込んで評価結果を標準出力できる
* threshold sweep の結果を terminal で確認できる
* notebook なしでも最小評価が動く

---

## 進め方の原則

### 1. 小さく動くものを優先する

最初から Snowflake、dbt、notebook、ML model を全部つなげない。

まずは fixture CSV で評価基盤の芯を動かす。

### 2. 実データを使わない

このリポジトリでは、学習用の合成データのみを使う。

実データ、社内データ、顧客データ、credential は入れない。

### 3. 責務を混ぜない

* feature generation は feature row を作る
* scoring_fn は feature row から risk_score を返す
* evaluation harness は score と label を比較する
* notebook は評価ワークフローを手で回す
* dbt は特徴量生成SQLの置き場所を表す

### 4. notebook を肥大化させない

notebook は実験と観察の場所。

scoring logic の本体や、大量の特徴量生成SQLは置かない。

### 5. public repo 前提で安全にする

public repo にできるよう、実運用上の検知ルールや閾値、社内固有の情報は入れない。

---

## 現時点の優先順位

まずは次の順番で進める。

1. Phase 0 を完了する
2. Phase 1 の最小 evaluation harness を作る
3. pytest を通す
4. Phase 2 の notebook で評価を眺める
5. Phase 3 の dbt skeleton で feature generation の置き場所を理解する
6. Phase 4 で error analysis を深める
7. Phase 5 で logistic regression の ML baseline と比較する
8. Phase 6 で小さく改善を繰り返す
