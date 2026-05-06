# Phase 7: Practical Evaluation Improvements

Phase 7 では、これまで作った評価の器を、もう少し実務に近い形で使えるようにする。

最初の改善は、複数時点の合成 feature rows を作ることである。

## 複数時点 fixture

これまでの `fixtures/feature_rows_sample.csv` は、`as_of_time` が1時点だけだった。

そのため rolling window evaluation の helper はあっても、実際には1 window しか出なかった。

今回、`scripts/build_timeseries_fixture.py` を追加し、次の fixture を生成した。

```text
fixtures/feature_rows_timeseries.csv
```

この fixture は、元の100行を4週間分に展開した400行の合成データである。

```text
2026-05-01: 100 rows
2026-05-08: 100 rows
2026-05-15: 100 rows
2026-05-22: 100 rows
```

一部の週では、growth 系、sleeper 系、credential attack 系の特徴量を少し変えている。これにより、window ごとの評価差を観察しやすくしている。

特に4週目には、正常な campaign / support burst 系の行動量を増やしている。

このため、rule-based scoring では4週目の false positive が増え、precision が落ちる。

```text
week 1: precision 0.84375 / fp 5
week 4: precision 0.642857 / fp 15
```

ML baseline でも4週目に false positive が増えるが、rule-based よりは落ち方が小さい。

```text
week 1: precision 1.0 / fp 0
week 4: precision 0.818182 / fp 10
```

## Time-based Split

ML baseline には、ランダム split に加えて time-based split を追加した。

```text
past rows   -> train
future rows -> validation
```

実行例:

```bash
.venv/bin/python scripts/train_ml_baseline.py \
  --feature-rows fixtures/feature_rows_timeseries.csv \
  --artifact-dir models/ml_baseline_timeseries_v001 \
  --split-strategy time \
  --validation-start 2026-05-15T00:00:00Z
```

これは、過去のデータで学習し、未来のデータで評価する考え方に近い。

## 学び

ランダム split は最初の確認には便利だが、実務の offline evaluation では楽観的になることがある。

不正検知では攻撃パターンが時間で変わるため、時間で分けた validation の方が「未来に通用するか」を見やすい。
