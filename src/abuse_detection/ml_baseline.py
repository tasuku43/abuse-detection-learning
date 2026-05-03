from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from abuse_detection.metrics import precision_recall_at_threshold
from abuse_detection.schema import ScoringFeatureRow, validate_feature_rows


NUMERIC_FEATURE_COLUMNS: tuple[str, ...] = (
    "account_age_minutes",
    "contacts_24h",
    "messages_1h",
    "profile_updates_24h",
    "device_count_24h",
    "failed_login_count_24h",
    "login_country_changes_24h",
    "password_reset_24h",
    "recipient_block_rate_24h",
    "message_link_ratio_1h",
)

CATEGORICAL_FEATURE_COLUMNS: tuple[str, ...] = ("plan",)

ML_FEATURE_COLUMNS: tuple[str, ...] = (
    *NUMERIC_FEATURE_COLUMNS,
    *CATEGORICAL_FEATURE_COLUMNS,
)

ML_BASELINE_MODEL_NAME = "ml_baseline"
DEFAULT_ML_BASELINE_VERSION = "v001"


@dataclass(frozen=True)
class MLScoringModel:
    """Small logistic-regression scorer that returns a 0-100 risk score."""

    pipeline: Pipeline

    def score_row(self, features: ScoringFeatureRow) -> float:
        """Score one feature row without reading the label."""
        feature_frame = pd.DataFrame(
            [{column: features[column] for column in ML_FEATURE_COLUMNS}]  # type: ignore[literal-required]
        )
        probability = self.pipeline.predict_proba(feature_frame)[0][1]
        return float(max(0.0, min(100.0, probability * 100.0)))


@dataclass(frozen=True)
class MLModelArtifact:
    """Saved model files that can be loaded in a later process."""

    model_path: Path
    metadata_path: Path


@dataclass(frozen=True)
class TrainValidationSplit:
    """Labeled feature rows split into train and validation sets."""

    train_rows: pd.DataFrame
    validation_rows: pd.DataFrame


def _feature_matrix(feature_rows: pd.DataFrame) -> pd.DataFrame:
    return feature_rows.loc[:, ML_FEATURE_COLUMNS].copy()


def build_logistic_regression_pipeline() -> Pipeline:
    """Build the preprocessing and logistic-regression pipeline."""
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                StandardScaler(),
                list(NUMERIC_FEATURE_COLUMNS),
            ),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                list(CATEGORICAL_FEATURE_COLUMNS),
            ),
        ],
    )
    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", LogisticRegression(max_iter=1000, random_state=0)),
        ],
    )


def train_ml_baseline(feature_rows: pd.DataFrame) -> MLScoringModel:
    """Train a logistic-regression baseline from labeled feature rows."""
    validate_feature_rows(feature_rows)
    labels = feature_rows["label_value"].astype(int)
    pipeline = build_logistic_regression_pipeline()
    pipeline.fit(_feature_matrix(feature_rows), labels)
    return MLScoringModel(pipeline=pipeline)


def split_train_validation(
    feature_rows: pd.DataFrame,
    *,
    validation_size: float = 0.3,
    random_state: int = 0,
) -> TrainValidationSplit:
    """Split labeled feature rows while preserving label balance."""
    validate_feature_rows(feature_rows)
    train_rows, validation_rows = train_test_split(
        feature_rows,
        test_size=validation_size,
        random_state=random_state,
        stratify=feature_rows["label_value"],
    )
    return TrainValidationSplit(
        train_rows=train_rows.reset_index(drop=True),
        validation_rows=validation_rows.reset_index(drop=True),
    )


def save_ml_model(
    model: MLScoringModel,
    artifact_dir: str | Path,
    *,
    metadata: dict[str, object] | None = None,
) -> MLModelArtifact:
    """Save a trained ML model plus human-readable metadata."""
    artifact_path = Path(artifact_dir)
    artifact_path.mkdir(parents=True, exist_ok=True)

    model_path = artifact_path / "model.joblib"
    metadata_path = artifact_path / "metadata.json"

    joblib.dump(model, model_path)

    metadata_payload: dict[str, object] = {
        "model_name": ML_BASELINE_MODEL_NAME,
        "model_type": "logistic_regression",
        "created_at": datetime.now(UTC).isoformat(),
        "feature_columns": list(ML_FEATURE_COLUMNS),
        "label_column": "label_value",
        "model_file": model_path.name,
    }
    if metadata:
        metadata_payload.update(metadata)

    metadata_path.write_text(
        json.dumps(metadata_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return MLModelArtifact(model_path=model_path, metadata_path=metadata_path)


def load_ml_model(artifact_dir: str | Path) -> MLScoringModel:
    """Load a saved ML model artifact."""
    model_path = Path(artifact_dir) / "model.joblib"
    loaded = joblib.load(model_path)
    if not isinstance(loaded, MLScoringModel):
        raise TypeError(f"Expected MLScoringModel in {model_path}")
    return loaded


def load_ml_model_metadata(artifact_dir: str | Path) -> dict[str, object]:
    """Load metadata saved next to a model artifact."""
    metadata_path = Path(artifact_dir) / "metadata.json"
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def build_ml_model_metadata(
    training_rows: pd.DataFrame,
    model: MLScoringModel,
    *,
    training_data_path: str,
    model_version: str,
    threshold: float = 80,
    validation_rows: pd.DataFrame | None = None,
    validation_size: float | None = None,
    random_state: int | None = None,
) -> dict[str, object]:
    """Build metadata that explains how the artifact was created."""
    validate_feature_rows(training_rows)
    evaluation_rows = validation_rows if validation_rows is not None else training_rows
    validate_feature_rows(evaluation_rows)

    scores = evaluation_rows.apply(lambda row: model.score_row(row.to_dict()), axis=1)
    metrics = precision_recall_at_threshold(
        labels=evaluation_rows["label_value"],
        scores=scores,
        threshold=threshold,
    )
    metadata: dict[str, object] = {
        "model_version": model_version,
        "training_data": training_data_path,
        "training_row_count": int(len(training_rows)),
        "evaluation_row_count": int(len(evaluation_rows)),
        "evaluation_data_role": "validation"
        if validation_rows is not None
        else "training",
        "evaluation_threshold": threshold,
        "precision_at_threshold": metrics.precision,
        "recall_at_threshold": metrics.recall,
        "tp_at_threshold": metrics.tp,
        "fp_at_threshold": metrics.fp,
        "fn_at_threshold": metrics.fn,
    }
    if validation_rows is None:
        metadata["warning"] = (
            "This learning baseline evaluates on the same fixture used for training."
        )
    else:
        metadata["validation_row_count"] = int(len(validation_rows))
        metadata["validation_size"] = validation_size
        metadata["random_state"] = random_state
    return metadata
