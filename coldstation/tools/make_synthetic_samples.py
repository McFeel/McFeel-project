"""Regenerate the tiny synthetic sample CSVs committed under tests/data/.

These samples exist ONLY so unit tests can exercise the reader / cleaner /
aggregator against each station's exact column layout (two header rows:
English point names then Chinese labels). All values are synthetic; no real
plant data is involved. Run from the coldstation/ folder:

    python tools/make_synthetic_samples.py
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from coldstation.stations import STATIONS, TIMESTAMP_COL  # noqa: E402

OUT_DIR = Path(__file__).resolve().parents[1] / "tests" / "data"
N_ROWS = 48  # 4 hours of 5-minute data
START = np.datetime64("2025-06-01T00:00:00")

_CN_LABELS = [
    ("timeStamp", "时间戳"),
    ("ChAMPS", "冷机电流百分比"),
    ("ChChWTempSupplySet", "冷冻水供水温度设定"),
    ("ChLeaveEvapTemp", "蒸发器出水温度"),
    ("ChEnterEvapTemp", "蒸发器进水温度"),
    ("ChEvapTemp", "蒸发温度"),
    ("ChLeaveCondTemp", "冷凝器出水温度"),
    ("ChEnterCondTemp", "冷凝器进水温度"),
    ("ChCondTemp", "冷凝温度"),
    ("ChRealtimeEfficiency", "冷机实时效率"),
    ("PriChWDiffPress", "冷冻水压差"),
    ("PriChWDP", "冷冻水压差"),
    ("PriChWPress", "冷冻水压力"),
    ("PriChWFlow", "冷冻水流量"),
    ("PriChWTempSupply", "冷冻总管供水温"),
    ("PriChWTempReturn", "冷冻总管回水温"),
    ("CWFlow", "冷却水流量"),
    ("CWTempSupply", "冷却总管供水温"),
    ("CWTempReturn", "冷却总管回水温"),
    ("CTOutletTemp", "冷却塔出水温度"),
    ("CTLeaveTemp", "冷却塔出水温度"),
    ("OutdoorWetTemp", "室外湿球温度"),
    ("OutdoorTdbin", "室外干球温度"),
    ("PriChWPVSDFreq", "冷冻泵频率"),
    ("CWPVSDFreq", "冷却泵频率"),
    ("CTVSDFreq", "冷却塔风机频率"),
    ("ChPowerTotal", "冷机电度"),
    ("PriChWPPowerTotal", "冷冻泵电度"),
    ("CWPPowerTotal", "冷却泵电度"),
    ("CTPowerTotal", "冷却塔电度"),
    ("ChPower", "冷机功率"),
    ("PriChWPPower", "冷冻泵功率"),
    ("CWPPower", "冷却泵功率"),
    ("CTPower", "冷却塔功率"),
    ("TotalRealTimeLoad", "系统实时冷负荷"),
    ("CoolingCapacityTotalDaily", "当日累计冷量"),
]


def chinese_label(column: str) -> str:
    for pattern, label in _CN_LABELS:
        if column.startswith(pattern):
            return label
    return "合成样例"


def synth_value(column: str, i: int, rng: np.random.Generator) -> float:
    hour_frac = (i % 288) / 288.0
    diurnal = np.sin(2 * np.pi * (hour_frac - 0.25))
    if "Freq" in column:
        return round(35 + 10 * diurnal + rng.normal(0, 1), 2)
    if "AMPS" in column:
        return round(60 + 20 * diurnal + rng.normal(0, 2), 2)
    if "PowerTotal" in column:
        return round(100000 + 10 * i + rng.normal(0, 1), 1)
    if "Power" in column:
        return round(120 + 40 * diurnal + rng.normal(0, 4), 2)
    if "SupplySet" in column:
        return 7.0
    if "OutdoorTdbin" in column:
        return round(30 + 5 * diurnal + rng.normal(0, 0.3), 2)
    if "OutdoorWetTemp" in column:
        return round(25 + 3 * diurnal + rng.normal(0, 0.3), 2)
    if "Temp" in column:
        return round(12 + 3 * diurnal + rng.normal(0, 0.5), 2)
    if "Flow" in column:
        return round(300 + 50 * diurnal + rng.normal(0, 5), 1)
    if "Press" in column or "DP" in column:
        return round(1.5 + 0.2 * diurnal + rng.normal(0, 0.05), 3)
    if column == "TotalRealTimeLoad":
        return round(1500 + 500 * diurnal + rng.normal(0, 30), 1)
    if column == "CoolingCapacityTotalDaily":
        return round(50 * (i % 288), 1)
    return round(rng.normal(0, 1), 3)


def make_sample(station_id: str) -> Path:
    config = STATIONS[station_id]
    rng = np.random.default_rng(hash(station_id) % 2**32)
    columns = config.columns
    rows: list[list] = []
    for i in range(N_ROWS):
        ts = START + np.timedelta64(5 * i, "m")
        row: list = [str(ts).replace("T", " ")]
        for col in columns[1:]:
            row.append(synth_value(col, i, rng))
        rows.append(row)

    # Station A quirks: -8888.7998 placeholders in CWTempReturn and the
    # three cooling-tower outlet temperatures, plus a few blank cells.
    if station_id == "A":
        sentinel_cols = ["CWTempReturn", "CTOutletTemp01", "CTOutletTemp02", "CTOutletTemp03"]
        for col in sentinel_cols:
            idx = columns.index(col)
            for r in range(0, N_ROWS, 3):
                rows[r][idx] = -8888.7998
    # Every station: a couple of blank cells and one non-physical value.
    load_idx = columns.index("TotalRealTimeLoad")
    rows[5][load_idx] = ""
    rows[7][load_idx] = -50.0  # negative load -> cleaned to NaN
    freq_idx = columns.index("PriChWPVSDFreq01")
    rows[9][freq_idx] = 99.0  # above 60 Hz -> cleaned to NaN

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"station_{station_id.lower()}_sample.csv"
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(columns)
        writer.writerow([chinese_label(c) if c != TIMESTAMP_COL else "时间戳" for c in columns])
        writer.writerows(rows)
    return out_path


if __name__ == "__main__":
    for sid in STATIONS:
        path = make_sample(sid)
        print(f"wrote {path}")
