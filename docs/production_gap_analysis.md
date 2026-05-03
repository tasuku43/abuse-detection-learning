# Production Gap Analysis

この文書は、この学習リポジトリで作った toy evaluation harness と、実際の SaaS 不正検知システムを本番運用する場合に必要になる要素の差分を整理するものです。

このリポジトリは個人学習用です。実データ、顧客データ、社内データ、credential、本番 warehouse 接続情報、実際の停止ルール、検知閾値、運用上の機密情報は扱いません。ここでは public repo に置ける抽象化された内容だけを扱います。

## 1. この学習リポジトリで既にできていること

このリポジトリでは、本番システムを作る前に理解すべき評価パイプラインの骨格を、小さな合成データで再現しています。

中心の流れは次です。

```text
feature row
  -> scoring_fn
  -> risk_score
  -> threshold sweep
  -> precision / recall
  -> false positive / false negative analysis
```

既にできていることは、主に次です。

* **feature row の概念**
  * `user_id + as_of_time` の粒度で、評価時点の特徴量行を作る考え方を扱っています。
  * fixture CSV、dbt skeleton、SQLite warehouse の3段階で、feature row が raw data そのものではなく評価用に作る派生データであることを確認できます。

* **`scoring_fn`**
  * feature row を受け取り、0 から 100 の `risk_score` を返す関数として実装しています。
  * DB 接続、ファイル読み込み、ネットワーク API、`label_value` 参照を scoring logic から分離しています。

* **threshold sweep**
  * threshold を動かしながら、各 threshold での precision / recall / TP / FP / FN を計算できます。

* **precision / recall**
  * 不正検知で重要になる「検知したものの正しさ」と「本当の positive を拾えた割合」を、小さなデータで確認できます。

* **false positive / false negative analysis**
  * 誤検知と見逃しを取り出し、どの feature や score が判断に影響しているかを観察する helper と notebook があります。

* **score bucket analysis**
  * score の帯ごとに行数や positive rate を見て、score の分布と誤りを観察できます。

* **dbt skeleton**
  * staging、human label source、evaluation target、point-in-time feature row の概念を SQL ファイルで表現しています。
  * 自動検知システムの結果を teacher label に混ぜない方針も明示しています。

* **local SQLite warehouse**
  * 合成 raw table から、human labels、evaluation targets、point-in-time feature rows、labeled feature rows CSV を作る流れをローカルで再現しています。
  * `event_time < as_of_time` と `snapshot_time <= as_of_time` による未来情報混入の防止を小さく確認できます。

* **ML baseline**
  * logistic regression による最小 ML baseline を作り、rule-based scoring と同じ evaluation harness で比較できます。
  * 学習時は `label_value` を使い、scoring 時は feature row だけから `risk_score` を返す境界を確認できます。

* **model artifact metadata**
  * 学習済み model artifact と metadata を保存する形を用意しています。
  * `score_source` / `score_version` の考え方も導入しています。

* **negative sampling toy implementation**
  * 「停止されていない = 正常」ではないことを前提に、stable negative candidate を選ぶ toy helper があります。
  * 除外理由を観察する script により、negative sampling を見える化できます。

* **rolling window evaluation**
  * `as_of_time` の window ごとに metrics を出す helper と script があります。
  * 複数時点の synthetic fixture により、window ごとの precision drop を観察できます。

* **calibration toy analysis**
  * score bucket ごとの observed positive rate を見て、score が確率らしく読めるかを確認する toy analysis があります。

## 2. 本番化するときに追加で必要になるもの

### Data Sources

学習 repo では、fixture CSV と synthetic SQLite tables だけを使っています。

本番では、検知対象となる event source、user / account attributes、operator action logs、auto decision logs を安定して取得できる必要があります。

特に重要なのは、label source の信頼性です。human review や human suspend のログがあっても、それがどのポリシーに基づく判断なのか、誤停止や解除がどう記録されるのか、判断の粒度が user なのか account なのか workspace なのかを明確にする必要があります。

また、auto decision logs は evaluation や監査には重要ですが、そのまま teacher label に混ぜると既存検知システムの判断を再学習してしまう危険があります。

### Data Contracts

本番では、event schema と required columns を契約として管理する必要があります。

この repo では `schema.py` で必須カラムを検証していますが、本番ではさらに次を定義する必要があります。

* 各 event の必須フィールド
* timestamp の意味
* event が発生した時刻と記録された時刻の違い
* event-time snapshot の作り方
* late arriving events の扱い
* user、account、organization、device などの identity mapping

data contract が曖昧だと、同じ feature 名でも期間や source によって意味が変わり、評価結果を比較できなくなります。

### Point-in-Time Correctness

この repo では、SQLite SQL で `event_time < as_of_time` と `snapshot_time <= as_of_time` を表現しています。

本番では、これを全 feature に対して一貫して保証する必要があります。

必要になる観点は次です。

