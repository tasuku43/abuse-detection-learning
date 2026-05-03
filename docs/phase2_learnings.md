# Phase 2 Learnings

Phase 2 では、Phase 1 で作った evaluation harness を notebook から動かし、`scoring_fn` と threshold の関係を観察しました。

このフェーズの目的は、scoring logic を notebook に移すことではありません。

目的は、`src/` にある評価処理を呼び出し、結果を手で見ながら改善候補を考えることです。

## Notebook の役割

notebook は、評価処理の本体を書く場所ではなく、観察する場所です。

```text
src/
  scoring logic や metrics の本体を置く

notebooks/
  同じ処理を手で動かし、表を見ながら理解する
```

Phase 2 の notebook では、次を観察できるようにしました。

* fixture CSV の feature row
* scoring_fn ごとの risk_score
* threshold ごとの precision / recall / TP / FP / FN
* threshold=80 に固定したときの scoring_fn 比較
* false positives / false negatives の具体的な行

## Threshold と Scoring Function

`scoring_fn` は feature row を受け取り、`risk_score` を返します。

threshold は、その `risk_score` を使って abuse と予測する境界です。

```text
risk_score >= threshold
  -> abuse と予測する

risk_score < threshold
  -> non-abuse と予測する
```

threshold を上げると、abuse と予測する条件は厳しくなります。

そのため false positive は減りやすくなりますが、true positive も減りやすく、false negative は増えやすくなります。

ただし、threshold を上げても、極端に高い score が付いた false positive は残ります。

その場合は threshold だけでは直せず、`scoring_fn` の score の付け方を見直す必要があります。

## Metrics の読み方

notebook では次の metrics を見ます。

* `threshold`: `risk_score` が何点以上なら abuse と予測するか
* `precision`: abuse と予測したもののうち、実際に abuse だった割合
* `recall`: 実際の abuse のうち、検知できた割合
* `tp`: true positive。abuse と予測し、実際にも abuse だった件数
* `fp`: false positive。abuse と予測したが、実際は non-abuse だった件数
* `fn`: false negative。non-abuse と予測したが、実際は abuse だった件数

ざっくり言うと、precision は誤検知の少なさ、recall は見逃しの少なさを見る指標です。

## 複数 Scoring Function の比較

Phase 2 では、3つの scoring function を比較しました。

* `baseline`
  * 最初に作った基準のルールベース score
* `conservative`
  * false positive を減らす方向の score
* `recall_heavy`
  * false negative を減らす方向の score

同じ fixture、同じ threshold、同じ metrics で比較すると、評価 harness が scoring function を差し替える器になっていることが分かります。

```text
feature row
  -> scoring_fn_a
  -> risk_score
  -> metrics

feature row
  -> scoring_fn_b
  -> risk_score
  -> metrics
```

この形を守ると、将来 `scoring_fn` の中身を ML model に差し替えても、同じ evaluation harness で比較できます。

## 特徴量を増やして分かったこと

Phase 2 では、fixture を100件の合成ユーザーに増やし、特徴量も追加しました。

追加した特徴量:

* `device_count_24h`
* `failed_login_count_24h`
* `login_country_changes_24h`
* `password_reset_24h`
* `recipient_block_rate_24h`
* `message_link_ratio_1h`

特徴量を増やすと、同じ threshold でも scoring function ごとの差が見えやすくなります。

一方で、特徴量を増やせば自動的に良くなるわけではありません。

特徴量が増えるほど、次のリスクも増えます。

* 本来は予測時点で見えない情報が混ざる leakage
* training data にだけある偶然の相関を拾う過学習
* 特徴量の欠損や品質問題
* 実運用で作れない重い特徴量
* なぜ高 score になったか説明しづらくなること

そのため、特徴量は広めに候補を作りつつ、評価と error analysis で絞る必要があります。

## ML への橋渡し

ML に移行しても、基本の形は変わりません。

```text
feature row -> scoring_fn -> risk_score -> threshold sweep -> precision / recall -> error analysis
```

変わるのは `scoring_fn` の中身です。

```text
rule-based scoring_fn
  -> 人間が条件と重みを書く

ML-based scoring_fn
  -> 学習済みモデルが risk_score を返す
```

ML は、与えられた特徴量の中で label と関係しそうなパターンを学習できます。

ただし、何を特徴量として渡すか、leakage がないか、運用で作れるか、失敗例が納得できるかは人間が確認する必要があります。

## 次に見るべきこと

Phase 3 に進む前に、feature row がどこから来るのかを考えます。

具体的には dbt skeleton で、次を表現します。

* raw event から staging model を作る
* human operator の停止イベントから label source を作る
* evaluation target を作る
* `user_id + as_of_time` の粒度で feature row を作る
* `event_time < as_of_time` により未来情報の混入を防ぐ
* auto actor の停止結果を teacher label に混ぜない

Phase 1 と Phase 2 では、すでに feature row が存在する前提で評価しました。

Phase 3 では、その feature row をどう作るべきかを SQL skeleton として表現します。

