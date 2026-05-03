import pandas as pd
import pytest

from abuse_detection.schema import missing_required_columns, validate_feature_rows


def test_missing_required_columns_detects_absent_columns() -> None:
    assert missing_required_columns(["user_id", "label_value"]) == [
        "as_of_time",
        "account_age_minutes",
        "contacts_24h",
        "messages_1h",
        "profile_updates_24h",
        "plan",
    ]


def test_validate_feature_rows_raises_for_missing_columns() -> None:
    feature_rows = pd.DataFrame({"user_id": ["synthetic_user"], "label_value": [0]})

    with pytest.raises(ValueError, match="Missing required feature columns"):
        validate_feature_rows(feature_rows)