* `as_of_time` が何を意味するか
* 行動 event は `event_time < as_of_time` だけで集計すること
* user attribute は現在値ではなく履歴 snapshot から取得すること
* label や future action が feature に混ざらないこと
* offline training と online serving で使える feature がずれないこと

training-serving skew は、本番で特に問題になりやすいです。offline では見えていた feature が online scoring 時にはまだ届いていない、または online では別の定義で計算されている、という状態を避ける必要があります。

### Label Management

本番では、label は単なる `0` / `1` ではなく、運用判断の履歴として管理する必要があります。

必要になるものは次です。

* human labels の定義
* reversal handling
* auto decisions を teacher label に混ぜない方針
* label quality の確認
* label delay の扱い
* ambiguous cases の扱い

たとえば、ある user が一度停止された後に解除された場合、それを positive のまま扱うのか、誤停止として除外するのか、別 label として保持するのかを決める必要があります。

また、abuse と判断されるまでに時間がかかる場合、`as_of_time` 時点では label がまだ存在しないことがあります。label delay を無視すると、実際には後で positive になる user を negative として扱ってしまう可能性があります。

### Negative Sampling

この repo では、stable negative candidate を選ぶ toy implementation があります。

本番では、negative sampling policy をより慎重に設計する必要があります。

重要なのは、「停止されていない = 正常」ではないことです。停止されていない user には、未発見 abuse、レビューされていない suspicious cases、将来動き出す account、単に review queue に入らなかった cases が混ざります。

本番で考えるべきことは次です。

* stable negative candidates の定義
* sampling bias
* informative negatives
* review-skipped cases の扱い
* normal high-activity users をどう含めるか
* negative をきれいにしすぎて実 traffic とずれないか

negative sampling は、モデルの学習対象を決める作業です。単なるデータ量調整ではありません。

### Feature Generation

この repo では、dbt skeleton と SQLite SQL で feature row generation を学習しています。

本番では、warehouse 上の feature row table を安定して作る必要があります。

必要になるものは次です。

* dbt / SQL / warehouse 上の feature row model
* feature definitions
* feature versioning
* feature freshness
* feature quality tests
* backfill 方針
* 欠損や異常値の扱い

feature definition は、単に SQL として存在するだけでは不十分です。誰が読んでも同じ意味に解釈でき、過去の評価結果と比較できるように version を管理する必要があります。

### Scoring

この repo では、rule-based scoring と ML model scoring を同じ interface で扱っています。

本番では、score の生成と運用判断を分けて管理する必要があります。

必要になるものは次です。

* rule-based scoring の version 管理
* ML model scoring の version 管理
* `score_source` / `score_version`
* threshold management
* calibration の確認
* fallback behavior
* score 計算失敗時の扱い

threshold はコードに埋め込むより、変更履歴と承認フローを持つ設定として管理する方が安全です。

また、scoring が失敗したときに何をするかも重要です。たとえば、score 欠損を low risk と扱うのか、review に回すのか、retry するのかを決める必要があります。

### Evaluation

この repo では、CSV や DataFrame 上で evaluation を実行しています。

本番では、評価結果を保存し、後から再現できる形にする必要があります。

必要になるものは次です。

* evaluation window
* rolling window evaluation
* holdout / validation
* precision / recall
* FP / FN review
* `evaluation_results` table
* reproducibility
* evaluation run の metadata

評価は一度実行して終わりではありません。どの feature rows、どの labels、どの score version、どの threshold set で評価したかを保存し、後から比較できる必要があります。

### Operations

この repo では offline evaluation が中心です。

本番では、評価だけでなく運用に載せるための仕組みが必要です。

必要になるものは次です。

* batch scoring
* near-real-time scoring
* alerting
* monitoring
* rollback
* audit log
* human review workflow
* auto action safety guard

特に auto action は慎重に扱う必要があります。score が高いだけで自動停止するのではなく、対象範囲、上限、監査、rollback、manual review の導線を設計する必要があります。

### Governance / Security

この repo では、実データや secret を扱っていません。

本番では、データと意思決定の責任を管理する必要があります。

必要になるものは次です。

* access control
* PII handling
* secrets management
* public documentation と private documentation の分離
* explainability
* accountability
* auditability
* data retention policy

public repo に置けるのは抽象化された設計、toy data、toy logic までです。本番の接続情報、実 threshold、停止ロジック、個別事例、社内固有の運用手順は private に管理する必要があります。

## 3. 学習 repo と本番システムの違い

