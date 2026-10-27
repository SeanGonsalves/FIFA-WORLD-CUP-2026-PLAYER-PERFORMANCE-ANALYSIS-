"""Small, transparent cleaning helpers for the FIFA player dataset."""

from pathlib import Path

import pandas as pd


def clean_dataset(input_path: Path, output_path: Path) -> tuple[pd.DataFrame, dict[str, int]]:
    """Normalize text/date fields, remove exact duplicate rows, and save a copy.

    No player records are removed for statistical outliers or suspicious values.
    """
    data = pd.read_csv(input_path, low_memory=False)
    original_rows = len(data)

    # Trim accidental whitespace, keeping missing values as missing.
    text_columns = data.select_dtypes(include=["object", "string"]).columns
    for column in text_columns:
        data[column] = data[column].str.strip().replace("", pd.NA)

    duplicate_rows = int(data.duplicated().sum())
    if duplicate_rows:
        data = data.drop_duplicates().copy()

    invalid_dates = 0
    if "match_date" in data.columns:
        parsed_dates = pd.to_datetime(data["match_date"], errors="coerce")
        invalid_dates = int(parsed_dates.isna().sum() - data["match_date"].isna().sum())
        data["match_date"] = parsed_dates

    output_path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_path, index=False, date_format="%Y-%m-%d")

    report = {
        "original_rows": original_rows,
        "cleaned_rows": len(data),
        "exact_duplicates_removed": duplicate_rows,
        "invalid_dates_created_as_missing": invalid_dates,
    }
    return data, report


def value_quality_checks(data: pd.DataFrame) -> pd.DataFrame:
    """Return counts for common metric consistency and range checks."""
    checks: dict[str, pd.Series] = {}

    numeric_columns = data.select_dtypes(include="number").columns
    if len(numeric_columns):
        checks["negative values in numeric columns"] = (
            data[numeric_columns].lt(0).any(axis=1)
        )

    bounded_pairs = [
        ("shots_on_target", "shots"),
        ("successful_passes", "total_passes"),
        ("successful_dribbles", "dribbles_attempted"),
        ("successful_crosses", "crosses"),
    ]
    for numerator, denominator in bounded_pairs:
        if numerator in data.columns and denominator in data.columns:
            checks[f"{numerator} greater than {denominator}"] = (
                data[numerator] > data[denominator]
            )

    for column in ("pass_accuracy", "save_percentage"):
        if column in data.columns:
            checks[f"{column} outside [0, 1]"] = (
                data[column].notna() & ~data[column].between(0, 1)
            )

    if "age" in data.columns:
        checks["age outside 15-60"] = data["age"].notna() & ~data["age"].between(15, 60)
    if "minutes_played" in data.columns:
        checks["minutes_played outside 0-120"] = (
            data["minutes_played"].notna() & ~data["minutes_played"].between(0, 120)
        )
    if "clean_sheet" in data.columns:
        checks["clean_sheet not binary"] = (
            data["clean_sheet"].notna() & ~data["clean_sheet"].isin([0, 1])
        )

    return pd.DataFrame(
        {
            "check": list(checks),
            "rows_flagged": [int(mask.fillna(False).sum()) for mask in checks.values()],
        }
    )
