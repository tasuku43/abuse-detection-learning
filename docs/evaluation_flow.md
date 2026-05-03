# Evaluation Flow

このドキュメントは、Phase 1 で実装した最小 evaluation harness の処理の流れを図で整理したものです。

目的は、次の流れをコードを読む前に掴めるようにすることです。

```text
feature row -> scoring_fn -> risk_score -> threshold sweep -> precision/recall -> error analysis
```

## 全体フロー

```mermaid
flowchart TD
    A["fixtures/feature_rows_sample.csv<br/>合成 feature row"] --> B["load_feature_rows(path)<br/>CSV を DataFrame として読み込む"]
    B --> C["validate_feature_rows(feature_rows)<br/>必須カラムを検証する"]
    C --> D["add_risk_scores(feature_rows)<br/>各行に scoring_fn を適用する"]
    D --> E["scoring_fn(features)<br/>feature row から risk_score を返す"]
    E --> F["scored rows<br/>元の行 + risk_score"]
    F --> G["threshold_sweep(labels, scores, thresholds)<br/>threshold ごとに評価する"]
    G --> H["metrics DataFrame<br/>threshold / precision / recall / TP / FP / FN"]
    F --> I["false_positives(scored_rows, threshold)<br/>誤検知を確認する"]
    F --> J["false_negatives(scored_rows, threshold)<br/>見逃しを確認する"]
```

## 責務の分離

```mermaid
flowchart LR
    subgraph Fixture["fixtures/"]
        A["feature_rows_sample.csv<br/>合成データのみ"]
    end

    subgraph Schema["schema.py"]
        B["ScoringFeatureRow<br/>scoring_fn が読む特徴量"]
        C["LabeledFeatureRow<br/>評価用の label 付き feature row"]
        D["validate_feature_rows<br/>必須カラム検証"]
    end

    subgraph Scoring["scoring.py"]
        E["scoring_fn<br/>feature row -> risk_score"]
    end

    subgraph Metrics["metrics.py"]
        F["precision_recall_at_threshold<br/>1つの threshold を評価"]
        G["threshold_sweep<br/>複数 threshold を評価"]
    end

    subgraph Evaluation["evaluation.py"]
        H["load_feature_rows<br/>CSV 読み込み"]
        I["add_risk_scores<br/>risk_score 付与"]
        J["evaluate_feature_rows<br/>scoring と metrics をつなぐ"]
        K["false_positives / false_negatives<br/>error analysis の入口"]
    end

    A --> H
    H --> D
    D --> I
    B --> E
    I --> E
    I --> J
    J --> G
    G --> F
    J --> K
```

## 型とラベルの境界

`scoring_fn` は `ScoringFeatureRow` だけを受け取ります。

`ScoringFeatureRow` には `label_value` を含めません。これは、score を出す処理が正解ラベルを見ないようにするためです。

```mermaid
flowchart TD
    A["LabeledFeatureRow<br/>user_id / as_of_time / label_value / features"] --> B["evaluation.py<br/>評価では label_value を使う"]
    A --> C["ScoringFeatureRow<br/>account_age_minutes / contacts_24h / messages_1h / profile_updates_24h / plan"]
    C --> D["scoring_fn(features)<br/>label_value を見ずに risk_score を計算"]
    D --> E["risk_score"]
    B --> F["metrics.py<br/>label_value と risk_score を比較"]
    E --> F
```

## threshold 評価

`risk_score >= threshold` の行を abuse と予測します。

threshold を変えると、precision と recall のバランスが変わります。

```mermaid
flowchart TD
    A["scored rows<br/>label_value + risk_score"] --> B["threshold を1つ選ぶ"]
    B --> C{"risk_score >= threshold ?"}
    C -->|yes| D["predicted_abuse = True"]
    C -->|no| E["predicted_abuse = False"]
    D --> F{"label_value == 1 ?"}
    E --> G{"label_value == 1 ?"}
    F -->|yes| H["TP<br/>正しく検知"]
    F -->|no| I["FP<br/>誤検知"]
    G -->|yes| J["FN<br/>見逃し"]
    G -->|no| K["TN<br/>正しく非検知"]
    H --> L["precision = TP / (TP + FP)"]
    I --> L
    H --> M["recall = TP / (TP + FN)"]
    J --> M
```

## error analysis の入口

Phase 1 では、まず false positive と false negative を取り出せるようにしています。

これにより、score や metrics の数字だけでなく、どの feature row を間違えたのかを確認できます。

```mermaid
flowchart LR
    A["scored rows"] --> B["threshold=80 などを決める"]
    B --> C["false_positives<br/>risk_score >= threshold<br/>かつ label_value == 0"]
    B --> D["false_negatives<br/>risk_score < threshold<br/>かつ label_value == 1"]
    C --> E["誤検知しやすい正常例を観察する"]
    D --> F["見逃しやすい abuse 例を観察する"]
    E --> G["scoring_fn の改善候補を考える"]
    F --> G
```

## コードを読む順番

1. `fixtures/feature_rows_sample.csv`
2. `src/abuse_detection/schema.py`
3. `src/abuse_detection/scoring.py`
4. `src/abuse_detection/metrics.py`
5. `src/abuse_detection/evaluation.py`
6. `tests/`

この順番で読むと、データの形、入力契約、score 計算、評価指標、pipeline、テストの対応関係が追いやすくなります。

