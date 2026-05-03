# Phase 4: Error Analysis

Phase 4 では、評価済みの feature rows から false positive / false negative を取り出し、score bucket ごとに誤りを観察できるようにした。

## 何を作ったか

`src/abuse_detection/error_analysis.py` に、次の helper を追加した。

* `false_positives(scored_rows, threshold)`
* `false_negatives(scored_rows, threshold)`
* `score_bucket_summary(scored_rows, bucket_size, threshold)`

これらは scoring logic ではなく、評価後の観察用 helper である。

また、`notebooks/02_error_analysis.ipynb` を追加し、helper の出力を表として読めるようにした。

この notebook では、次の順番で観察する。

1. feature rows を読み込む
2. `scoring_fn` で `risk_score` を付ける
3. threshold=80 の precision / recall を見る
4. score bucket ごとの分布を見る
5. false positives を読む
6. false negatives を読む
7. FP / FN の特徴量平均を全体平均と比べる

## なぜ必要か

precision / recall は全体の性能を見るには便利だが、どの種類の行が誤判定されているかは分からない。

false positives / false negatives を行として取り出すと、次のような問いを立てられる。

* 正常ユーザーなのに高 score になった理由は何か
* abuse ユーザーなのに低 score になった理由は何か
* 誤りは特定の score bucket に偏っているか
* threshold を動かすと、どの誤りが増減するか

## score bucket の読み方

`score_bucket_summary` は、risk score を 0-20、20-40、40-60 のような bucket に分ける。

各 bucket では、次を確認する。

* `row_count`: その score 帯に入った行数
* `positive_count`: label が 1 の行数
* `negative_count`: label が 0 の行数
* `false_positive_count`: threshold 以上だが label が 0 の行数
* `false_negative_count`: threshold 未満だが label が 1 の行数

score bucket は、個別行を見る前の地図として使う。例えば高 score bucket に negative が多いなら、正常ユーザーを強く疑いすぎている可能性がある。

## notebook が必要だった理由

helper だけでは、Phase 4 の学習効果は弱い。

error analysis では、関数を作ることよりも、実際に表を見て次の問いを立てることが重要である。

* どの row が false positive になったか
* どの row が false negative になったか
* それぞれの row は、どの特徴量で高く、どの特徴量で低いか
* score bucket のどこに誤りが集まっているか

そのため、Phase 4 では helper に加えて notebook を作った。

`02_error_analysis.ipynb` は、人間が error analysis を読むための作業台である。

## ML への接続

Phase 4 の error analysis は、rule-based scoring だけでなく ML baseline にも接続できる。

重要なのは、rule-based でも ML でも、最終的な出力を次の形にそろえることである。

```text
feature row -> risk_score
```

ML baseline では、logistic regression などの model が abuse probability を出す。その probability を 0 から 100 の `risk_score` に変換すれば、同じ evaluation harness と error analysis helper を使える。

つまり、Phase 5 では次の比較ができる。

* rule-based scoring の false positives
* ML-based scoring の false positives
* rule-based scoring の false negatives
* ML-based scoring の false negatives
* rule-based では外したが ML では拾えた row
* ML で新しく増えた誤判定 row

このため、Phase 4 は ML の前処理ではなく、ML を評価して改善するための観察基盤である。

## scoring_fn 改善メモ

次に改善するなら、いきなり ML に進む前に、次の観察をする。

* false positive に多い `plan` や `account_age_minutes` の傾向を見る
* false negative に多い `failed_login_count_24h` や `login_country_changes_24h` の傾向を見る
* threshold=80 だけでなく、60 / 70 / 90 でも FP/FN を比較する
* score bucket ごとの positive rate を見て、score が label の強さを反映しているか確認する

この段階では、`scoring_fn` が label を直接見ていないことが重要である。label は評価と error analysis のためだけに使う。
