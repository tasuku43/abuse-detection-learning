# Phase 6: Score Calibration

Score calibration は、score を「順位」ではなく「確率らしい値」として読めるかを確認する考え方である。

threshold sweep は、ある threshold で precision / recall がどう変わるかを見る。

calibration は、例えば score 80 前後の行が本当に約80%の確率で positive になっているかを見る。

## 今回の最小実装

`calibration_by_score_bucket` は、score を bucket に分けて次を並べる。

* `average_score`
* `average_score_probability`
* `positive_rate`
* `calibration_gap`

実行方法:

```bash
.venv/bin/python scripts/inspect_score_calibration.py --score-source ml
```

rule-based score でも確認できる。

```bash
.venv/bin/python scripts/inspect_score_calibration.py --score-source rule
```

## 読み方

`average_score_probability` が 0.80 で、`positive_rate` も 0.80 に近ければ、その bucket は確率らしく読める。

一方で、`average_score_probability` が 0.80 なのに `positive_rate` が 0.40 なら、score は高すぎる可能性がある。

このリポジトリの rule-based score は、人間が重みを足した点数であり、確率として作っていない。そのため calibration はよくない可能性がある。

logistic regression は probability を出すが、小さな fixture で学習しているため、その probability も実務的に校正済みとは言えない。

## threshold sweep との違い

threshold sweep は、判定基準を動かして precision / recall を見る。

score calibration は、score の数値そのものが確率として読めるかを見る。

不正検知では、必ずしも score を確率として使う必要はない。review queue の順位付けに使うなら、calibration より ranking の方が重要な場合もある。
