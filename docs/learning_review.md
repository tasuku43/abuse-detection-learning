# Learning Review

この文書は、Phase 0 から Phase 7 までで学んだことを後から読み返すための総まとめです。

このリポジトリは個人学習用であり、本番システムではありません。実データ、社内データ、credential、本番検知ロジックは扱いません。

## 1. Feature Row の役割

feature row は、あるユーザーをある時点で評価するための入力行です。

重要なのは、feature row が raw data そのものではないことです。アカウント属性、行動ログ、プロフィール更新、ログイン失敗、ブロック率などを、`user_id + as_of_time` の粒度に集約して作ります。

feature row の中心は `as_of_time` です。評価時点より未来の行動を特徴量に混ぜると、offline evaluation が実力以上によく見えてしまいます。そのため、行動ログでは `event_time < as_of_time`、状態 snapshot では `snapshot_time <= as_of_time` のような point-in-time correctness が必要です。

feature row は scoring input なので、本来は `label_value` を持たない方が責務として自然です。評価時には、feature row と label を join した labeled feature rows を使います。

## 2. `scoring_fn` の役割

`scoring_fn` は、feature row を受け取り、`risk_score` を返す関数です。

このプロジェクトでは、`feature row -> risk_score` を純粋な変換として扱いました。`scoring_fn` は DB に接続せず、ファイルを読まず、ネットワーク API を呼ばず、`label_value` を見ません。

この境界を守ると、rule-based scoring でも ML-based scoring でも、同じ evaluation harness に渡せます。つまり、評価基盤側から見ると、スコアの作り方がルールかモデルかは差し替え可能な実装詳細になります。

## 3. Evaluation Harness の役割

evaluation harness は、score を作る関数の良し悪しを観察するための器です。

このプロジェクトでは、次の流れを明示しました。

```text
labeled feature rows
  -> required columns validation
  -> scoring_fn
  -> risk_score
  -> threshold sweep
  -> precision / recall / TP / FP / FN
  -> false positive / false negative analysis
```

評価の主役は単一の accuracy ではありません。不正検知では、どの threshold でどれだけ検知でき、どれだけ正常ユーザーを巻き込むかを見る必要があります。

evaluation harness を scoring logic から分離したことで、rule-based scoring、ML baseline、保存済み model、rolling window evaluation を同じ考え方で比較できました。

## 4. Notebook の役割

notebook は、評価ワークフローを手で回して観察するための作業台です。

notebook には、scoring logic の本体や大量の特徴量生成 SQL を置かない方針にしました。理由は、notebook が実験と観察の場であり、再利用される処理本体は `src/` や `scripts/` に置いた方が読みやすく、テストしやすいからです。

notebook では、feature rows を読み込み、score を付け、threshold sweep の結果を表で見て、false positive / false negative を観察しました。これは「モデルを作る」より前に、「評価結果をどう読むか」を学ぶために重要でした。

## 5. dbt Skeleton の役割

dbt skeleton は、将来の特徴量生成 SQL の置き場所と責務を表すための構造です。

このプロジェクトでは実 DB には接続せず、概念を SQL ファイルで表現しました。特に重要だったのは、次の分離です。

* staging model は raw data を読みやすい形に整える
* label source は human action から teacher label を作る
* evaluation target は評価したい `user_id + as_of_time` を定義する
* feature row model は point-in-time に特徴量を作る

また、自動検知システムによる停止結果を teacher label に混ぜない方針も明示しました。自動検知結果を label に混ぜると、既存システムの判断を新しいモデルがそのまま学習してしまう危険があるためです。

## 6. SQLite Warehouse で学んだこと

SQLite warehouse では、dbt skeleton の考え方をローカルで実行できる形にしました。

1つの SQLite ファイルの中で、`app_*`、`warehouse_*`、`eval_*` という table prefix を使い、データの性質を分けました。

```text
app_*       -> アプリ DB 由来のユーザー状態
warehouse_* -> 行動ログやオペレーター操作ログ
eval_*      -> 評価用 target / label / feature rows
```

ここで学んだ中心は、feature row は raw table から自然に出てくるものではなく、評価時点を決めて作る派生テーブルだという点です。

SQLite によって、次の流れを小さく体験できました。

```text
synthetic raw tables
  -> human labels
  -> evaluation targets
  -> point-in-time feature rows
  -> CSV export
  -> Python evaluation harness
```

これは実務でいう warehouse / dbt / offline evaluation batch の学習版です。

## 7. Rule-Based Scoring と ML Baseline の違い

rule-based scoring は、人間が条件と重みを決めます。

たとえば、作成直後、contacts が多い、messages が多い、failed login が多い、block rate が高い、といった観察から加点します。なぜ score が上がったかを読みやすい一方、重みの調整は人間の仮説に依存します。

ML baseline は、feature row と label から重みを学習します。このプロジェクトでは logistic regression を使い、出力 probability を 0 から 100 の `risk_score` に変換しました。

違いはありますが、評価時の形は同じです。

```text
feature row -> scoring function -> risk_score -> threshold sweep
```

重要なのは、ML model も学習後は `label_value` を見ずに score を返す関数として扱うことです。学習時には label を使いますが、scoring 時には feature だけを使います。

## 8. Precision / Recall / Threshold Sweep の理解

precision は、検知したもののうち本当に positive だった割合です。

recall は、本当の positive のうち検知できた割合です。

不正検知では、threshold を上げると検知対象は絞られ、precision は上がりやすく、recall は下がりやすくなります。threshold を下げるとより多く拾えますが、false positive も増えやすくなります。

threshold sweep は、この trade-off を表で見るための方法です。

