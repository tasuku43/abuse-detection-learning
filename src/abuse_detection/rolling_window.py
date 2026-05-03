from __future__ import annotations

import pandas as pd

from abuse_detection.metrics import precision_recall_at_threshold


def rolling_window_metrics(
    scored_rows: pd.DataFrame,
    *,
    threshold: float,
    window: str = "7D",
    time_column: str = "as_of_time",
) -> pd.DataFrame:
    """Calculate precision/recall for each time window."""
    required_columns = {time_column, "label_value", "risk_score"}
    missing = required_columns - set(scored_rows.columns)
    if missing:
        raise ValueError(f"Missing scored row columns: {', '.join(sorted(missing))}")

    rows = scored_rows.copy()
    rows[time_column] = pd.to_datetime(rows[time_column], utc=True)
    rows["window_start"] = rows[time_column].dt.floor(window)

    metric_rows: list[dict[str, object]] = []
    for window_start, window_rows in rows.groupby("window_start", sort=True):
        metrics = precision_recall_at_threshold(
            labels=window_rows["label_value"],
            scores=window_rows["risk_score"],
            threshold=threshold,
        )
        metric_rows.append(
            {
                "window_start": window_start,
                "window_end": window_start + pd.Timedelta(window),
                "row_count": int(len(window_rows)),
                "positive_count": int(window_rows["label_value"].sum()),
                "negative_count": int(len(window_rows) - window_rows["label_value"].sum()),
                **metrics.__dict__,
            }
        )

    return pd.DataFrame(metric_rows)
