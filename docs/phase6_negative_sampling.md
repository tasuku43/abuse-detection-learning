# Phase 6: Negative Sampling

Negative sampling は、学習に使う負例をどう選ぶかを考える作業である。

不正検知では、`label_value = 1` は人間の確認や停止操作から比較的作りやすい。一方で、`label_value = 0` は単純ではない。

「停止されていないユーザー」は、必ずしも「正常ユーザー」とは限らない。まだ見つかっていない abuse、レビューされていない abuse、将来 abuse になる sleeper account が混ざる可能性がある。

## 今回の最小ルール

この学習リポジトリでは、まず fixture rows の中から安定した負例候補だけを選ぶ。

`NegativeSamplingConfig` の default では、次のような negative row を除外する。

* 作成直後のアカウント
* contacts がかなり多いアカウント
* messages がかなり多いアカウント
* failed login が多いアカウント
* recipient block rate が高いアカウント

これは「負例をきれいにしすぎる」危険もあるが、最初の学習では「明らかに怪しい未停止ユーザー」を負例として強く学習してしまうリスクを避けるためである。

## 実行方法

```bash
.venv/bin/python scripts/inspect_negative_sampling.py
```

この script は、負例候補として選ばれた行数と、除外理由を表示する。

## 学ぶこと

重要なのは、負例は自然に存在する正解ではなく、設計して作る training data だという点である。

雑に `label_value = 0` を全部使うと、次の問題が起きる。

* 未発見の abuse を正常として学習する
* 怪しいが許容される power user を正常として強く学習する
* negative sample の構成が実運用の traffic とずれる

今回の helper は完成形ではない。negative sampling の判断を見える化し、後から改善できる形にするための最小実装である。