単一の threshold だけを見ると、「どの運用判断を選んだ結果なのか」が分かりにくくなります。threshold を 0 から 100 まで動かすことで、review capacity やユーザー影響に合わせてどの threshold が現実的かを考えやすくなります。

## 9. False Positive / False Negative から学べること

false positive は、正常なのに abuse と判定した行です。

false negative は、abuse なのに見逃した行です。

false positive からは、正常な高活動ユーザー、キャンペーン、サポート対応、成長中の legitimate user などを誤検知していないかを学べます。これは、どの feature が強すぎるか、どの segment に別 threshold が必要かを考える材料になります。

false negative からは、現在の feature では見えていない攻撃パターンを学べます。たとえば、低頻度で長期間潜む sleeper account や、行動量は少ないが質的に怪しいアカウントは、単純な volume feature だけでは拾いにくい可能性があります。

error analysis は、metrics の後に行う作業です。precision / recall は問題の大きさを教えてくれますが、何を直すべきかは FP / FN の中身を見ないと分かりません。

## 10. Negative Sampling の難しさ

不正検知では、positive label は human suspend や human review から比較的作りやすい一方、negative label は難しいです。

「停止されていないユーザー」は、必ずしも「正常ユーザー」ではありません。未発見の abuse、まだレビューされていない abuse、将来動き出す sleeper account が混ざる可能性があります。

雑に `label_value = 0` を全部 negative として使うと、モデルが未発見 abuse を正常として学習してしまう危険があります。

このプロジェクトでは、stable negative candidate を選ぶ helper を作り、作成直後、行動量が多い、failed login が多い、block rate が高い、といった怪しい negative 候補を除外しました。

ただし、negative をきれいにしすぎると、実運用 traffic から離れた簡単すぎるデータになる危険もあります。negative sampling は、単なる前処理ではなく、training data を設計する作業です。

## 11. Rolling Window Evaluation と攻撃者ドリフト

rolling window evaluation は、期間ごとに metrics を分けて見る方法です。

全期間をまとめた precision / recall だけでは、ある週だけ false positive が増えた、ある期間だけ false negative が増えた、といった変化を見落とします。

不正検知では、攻撃者の行動が時間で変わります。たとえば、最初は大量 message が特徴だった攻撃が、次の週には低頻度で長く潜む形に変わるかもしれません。また、正常ユーザー側のキャンペーンや季節イベントで行動量が増え、既存 threshold の false positive が増えることもあります。

Phase 7 では、複数時点の synthetic fixture を作り、window ごとの precision drop を観察できるようにしました。これにより、random split より time-based split の方が、未来に通用するかを見るうえで自然だと理解できました。

## 12. Score Calibration と Threshold Sweep の違い

threshold sweep は、score をどこで切るかを変えながら precision / recall を見る方法です。

score calibration は、score の数値そのものが確率として読めるかを見る考え方です。

たとえば score 80 の bucket にいるユーザーの observed positive rate が 80% に近ければ、その score は確率らしく読めます。score 80 なのに observed positive rate が 40% なら、その score は高く出すぎている可能性があります。

rule-based score は、人間が重みを足した点数なので、通常は確率ではありません。logistic regression は probability を出しますが、小さな fixture で学習した probability が本当に校正済みとは限りません。

不正検知では、常に calibration が最重要とは限りません。review queue の優先順位付けが目的なら、確率として正しいことより ranking が有用なこともあります。一方で、risk score を運用 SLA や自動アクションの基準に使うなら、calibration の確認は重要になります。

## 13. 本番化するなら足りないもの

このプロジェクトは学習用なので、本番化には多くの要素が足りません。

足りないものは、主に次です。

* 実データではなく、合成 fixture だけで検証している
* label quality の確認がない
* review policy と teacher label の定義が簡略化されている
* feature freshness、遅延、欠損、backfill の扱いがない
* model registry や approval workflow がない
* online serving と offline evaluation の一致確認がない
* monitoring、alerting、drift detection がない
* bias / fairness / user impact の確認がない
* 誤検知時の人間レビュー、異議申し立て、解除フローがない
* secrets、権限、監査ログ、データ保持ポリシーを扱っていない
* A/B test、shadow mode、段階 rollout の設計がない

本番化では、モデル性能だけでなく、ユーザー影響、運用負荷、説明責任、データガバナンスを含めて設計する必要があります。

## 14. 次に学ぶべきこと

次に学ぶとよいのは、評価を「一回の notebook 実行」から「継続的に比較できる evaluation system」に近づけることです。

具体的には、次の順番がよさそうです。

1. evaluation run の保存
   * `run_id`、`score_source`、`score_version`、評価期間、threshold metrics、scored rows を保存する。

2. segment 別評価
   * plan、signup method、国、account age bucket、traffic pattern などで precision / recall を分ける。

3. label delay の扱い
   * `as_of_time` と `label_time` の関係を明示し、未来 label をいつ評価に使えるか整理する。

4. online / offline feature consistency
   * offline で作った feature と online scoring 時に使える feature が一致するか確認する。

5. drift monitoring
   * feature distribution、score distribution、positive rate、FP / FN の傾向を期間ごとに見る。

6. review queue design
   * threshold だけでなく、review capacity、priority、manual action、feedback loop を設計する。

7. model governance
   * model version、training data、evaluation result、承認履歴、rollback 方針を管理する。

このプロジェクトで最も大事だった学びは、モデル単体ではなく、次の流れ全体を設計することです。

```text
feature row
  -> scoring function
  -> risk_score
  -> threshold decision
  -> precision / recall
  -> error analysis
  -> data and model iteration
```

