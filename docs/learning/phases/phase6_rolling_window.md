# Phase 6: Rolling Window Evaluation

Rolling window evaluation は、評価期間を分けて precision / recall を見る方法である。

全期間をまとめて評価すると、特定の期間だけ性能が悪いことを見落としやすい。

```text
all rows -> overall precision / recall
```

だけではなく、次のように見る。

```text
week 1 -> precision / recall
week 2 -> precision / recall
week 3 -> precision / recall
```

## 今回の実装

`rolling_window_metrics` は、score 済み rows を `as_of_time` の window に分け、window ごとに同じ threshold で metrics を計算する。

```bash
.venv/bin/python scripts/evaluate_rolling_windows.py --score-source ml --window 7D --threshold 80
```

現状の `fixtures/feature_rows_sample.csv` は `as_of_time` が1時点だけなので、window は1つだけ出る。

この状態でも、helper の形は確認できる。今後、複数日・複数週の fixture や SQLite export を作ると、window ごとの変化を観察できる。

## 実務上の読み方

window ごとに性能が違う場合、すぐに時間帯別 model を作るとは限らない。

まず確認するのは次である。

* row count が少なすぎて指標がブレていないか
* false positive が増えているのか
* false negative が増えているのか
* 攻撃パターンが変わったのか
* feature が古くなっているのか
* threshold 変更で対応できるのか

それでも特定 window だけ挙動が大きく違う場合に、segment 別 threshold、追加 feature、別 model を検討する。
