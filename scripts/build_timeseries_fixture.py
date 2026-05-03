from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def build_timeseries_fixture(
    input_path: str | Path,
    output_path: str | Path,
    *,
    weeks: int = 4,
) -> None:
    """Expand the one-point fixture into weekly synthetic evaluation windows."""
    base_rows = pd.read_csv(input_path)
    base_time = pd.Timestamp("2026-05-01T10:00:00Z")
    expanded: list[pd.DataFrame] = []

    for week in range(weeks):
        rows = base_rows.copy()
        rows["as_of_time"] = (base_time + pd.Timedelta(days=7 * week)).isoformat()
        rows["user_id"] = rows["user_id"].str.replace("synthetic_", f"synthetic_w{week + 1}_", regex=False)

        # Make later windows slightly different so rolling metrics have something to reveal.
        if week == 1:
            growth = rows["user_id"].str.contains("fp_growth|marketing_launch")
            rows.loc[growth, "contacts_24h"] += 15
            rows.loc[growth, "messages_1h"] += 10
        elif week == 2:
            sleeper = rows["user_id"].str.contains("fn_sleeper")
            rows.loc[sleeper, "contacts_24h"] += 8
            rows.loc[sleeper, "messages_1h"] += 8
            rows.loc[sleeper, "failed_login_count_24h"] += 2
        elif week == 3:
            credential = rows["user_id"].str.contains("credential_attack|old_takeover")
            rows.loc[credential, "failed_login_count_24h"] += 4
            rows.loc[credential, "login_country_changes_24h"] += 1
            rows.loc[credential, "recipient_block_rate_24h"] += 0.05

            campaign = rows["user_id"].str.contains("support_burst|marketing_launch")
            rows.loc[campaign, "account_age_minutes"] = 180
            rows.loc[campaign, "contacts_24h"] += 35
            rows.loc[campaign, "messages_1h"] += 25
            rows.loc[campaign, "profile_updates_24h"] = 6
            rows.loc[campaign, "device_count_24h"] = 5
            rows.loc[campaign, "recipient_block_rate_24h"] = 0.30
            rows.loc[campaign, "message_link_ratio_1h"] = 0.50
            rows.loc[campaign, "plan"] = "free"

        expanded.append(rows)

    output = pd.concat(expanded, ignore_index=True)
    output.to_csv(output_path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a multi-week synthetic feature row fixture."
    )
    parser.add_argument(
        "--input",
        default="fixtures/feature_rows_sample.csv",
        help="Base one-point fixture.",
    )
    parser.add_argument(
        "--output",
        default="fixtures/feature_rows_timeseries.csv",
        help="Output fixture path.",
    )
    parser.add_argument("--weeks", type=int, default=4)
    args = parser.parse_args()

    build_timeseries_fixture(args.input, args.output, weeks=args.weeks)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
