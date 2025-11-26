from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
ANALYSIS_DIR = DATA_DIR / "analysis"
PLOTS_DIR = DATA_DIR / "plots"

for d in [ANALYSIS_DIR, PLOTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def load_pre_post_data(pre_path: Path, post_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    pre = pd.read_csv(pre_path)
    post = pd.read_csv(post_path)
    return pre, post


def compare_pre_post(pre: pd.DataFrame, post: pd.DataFrame) -> pd.DataFrame:
    cols = ["machine_id", "axis", "angle_deg"]
    merged = pre.merge(
        post,
        on=cols,
        suffixes=("_pre", "_post"),
    )
    merged["delta_dev_mm"] = merged["deviation_mm_post"] - merged["deviation_mm_pre"]
    return merged


def plot_pre_post_summary(df: pd.DataFrame) -> Path:
    summary = (
        df.groupby("machine_id")
        .agg(
            mean_delta=("delta_dev_mm", "mean"),
        )
        .reset_index()
    )
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(summary["machine_id"], summary["mean_delta"])
    ax.axhline(0, color="black", linestyle="--")
    ax.set_ylabel("Zmiana średniej odchyłki [mm] (post - pre)")
    ax.set_title("Wpływ kalibracji na odchyłki ballbar")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    out_path = PLOTS_DIR / "post_calib_delta.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path