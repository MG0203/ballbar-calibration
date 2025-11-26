from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
ANALYSIS_DIR = DATA_DIR / "analysis"

ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)


def load_measurements() -> pd.DataFrame:
    path = ANALYSIS_DIR / "all_measurements.csv"
    return pd.read_csv(path)


def suggest_feedrate_adjustments(df: pd.DataFrame, max_allowed_dev: float = 0.02) -> pd.DataFrame:
    summary = (
        df.groupby("machine_id")
        .agg(
            mean_dev_mm=("deviation_mm", "mean"),
        )
        .reset_index()
    )
    summary["action"] = summary["mean_dev_mm"].apply(
        lambda x: "reduce feedrate" if abs(x) > max_allowed_dev else "ok"
    )
    return summary