"""Cleaning the 5-minute raw data and aggregating it to hourly resolution.

Steps:
1. Replace sentinel placeholders (e.g. -8888.7998 in station A) with NaN.
2. Null out physically impossible values (per column-family bounds).
3. Deduplicate timestamps and reindex to a regular 5-minute grid so data
   gaps (e.g. station A ends 2025-10-20 23:55 despite the filename saying
   10-31) become explicit NaN runs instead of silently missing rows.
4. Aggregate to hourly means, requiring minimum intra-hour coverage.

Scoring is on 24h *hourly* values, so everything downstream works on the
hourly frame produced here.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .stations import SENTINEL_THRESHOLD, TIMESTAMP_COL

RAW_FREQ = "5min"
POINTS_PER_HOUR = 12

# Physical plausibility bounds by column-name pattern (checked in order;
# first match wins). Values outside the bounds become NaN.
_BOUNDS: list[tuple[str, float, float]] = [
    ("Freq", 0.0, 60.0),          # VSD frequency in Hz
    ("Temp", -40.0, 80.0),        # any water/air temperature in Celsius
    ("Tdbin", -40.0, 60.0),       # outdoor dry bulb
    ("AMPS", 0.0, 150.0),         # chiller amperage (percent RLA)
    ("PowerTotal", 0.0, np.inf),  # cumulative energy counters
    ("Power", 0.0, np.inf),
    ("Flow", 0.0, np.inf),
    ("Load", 0.0, np.inf),
    ("CoolingCapacity", 0.0, np.inf),
    ("Press", -5.0, 100.0),
    ("DP", -5.0, 100.0),
]


def _bounds_for(column: str) -> tuple[float, float] | None:
    for pattern, lo, hi in _BOUNDS:
        if pattern in column:
            return lo, hi
    return None


@dataclass
class CleaningReport:
    n_raw_rows: int = 0
    n_duplicate_timestamps: int = 0
    n_grid_rows: int = 0
    n_missing_grid_rows: int = 0
    sentinel_cells: int = 0
    out_of_bounds_cells: int = 0

    def as_dict(self) -> dict:
        return dict(self.__dict__)


def clean_raw(df: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
    """Sentinel/bounds cleaning + regular 5-minute grid. Returns (df, report)."""
    report = CleaningReport(n_raw_rows=len(df))
    df = df.copy()

    value_cols = [c for c in df.columns if c != TIMESTAMP_COL]
    values = df[value_cols]

    sentinel_mask = values <= SENTINEL_THRESHOLD
    report.sentinel_cells = int(sentinel_mask.sum().sum())
    df[value_cols] = values.mask(sentinel_mask)

    oob = 0
    for col in value_cols:
        bounds = _bounds_for(col)
        if bounds is None:
            continue
        lo, hi = bounds
        bad = (df[col] < lo) | (df[col] > hi)
        oob += int(bad.sum())
        df.loc[bad, col] = np.nan
    report.out_of_bounds_cells = oob

    dup = df.duplicated(subset=TIMESTAMP_COL, keep="last")
    report.n_duplicate_timestamps = int(dup.sum())
    df = df[~dup]

    df = df.set_index(TIMESTAMP_COL).sort_index()
    full_index = pd.date_range(df.index.min(), df.index.max(), freq=RAW_FREQ)
    report.n_missing_grid_rows = int(len(full_index) - len(df))
    df = df.reindex(full_index)
    df.index.name = TIMESTAMP_COL
    report.n_grid_rows = len(df)
    return df, report


def aggregate_hourly(df_5min: pd.DataFrame, min_points: int = 6) -> pd.DataFrame:
    """Hourly means; hours with fewer than ``min_points`` valid 5-min samples
    (out of 12) are left as NaN rather than trusting a thin average."""
    grouped = df_5min.resample("h")
    hourly = grouped.mean()
    counts = grouped.count()
    return hourly.mask(counts < min_points)


def prepare_hourly(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
    """Convenience: raw dataframe -> cleaned hourly dataframe."""
    cleaned, report = clean_raw(df_raw)
    return aggregate_hourly(cleaned), report
