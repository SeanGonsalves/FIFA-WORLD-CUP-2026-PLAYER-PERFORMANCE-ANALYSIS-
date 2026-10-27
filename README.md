# FIFA World Cup 2026 Player Performance

### A Python exploratory data analysis project

Explore player and match performance through clean, reproducible analysis in
Python. This project takes the supplied player-performance CSV from raw-data
inspection to a cleaned copy, statistical summaries, ranked tables, and
presentation-ready visualizations.

> **Scope:** This is a data analysis and visualization project—not a dashboard,
> prediction model, or player evaluation system. The supplied data is analyzed
> as-is and has not been independently verified against official tournament
> records.

## Project snapshot

| | |
|---|---|
| **Dataset** | 54,600 player-match records and 75 columns |
| **Coverage in the file** | 1,248 player IDs across 48 teams |
| **Analysis** | Data quality, descriptive statistics, group comparisons, rankings, correlations, and outlier review |
| **Deliverables** | Jupyter notebook, cleaned CSV, 9 PNG charts, and 11 analysis tables |
| **Tools** | Python, pandas, NumPy, Matplotlib, Seaborn, Jupyter |

The supplied file has no missing cells or exact duplicate rows. Cleaning still
checks for these conditions so the notebook remains useful if the input CSV is
updated.

## What this project explores

The notebook is designed to be approachable for students and Python beginners,
while documenting each step so readers can follow and reproduce the analysis.

### 1. Inspect and understand the data

- Read the original CSV and report its dimensions, column names, data types,
  sample records, missing values, and duplicate rows.
- Review the dataset's categories and numerical fields before selecting
  comparisons.
- Treat a row as a **player-match record**. A player can appear in more than one
  row, so record counts are not the same as unique player counts.

### 2. Clean conservatively

- Trim surrounding whitespace in text fields and represent blank text as
  missing.
- Parse `match_date` and report invalid date values.
- Remove exact duplicate rows only; do not remove records simply because they
  look unusual.
- Save the cleaned data to a separate file, preserving the original CSV.

### 3. Summarize performance

- Calculate numerical descriptive statistics including mean, standard
  deviation, quartiles, minimum, and maximum.
- Count records across useful categories such as position, team, tournament
  stage, and match result.
- Compare average ratings and contribution metrics across positions and teams.
- Aggregate match statistics by player ID to create player rankings for goals,
  assists, shots, minutes, and average ratings.
- Calculate correlations between numerical metrics. Correlation is descriptive
  and does not demonstrate cause and effect.

### 4. Visualize patterns

The notebook creates high-resolution PNG figures, including:

- Position and team count plots.
- A player-rating histogram with a KDE curve.
- Rating box plots and performance-score violin plots by position.
- A shots-versus-goals scatter plot.
- A correlation heatmap of selected numerical metrics.
- A grouped position comparison for ratings and contribution scores.
- A top-scorers ranking chart.
- A daily goals line chart when valid date data is available.

### 5. Flag unusual values without removing them

Basic checks look for metric inconsistencies such as shots on target exceeding
shots, successful passes exceeding total passes, percentages outside their
expected range, or negative numeric values. The IQR rule also identifies
potential statistical outliers. These are **flags for review**, not proof of
errors: plausible extreme values stay in the cleaned dataset.

## Project structure

```text
.
├── data/
│   ├── raw/
│   │   └── fifa_world_cup_2026_player_performance.csv  # Original source dataset
│   └── cleaned/
│       └── cleaned_player_performance.csv       # Generated cleaned copy
├── notebooks/
│   └── fifa_player_eda.ipynb                   # Complete, runnable analysis
├── outputs/
│   ├── plots/                                  # Generated 300-dpi PNG figures
│   └── tables/                                 # Generated analysis CSVs
├── src/
│   ├── analysis.py                             # Summary tables and plotting helpers
│   └── data_cleaning.py                        # Cleaning and quality-check helpers
├── requirements.txt
├── .gitignore
└── README.md
```

### Generated tables

The notebook reads the original CSV from `data/raw/` and writes the cleaned
dataset to `data/cleaned/cleaned_player_performance.csv`. It writes these
analysis CSV files to `outputs/tables/`:

| File | Contents |
|---|---|
| `cleaning_report.csv` | Input and output row counts; duplicate and invalid-date handling |
| `column_info.csv` | Data type, missing count, and unique values for each column |
| `missing_summary.csv` | Missing-value counts and percentages |
| `numeric_summary.csv` | Descriptive statistics for numeric columns |
| `category_frequencies.csv` | Counts and percentages for selected categorical columns |
| `quality_checks.csv` | Counts of rows flagged by consistency and range checks |
| `outlier_summary.csv` | IQR bounds and potential-outlier counts for selected metrics |
| `team_summary.csv` | Player-match counts, unique players, totals, and mean performance measures by team |
| `position_summary.csv` | Record counts, totals, and average performance measures by position |
| `player_rankings.csv` | Player-level aggregates of match statistics and average ratings |
| `correlations.csv` | Correlation matrix for numeric columns |

### Generated figures

The notebook writes these 300-dpi PNG files to `outputs/plots/`:

`category_counts.png` · `player_rating_distribution.png` ·
`player_rating_by_position_boxplot.png` · `performance_by_position_violin.png` ·
`shots_vs_goals.png` · `correlation_heatmap.png` ·
`position_grouped_comparison.png` · `top_scorers.png` ·
`daily_player_goals.png` (when valid dates are available).

## Get started

### Requirements

- Python 3.10 or later recommended.
- `pip` for installing dependencies.
- VS Code with the Python and Jupyter extensions to work interactively with the
  notebook (optional if using the command line).

### Windows PowerShell

From the project directory:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell prevents environment activation, either enable it for this
terminal with:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Or run the virtual environment's Python directly:
`.\.venv\Scripts\python.exe`.

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run the analysis

### In VS Code

1. Open the project folder in VS Code.
2. Open `notebooks/fifa_player_eda.ipynb`.
3. Select the `.venv` Python environment as the notebook kernel.
4. Choose **Run All**.

The notebook creates `data/cleaned/`, `outputs/plots/`, and `outputs/tables/`
as needed. Keep the original file at
`data/raw/fifa_world_cup_2026_player_performance.csv`; running the notebook
refreshes the cleaned copy, tables, and figures without changing the original.

### From PowerShell

Execute the notebook from the project root and save the executed copy:

```powershell
jupyter nbconvert --to notebook --execute .\notebooks\fifa_player_eda.ipynb --output fifa_player_eda_executed.ipynb
```

On macOS/Linux, use:

```bash
jupyter nbconvert --to notebook --execute notebooks/fifa_player_eda.ipynb --output fifa_player_eda_executed.ipynb
```

## Important interpretation notes

- Team summaries describe the player-match rows associated with each team;
  they are **not team score or standings tables**.
- Player rankings aggregate recorded match statistics by player ID. A sum of
  match goals is not assumed to be an independently verified official
  tournament total.
- The source CSV includes tournament-total fields as well as match-level
  statistics; these are kept distinct in the summaries.
- Correlations and group averages describe associations in this file. They do
  not establish causation or prove that one metric predicts another.
- Outlier checks do not automatically discard observations.

## Reproducibility

All reported summaries and charts are calculated from the supplied CSV when the
notebook runs. The notebook and source code contain the analysis logic; outputs
can be regenerated locally using the setup steps above. Generated output files
are excluded by `.gitignore` and can be created again by running the notebook.

---

Made as a clear, reproducible showcase of exploratory data analysis with Python.
