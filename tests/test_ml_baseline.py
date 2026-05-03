import pandas as pd

from abuse_detection.evaluation import evaluate_feature_rows
from abuse_detection.ml_baseline import (
    build_ml_model_metadata,
    load_ml_model,
    load_ml_model_metadata,
    save_ml_model,
    split_train_validation,
    split_train_validation_by_time,
    train_ml_baseline,
)


def test_ml_baseline_scores_rows_between_0_and_100() -> None:
    feature_rows = pd.read_csv("fixtures/feature_rows_sample.csv")
    model = train_ml_baseline(feature_rows)

    score = model.score_row(feature_rows.iloc[0].to_dict())

    assert 0 <= score <= 100


def test_ml_baseline_can_use_existing_evaluation_harness() -> None:
    feature_rows = pd.read_csv("fixtures/feature_rows_sample.csv")
    model = train_ml_baseline(feature_rows)

    scored_rows, metrics = evaluate_feature_rows(
        feature_rows,
        thresholds=[50, 80],
        score_fn=model.score_row,
    )

    assert "risk_score" in scored_rows.columns
    assert list(metrics["threshold"]) == [50, 80]
    assert set(metrics.columns) == {"threshold", "precision", "recall", "tp", "fp", "fn"}


def test_ml_baseline_does_not_require_label_when_scoring_one_row() -> None:
    feature_rows = pd.read_csv("fixtures/feature_rows_sample.csv")
    model = train_ml_baseline(feature_rows)
    unlabeled_row = feature_rows.drop(columns=["label_value"]).iloc[0].to_dict()

    score = model.score_row(unlabeled_row)

    assert 0 <= score <= 100


def test_saved_ml_baseline_can_be_loaded_and_evaluated(tmp_path) -> None:
    feature_rows = pd.read_csv("fixtures/feature_rows_sample.csv")
    model = train_ml_baseline(feature_rows)
    metadata = build_ml_model_metadata(
        feature_rows,
        model,
        training_data_path="fixtures/feature_rows_sample.csv",
        model_version="test",
        threshold=80,
    )

    artifact = save_ml_model(model, tmp_path / "ml_baseline_test", metadata=metadata)
    loaded_model = load_ml_model(tmp_path / "ml_baseline_test")
    _, metrics = evaluate_feature_rows(
        feature_rows,
        thresholds=[80],
        score_fn=loaded_model.score_row,
    )

    assert artifact.model_path.exists()
    assert artifact.metadata_path.exists()
    assert metrics.loc[0, "threshold"] == 80
    assert 0 <= metadata["precision_at_threshold"] <= 1
    assert 0 <= metadata["recall_at_threshold"] <= 1


def test_saved_ml_baseline_metadata_can_be_loaded(tmp_path) -> None:
    feature_rows = pd.read_csv("fixtures/feature_rows_sample.csv")
    model = train_ml_baseline(feature_rows)
    save_ml_model(
        model,
        tmp_path / "ml_baseline_test",
        metadata={"model_version": "test"},
    )

    metadata = load_ml_model_metadata(tmp_path / "ml_baseline_test")

    assert metadata["model_name"] == "ml_baseline"
    assert metadata["model_version"] == "test"


def test_train_validation_split_preserves_label_balance() -> None:
    feature_rows = pd.read_csv("fixtures/feature_rows_sample.csv")

    split = split_train_validation(feature_rows, validation_size=0.3, random_state=0)

    assert len(split.train_rows) == 70
    assert len(split.validation_rows) == 30
    assert set(split.train_rows["label_value"]) == {0, 1}
    assert set(split.validation_rows["label_value"]) == {0, 1}


def test_time_based_train_validation_split_uses_future_rows_for_validation() -> None:
    feature_rows = pd.read_csv("fixtures/feature_rows_timeseries.csv")

    split = split_train_validation_by_time(
        feature_rows,
        validation_start="2026-05-15T00:00:00Z",
    )

    assert len(split.train_rows) == 200
    assert len(split.validation_rows) == 200
    assert split.train_rows["as_of_time"].max() < pd.Timestamp("2026-05-15T00:00:00Z")
    assert split.validation_rows["as_of_time"].min() >= pd.Timestamp(
        "2026-05-15T00:00:00Z"
    )
    assert set(split.train_rows["label_value"]) == {0, 1}
    assert set(split.validation_rows["label_value"]) == {0, 1}


def test_metadata_can_use_validation_rows() -> None:
    feature_rows = pd.read_csv("fixtures/feature_rows_sample.csv")
    split = split_train_validation(feature_rows, validation_size=0.3, random_state=0)
    model = train_ml_baseline(split.train_rows)

    metadata = build_ml_model_metadata(
        split.train_rows,
        model,
        training_data_path="fixtures/feature_rows_sample.csv",
        model_version="test",
        threshold=80,
        validation_rows=split.validation_rows,
        validation_size=0.3,
        random_state=0,
    )

    assert metadata["training_row_count"] == 70
    assert metadata["validation_row_count"] == 30
    assert metadata["evaluation_data_role"] == "validation"
    assert 0 <= metadata["precision_at_threshold"] <= 1
    assert 0 <= metadata["recall_at_threshold"] <= 1
