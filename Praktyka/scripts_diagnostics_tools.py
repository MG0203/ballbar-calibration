from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
ANALYSIS_DIR = DATA_DIR / "analysis"

ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)


def load_measurements_with_classes() -> pd.DataFrame:
    path = ANALYSIS_DIR / "all_measurements_with_classes.csv"
    return pd.read_csv(path)


def filter_high_errors(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["error_class"] == "HIGH"]


def group_by_machine_axis(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby(["machine_id", "axis"])
        .agg(
            n_points=("deviation_mm", "count"),
            mean_dev_mm=("deviation_mm", "mean"),
        )
        .reset_index()
    )
    return summary