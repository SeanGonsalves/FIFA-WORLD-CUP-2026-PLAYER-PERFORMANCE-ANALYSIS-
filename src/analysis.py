"""Reusable summaries and figures for the FIFA player-performance notebook."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from data_cleaning import value_quality_checks


PLOT_STYLE = "seaborn-v0_8-whitegrid"
PALETTE = "viridis"


def build_tables(data: pd.DataFrame, tables_dir: Path) -> dict[str, pd.DataFrame]:
    """Create and save descriptive, group-wise, ranking, and quality tables."""
    tables_dir.mkdir(parents=True, exist_ok=True)

    column_info = pd.DataFrame(
        {
            "column": data.columns,
            "dtype": data.dtypes.astype(str).values,
            "missing_values": data.isna().sum().values,
            "unique_values": data.nunique(dropna=False).values,
        }
    )
    missing = data.isna().sum().rename("missing_values").to_frame()
    missing["missing_percent"] = missing["missing_values"].div(len(data)).mul(100)

    numeric = data.select_dtypes(include=np.number)
    numeric_summary = numeric.describe().T.rename_axis("metric").reset_index()
    category_columns = [
        column
        for column in (
            "team",
            "position",
            "nationality",
            "preferred_foot",
            "tournament_stage",
            "match_result",
        )
        if column in data.columns
    ]
    category_frequencies = pd.concat(
        [
            data[column]
            .value_counts(dropna=False)
            .rename_axis("category_value")
            .reset_index(name="count")
            .assign(
                category=column,
                percent=lambda frame: frame["count"].div(len(data)).mul(100),
            )
            for column in category_columns
        ],
        ignore_index=True,
    )

    quality_checks = value_quality_checks(data)
    metric_names = [
        name
        for name in (
            "goals",
            "assists",
            "shots",
            "minutes_played",
            "player_rating",
            "performance_score",
        )
        if name in data.columns
    ]
    outlier_rows = []
    for metric in metric_names:
        values = data[metric].dropna()
        if values.empty:
            continue
        q1, q3 = values.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        count = int(((values < lower) | (values > upper)).sum())
        outlier_rows.append(
            {
                "metric": metric,
                "q1": q1,
                "q3": q3,
                "iqr": iqr,
                "lower_bound": lower,
                "upper_bound": upper,
                "rows_flagged": count,
                "percent_flagged": count / len(values) * 100,
                "note": "Potential outliers only; no rows were removed.",
            }
        )
    outlier_summary = pd.DataFrame(outlier_rows)

    team_summary = (
        data.groupby("team", dropna=False)
        .agg(
            player_match_records=("player_id", "size"),
            unique_players=("player_id", "nunique"),
            player_goals=("goals", "sum"),
            player_assists=("assists", "sum"),
            mean_minutes_per_record=("minutes_played", "mean"),
            mean_player_rating=("player_rating", "mean"),
            mean_performance_score=("performance_score", "mean"),
        )
        .sort_values("mean_performance_score", ascending=False)
        .reset_index()
    )
    position_summary = (
        data.groupby("position", dropna=False)
        .agg(
            player_match_records=("player_id", "size"),
            unique_players=("player_id", "nunique"),
            total_player_goals=("goals", "sum"),
            mean_goals_per_record=("goals", "mean"),
            mean_assists_per_record=("assists", "mean"),
            mean_minutes_per_record=("minutes_played", "mean"),
            mean_player_rating=("player_rating", "mean"),
            mean_offensive_contribution=("offensive_contribution", "mean"),
            mean_defensive_contribution=("defensive_contribution", "mean"),
        )
        .sort_values("mean_player_rating", ascending=False)
        .reset_index()
    )
    player_summary = (
        data.groupby(["player_id", "player_name", "team"], dropna=False)
        .agg(
            match_records=("match_id", "nunique"),
            goals=("goals", "sum"),
            assists=("assists", "sum"),
            shots=("shots", "sum"),
            minutes_played=("minutes_played", "sum"),
            mean_player_rating=("player_rating", "mean"),
            mean_performance_score=("performance_score", "mean"),
            tournament_rating_mean=("tournament_rating", "mean"),
        )
        .sort_values(["goals", "assists", "minutes_played"], ascending=False)
        .reset_index()
    )
    correlations = numeric.corr()

    tables = {
        "column_info": column_info,
        "missing_summary": missing,
        "numeric_summary": numeric_summary,
        "category_frequencies": category_frequencies,
        "quality_checks": quality_checks,
        "outlier_summary": outlier_summary,
        "team_summary": team_summary,
        "position_summary": position_summary,
        "player_rankings": player_summary,
        "correlations": correlations,
    }
    for name, table in tables.items():
        table.to_csv(tables_dir / f"{name}.csv", index=name == "correlations")
    return tables


def save_figures(data: pd.DataFrame, player_summary: pd.DataFrame, plots_dir: Path) -> list[Path]:
    """Create presentation-ready PNG charts using columns present in the CSV."""
    plots_dir.mkdir(parents=True, exist_ok=True)
    plt.style.use(PLOT_STYLE)
    sns.set_palette(PALETTE)
    saved: list[Path] = []

    def finish(fig: plt.Figure, filename: str) -> None:
        fig.tight_layout()
        path = plots_dir / filename
        fig.savefig(path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        saved.append(path)

    # Player-match record counts, not unique player totals.
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    sns.countplot(data=data, y="position", order=data["position"].value_counts().index, ax=axes[0])
    axes[0].set(title="Player-match records by position", xlabel="Records", ylabel="Position")
    team_order = data["team"].value_counts().head(15).index
    sns.countplot(data=data[data["team"].isin(team_order)], y="team", order=team_order, ax=axes[1])
    axes[1].set(title="15 teams with most player-match records", xlabel="Records", ylabel="Team")
    finish(fig, "category_counts.png")

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.histplot(data=data, x="player_rating", kde=True, bins=25, ax=ax)
    ax.set(title="Distribution of per-match player ratings", xlabel="Player rating", ylabel="Player-match records")
    finish(fig, "player_rating_distribution.png")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=data, x="position", y="player_rating", order=data["position"].value_counts().index, ax=ax)
    ax.set(title="Player rating by position", xlabel="Position", ylabel="Per-match player rating")
    finish(fig, "player_rating_by_position_boxplot.png")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.violinplot(
        data=data,
        x="position",
        y="performance_score",
        order=data["position"].value_counts().index,
        inner="quartile",
        cut=0,
        ax=ax,
    )
    ax.set(title="Performance-score distribution by position", xlabel="Position", ylabel="Performance score")
    finish(fig, "performance_by_position_violin.png")

    fig, ax = plt.subplots(figsize=(9, 6))
    sns.scatterplot(data=data, x="shots", y="goals", hue="position", alpha=0.35, s=22, ax=ax)
    ax.set(title="Shots and goals in player-match records", xlabel="Shots", ylabel="Goals")
    finish(fig, "shots_vs_goals.png")

    selected_metrics = [
        name
        for name in (
            "goals",
            "assists",
            "shots",
            "shots_on_target",
            "expected_goals_xg",
            "minutes_played",
            "successful_passes",
            "tackles",
            "distance_covered_km",
            "player_rating",
            "performance_score",
            "tournament_rating",
        )
        if name in data.select_dtypes(include=np.number).columns
    ]
    fig, ax = plt.subplots(figsize=(12, 9))
    sns.heatmap(
        data[selected_metrics].corr(),
        cmap="vlag",
        center=0,
        annot=True,
        fmt=".2f",
        square=True,
        ax=ax,
    )
    ax.set_title("Correlation between selected numerical metrics")
    finish(fig, "correlation_heatmap.png")

    position_means = (
        data.groupby("position")[
            ["player_rating", "offensive_contribution", "defensive_contribution"]
        ]
        .mean()
        .reset_index()
        .melt(id_vars="position", var_name="metric", value_name="mean")
    )
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=position_means, x="position", y="mean", hue="metric", ax=ax)
    ax.set(title="Average rating and contribution scores by position", xlabel="Position", ylabel="Per-match mean")
    ax.legend(title="Metric", bbox_to_anchor=(1.02, 1), loc="upper left")
    finish(fig, "position_grouped_comparison.png")

    top_scorers = player_summary.nlargest(10, "goals").copy()
    top_scorers["player_label"] = top_scorers["player_name"] + " (" + top_scorers["team"] + ")"
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=top_scorers, x="goals", y="player_label", color=sns.color_palette(PALETTE, 1)[0], ax=ax)
    ax.set(title="Top 10 players by summed match goals", xlabel="Goals across player-match records", ylabel="Player (team)")
    finish(fig, "top_scorers.png")

    if "match_date" in data.columns and data["match_date"].notna().any():
        daily_goals = data.groupby("match_date")["goals"].sum().sort_index()
        fig, ax = plt.subplots(figsize=(12, 5))
        daily_goals.plot(ax=ax, marker="o", linewidth=1.5)
        ax.set(title="Player goals recorded per match date", xlabel="Match date", ylabel="Sum of player goals")
        finish(fig, "daily_player_goals.png")

    return saved


def describe_findings(
    data: pd.DataFrame,
    position_summary: pd.DataFrame,
    player_summary: pd.DataFrame,
    outlier_summary: pd.DataFrame,
) -> list[str]:
    """Produce short, data-driven observations for the notebook."""
    messages = [
        f"The dataset contains {len(data):,} player-match records, "
        f"{data['player_id'].nunique():,} distinct player IDs, and {data['team'].nunique():,} teams."
    ]
    if not player_summary.empty:
        top_scorer = player_summary.iloc[0]
        messages.append(
            f"The player with the most summed match goals is {top_scorer['player_name']} "
            f"({top_scorer['team']}) with {int(top_scorer['goals'])}."
        )
    if not position_summary.empty:
        top_position = position_summary.loc[position_summary["mean_player_rating"].idxmax()]
        messages.append(
            f"{top_position['position']} has the highest mean per-match player rating "
            f"({top_position['mean_player_rating']:.2f}) among the listed positions."
        )
    if not outlier_summary.empty:
        largest = outlier_summary.loc[outlier_summary["rows_flagged"].idxmax()]
        messages.append(
            f"The IQR rule flags {int(largest['rows_flagged']):,} records for "
            f"{largest['metric']}; these are potential outliers, not confirmed errors."
        )
    messages.append(
        "These are descriptive comparisons of the supplied records. Correlation and group averages "
        "do not establish causes, and team summaries are based on player-match records rather than match scores."
    )
    return messages
