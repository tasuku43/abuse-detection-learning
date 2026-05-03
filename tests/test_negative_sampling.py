import pandas as pd

from abuse_detection.negative_sampling import (
    NegativeSamplingConfig,
    annotate_negative_candidates,
    sample_training_rows_with_negatives,
)


def test_annotate_negative_candidates_marks_stable_negatives() -> None:
    rows = pd.read_csv("fixtures/feature_rows_sample.csv")

    annotated = annotate_negative_candidates(rows)

    assert "negative_candidate" in annotated.columns
    assert "negative_exclusion_reason" in annotated.columns
    assert annotated["negative_candidate"].sum() > 0
    assert set(annotated[annotated["negative_candidate"]]["label_value"]) == {0}


def test_negative_sampling_excludes_new_high_volume_negative() -> None:
    rows = pd.read_csv("fixtures/feature_rows_sample.csv")

    annotated = annotate_negative_candidates(rows)
    fp_growth = annotated.set_index("user_id").loc["synthetic_fp_growth_003"]

    assert not bool(fp_growth["negative_candidate"])
    assert fp_growth["negative_exclusion_reason"] == "high_message_volume"


def test_sample_training_rows_with_negatives_respects_ratio() -> None:
    rows = pd.read_csv("fixtures/feature_rows_sample.csv")
    config = NegativeSamplingConfig(negative_to_positive_ratio=0.5, random_state=0)

    sampled = sample_training_rows_with_negatives(rows, config=config)

    label_counts = sampled["label_value"].value_counts().to_dict()
    assert label_counts[1] == 50
    assert label_counts[0] == 25
