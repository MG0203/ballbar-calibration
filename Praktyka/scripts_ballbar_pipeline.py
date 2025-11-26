from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

import json
import pandas as pd
import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
META_DIR = DATA_DIR / "meta"
ANALYSIS_DIR = DATA_DIR / "analysis"
REPORTS_DIR = DATA_DIR / "reports"
PLOTS_DIR = DATA_DIR / "plots"

for d in [RAW_DIR, PROCESSED_DIR, META_DIR, ANALYSIS_DIR, REPORTS_DIR, PLOTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def create_template():
    template_path = PROCESSED_DIR / "ballbar_template.xlsx"
    columns = [
        "timestamp",
        "machine_id",
        "operator",
        "test_id",
        "axis",
        "angle_deg",
        "radius_nominal_mm",
        "radius_measured_mm",
        "deviation_mm",
    ]
    df_template = pd.DataFrame(columns=columns)
    df_template.to_excel(template_path, index=False)
    return template_path


def read_ballbar_device_sample():
    sample_data = [
        {"axis": "XY", "angle_deg": 0, "radius_nominal_mm": 150.0, "radius_measured_mm": 149.98},
        {"axis": "XY", "angle_deg": 90, "radius_nominal_mm": 150.0, "radius_measured_mm": 150.02},
        {"axis": "XY", "angle_deg": 180, "radius_nominal_mm": 150.0, "radius_measured_mm": 149.97},
    ]
    return sample_data


def collect_and_save_data(machine_id: str, operator: str, test_id: str | None = None) -> Path:
    if test_id is None:
        test_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    rows = []
    now = datetime.now().isoformat()
    for row in read_ballbar_device_sample():
        deviation = row["radius_measured_mm"] - row["radius_nominal_mm"]
        rows.append(
            {
                "timestamp": now,
                "machine_id": machine_id,
                "operator": operator,
                "test_id": test_id,
                "axis": row["axis"],
                "angle_deg": row["angle_deg"],
                "radius_nominal_mm": row["radius_nominal_mm"],
                "radius_measured_mm": row["radius_measured_mm"],
                "deviation_mm": deviation,
            }
        )
    out_path = RAW_DIR / f"{machine_id}_{test_id}.csv"
    pd.DataFrame(rows).to_csv(out_path, index=False)
    return out_path


META_FILE = META_DIR / "tests_metadata.json"


def load_metadata() -> list[dict]:
    if META_FILE.exists():
        with open(META_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_metadata(metadata: list[dict]):
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def register_test(csv_path: Path, machine_id: str, operator: str, description: str, test_type: str = "circular") -> dict:
    metadata = load_metadata()
    test_id = csv_path.stem
    entry = {
        "test_id": test_id,
        "file": str(csv_path),
        "machine_id": machine_id,
        "operator": operator,
        "description": description,
        "test_type": test_type,
        "created_at": datetime.now().isoformat(),
    }
    metadata.append(entry)
    save_metadata(metadata)
    return entry


def plot_control_chart(csv_path: Path) -> Path:
    df = pd.read_csv(csv_path)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df["angle_deg"], df["deviation_mm"], marker="o")
    ax.axhline(0, color="black", linestyle="--", linewidth=1)
    ax.set_xlabel("Kąt [deg]")
    ax.set_ylabel("Odchyłka promienia [mm]")
    ax.set_title(f"Ballbar – wykres kontrolny\n{csv_path.name}")
    ax.grid(True)
    out_path = PLOTS_DIR / f"{csv_path.stem}_control_chart.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def load_all_measurements() -> pd.DataFrame:
    frames = []
    for csv_path in RAW_DIR.glob("*.csv"):
        df = pd.read_csv(csv_path)
        df["source_file"] = csv_path.name
        frames.append(df)
    if not frames:
        raise RuntimeError("Brak plików CSV w katalogu data/raw/")
    return pd.concat(frames, ignore_index=True)


def compute_basic_stats(df: pd.DataFrame) -> pd.DataFrame:
    stats = (
        df.groupby(["machine_id", "axis"])
        .agg(
            deviation_mean_mm=("deviation_mm", "mean"),
            deviation_std_mm=("deviation_mm", "std"),
            deviation_max_mm=("deviation_mm", "max"),
            deviation_min_mm=("deviation_mm", "min"),
            n_points=("deviation_mm", "count"),
        )
        .reset_index()
    )
    return stats


def export_results(df_all: pd.DataFrame, df_stats: pd.DataFrame):
    csv_all = ANALYSIS_DIR / "all_measurements.csv"
    xlsx_all = ANALYSIS_DIR / "all_measurements.xlsx"
    csv_stats = ANALYSIS_DIR / "deviation_stats.csv"
    xlsx_stats = ANALYSIS_DIR / "deviation_stats.xlsx"
    df_all.to_csv(csv_all, index=False)
    df_all.to_excel(xlsx_all, index=False)
    df_stats.to_csv(csv_stats, index=False)
    df_stats.to_excel(xlsx_stats, index=False)


def plot_stats_summary(df_stats: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(8, 5))
    for machine_id, group in df_stats.groupby("machine_id"):
        ax.bar(
            group["axis"] + "_" + machine_id,
            group["deviation_mean_mm"],
            label=machine_id,
        )
    ax.set_ylabel("Średnia odchyłka promienia [mm]")
    ax.set_title("Średnie odchyłki ballbar – porównanie maszyn/osi")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()
    out_path = PLOTS_DIR / "deviation_summary.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


@dataclass
class ErrorThresholds:
    small_dev: float = 0.01
    medium_dev: float = 0.03


def classify_deviation(dev: float, thresholds: ErrorThresholds) -> str:
    if abs(dev) <= thresholds.small_dev:
        return "OK"
    elif abs(dev) <= thresholds.medium_dev:
        return "MEDIUM"
    else:
        return "HIGH"


def apply_error_classification(df: pd.DataFrame, thresholds: ErrorThresholds) -> pd.DataFrame:
    df = df.copy()
    df["error_class"] = df["deviation_mm"].apply(
        lambda x: classify_deviation(x, thresholds)
    )
    return df


def aggregate_errors(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby(["machine_id", "axis", "error_class"])
        .size()
        .reset_index(name="count")
    )
    return summary


def plot_error_distribution(df_summary: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(8, 5))
    pivot = df_summary.pivot_table(
        index="machine_id",
        columns="error_class",
        values="count",
        fill_value=0,
    )
    pivot.plot(kind="bar", stacked=True, ax=ax)
    ax.set_ylabel("Liczba punktów pomiarowych")
    ax.set_title("Rozkład klas błędów ballbar wg maszyn")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    out_path = PLOTS_DIR / "error_classes_by_machine.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def export_html_report(df: pd.DataFrame, df_summary: pd.DataFrame, plot_path: Path):
    report_path = REPORTS_DIR / "ballbar_error_report.html"
    html = """
    <html>
    <head><meta charset="utf-8"><title>Raport błędów ballbar</title></head>
    <body>
      <h1>Raport błędów ballbar</h1>
      <h2>Podsumowanie statystyczne</h2>
      {summary_table}
      <h2>Przykładowe dane pomiarowe (pierwszych 50 wierszy)</h2>
      {sample_table}
      <h2>Rozkład klas błędów</h2>
      <img src="{plot_rel}" alt="Rozkład błędów" style="max-width: 800px;">
    </body>
    </html>
    """
    summary_table_html = df_summary.to_html(index=False)
    sample_table_html = df.head(50).to_html(index=False)
    html_final = html.format(
        summary_table=summary_table_html,
        sample_table=sample_table_html,
        plot_rel=plot_path.name,
    )
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_final)


def main():
    create_template()
    csv_path = collect_and_save_data(machine_id="CNC_01", operator="Operator")
    register_test(
        csv_path=csv_path,
        machine_id="CNC_01",
        operator="Operator",
        description="Test wstępny ruchu kołowego",
    )
    plot_control_chart(csv_path)
    df_all = load_all_measurements()
    df_stats = compute_basic_stats(df_all)
    export_results(df_all, df_stats)
    plot_stats_summary(df_stats)
    thresholds = ErrorThresholds()
    df_cls = apply_error_classification(df_all, thresholds)
    df_summary = aggregate_errors(df_cls)
    out_csv = ANALYSIS_DIR / "all_measurements_with_classes.csv"
    df_cls.to_csv(out_csv, index=False)
    plot_path = plot_error_distribution(df_summary)
    export_html_report(df_cls, df_summary, plot_path)


if __name__ == "__main__":
    main()