| 領域 | 学習repoでの状態 | 本番で必要なこと | まだ分からないこと / 次に調べること |
| --- | --- | --- | --- |
| Data sources | fixture CSV と synthetic SQLite tables | 本番 event source、user attributes、operator action logs、auto decision logs の安定取得 | どの source を正とするか、欠損時にどう扱うか |
| Label source | human label source の skeleton と synthetic labels | human labels の定義、reversal、label delay、ambiguous cases の管理 | 誤停止や解除を evaluation でどう扱うか |
| Data contracts | `schema.py` の required columns | event schema、timestamp semantics、identity mapping、late events の契約 | event time と ingestion time の差をどう監視するか |
| Point-in-time correctness | `event_time < as_of_time` と snapshot 条件を toy SQL で表現 | 全 feature で leakage prevention を保証 | offline と online の feature 定義をどう一致させるか |
| Feature generation | dbt skeleton と SQLite SQL | warehouse 上の feature table、feature versioning、freshness、quality tests | feature catalog をどの粒度で管理するか |
| Scoring | rule-based `scoring_fn` と logistic regression baseline | score_source / score_version、threshold management、fallback behavior | threshold の承認、変更、rollback をどう運用するか |
| Evaluation | DataFrame 上の threshold sweep と helper | evaluation_results table、run metadata、reproducibility | どの metrics を定常監視対象にするか |
| Error analysis | FP / FN helper と notebook | review workflow とつながる error analysis、segment 別評価 | FP / FN の原因分類をどう標準化するか |
| Negative sampling | stable negative toy helper | sampling policy、review-skipped cases、informative negatives | negative の代表性と安全性をどう検証するか |
| Rolling window | synthetic time series fixture で window metrics | 継続的な window evaluation と drift monitoring | どの window 幅が運用判断に適切か |
| Calibration | score bucket ごとの toy analysis | score を確率として使うか、ranking として使うかの設計 | calibration が必要な運用判断は何か |
| Model artifacts | local artifact と metadata | model registry、approval、rollback、lineage | metadata に最低限何を残すべきか |
| Operations | offline scripts | batch / near-real-time scoring、alerting、monitoring、audit log | 最初の運用形態を batch にするか near-real-time にするか |
| Human review | notebook 上の観察 | queue、優先順位、review outcome feedback loop | review capacity を threshold とどう結びつけるか |
| Auto action | 実装しない | safety guard、rate limit、manual override、rollback | どの条件なら自動化してよいか |
| Governance / security | 実データと secret を置かない | access control、PII、secrets、private docs、accountability | public / private docs の境界をどう定義するか |

## 4. MVP として最初に本番寄りへ進めるなら何を優先するか

本番寄りに進める場合でも、いきなり自動判定や複雑な ML には進まない方がよいです。まずは、評価を再現できる土台を作ります。

### Priority 1: 評価データの土台

最初に優先するのは、label と feature row と evaluation result の最小契約です。

* label source の定義
* `label_events_human` schema の設計
* feature row schema の設計
* `as_of_time` の意味の明確化
* point-in-time correctness の確認
* `evaluation_results` の保存
* evaluation run metadata の保存

この段階の目的は、「どのデータで、どの version を、いつ評価したか」を後から説明できるようにすることです。

### Priority 2: 評価の読み方を運用に近づける

次に、評価結果を実務判断に近づけます。

* negative sampling policy
* rolling window evaluation
* score versioning
* segment 別 metrics
* FP / FN review workflow
* score bucket analysis
* label delay の扱い

この段階では、model の複雑さよりも、評価結果をどう解釈し、どの改善につなげるかを重視します。

### Priority 3: Scoring を本番運用に近づける

最後に、scoring と運用連携を広げます。

* ML model registry
* calibration
* online scoring / near-real-time scoring
* threshold management
* monitoring
* rollback
* auto action integration

auto action integration は最後に扱うべきです。十分な offline evaluation、shadow evaluation、human review を経てから、安全 guard 付きで検討します。

## 5. この段階でまだやらない方がよいこと

この学習段階では、次のことは避けた方がよいです。

* いきなり自動停止する
* いきなり複雑な ML model にする
* 実データを public repo に持ち込む
* credential や本番接続情報を追加する
* notebook に本番ロジックを閉じ込める
* auto decision を teacher label に混ぜる
* threshold を根拠なく固定して成功扱いする
* false positive / false negative を見ずに metrics だけで判断する
* feature definition を version 管理しないまま比較する
* 本番運用の監査や rollback を後回しにして自動 action を作る

今の段階で大事なのは、モデルを強くすることより、評価の前提を崩さないことです。

## 6. 次の学習タスク案

次に進むなら、次の3つが学習効果の高いタスクです。

1. **本番 MVP 用の `label_events_human` schema を設計する**
   * human label の発生時刻、対象 ID、判断種別、reversal、label quality、label delay を public repo に置ける抽象 schema として整理します。
   * 目的は、teacher label の定義を曖昧にしないことです。

2. **`evaluation_results` table の最小 schema を設計する**
   * `run_id`、評価期間、score_source、score_version、threshold、precision、recall、TP / FP / FN、入力 dataset の参照を保存する形を考えます。
   * 目的は、評価結果を notebook の表示で終わらせず、後から比較できるようにすることです。

3. **production-grade feature row contract を設計する**
   * required columns、timestamp semantics、feature definitions、nullable policy、version、freshness requirement をまとめます。
   * 目的は、feature row を「CSV の列」ではなく、scoring と evaluation の共通契約として扱えるようにすることです。

