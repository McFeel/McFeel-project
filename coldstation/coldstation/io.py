"""Reading the raw 5-minute history files.

File layout (both the real xlsx exports and the tiny synthetic CSV samples
kept in this repo for unit tests):

* xlsx: data lives in sheet ``历史数据`` (the ``系统参数`` sheet only
  contains a screenshot and is ignored).
* Row 1: English point names (used as column names).
* Row 2: Chinese descriptions (skipped).
* Row 3+: data. ``timeStamp`` is text ``YYYY-MM-DD HH:MM:SS`` at 5-minute
  resolution.

Real xlsx files are read from the folder given by the COLD_STATION_DATA_DIR
environment variable; they must never be committed to the repository.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from .stations import HISTORY_SHEET, TIMESTAMP_COL, StationConfig

DATA_DIR_ENV = "COLD_STATION_DATA_DIR"
# Documented default location on the analyst's Mac; overridden by the env var.
DEFAULT_DATA_DIR = "/Users/wangtianzhi/Documents/AI冷站比赛"


def data_dir() -> Path:
    return Path(os.environ.get(DATA_DIR_ENV, DEFAULT_DATA_DIR))


def resolve_history_path(config: StationConfig, path: str | Path | None = None) -> Path:
    """Locate the raw history file for a station (explicit path wins)."""
    if path is not None:
        return Path(path)
    return data_dir() / config.default_filename


def _finalize(df: pd.DataFrame) -> pd.DataFrame:
    if TIMESTAMP_COL not in df.columns:
        raise ValueError(
            f"Column '{TIMESTAMP_COL}' not found; got columns {list(df.columns)[:5]}..."
        )
    df = df.copy()
    df[TIMESTAMP_COL] = pd.to_datetime(df[TIMESTAMP_COL], format="%Y-%m-%d %H:%M:%S")
    for col in df.columns:
        if col != TIMESTAMP_COL:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.sort_values(TIMESTAMP_COL).reset_index(drop=True)


def read_history_xlsx(path: str | Path) -> pd.DataFrame:
    """Read one real xlsx export (sheet 历史数据, Chinese header row skipped)."""
    df = pd.read_excel(path, sheet_name=HISTORY_SHEET, header=0, skiprows=[1])
    return _finalize(df)


def read_history_csv(path: str | Path) -> pd.DataFrame:
    """Read a CSV with the same two-header-row layout (used for repo samples)."""
    df = pd.read_csv(path, header=0, skiprows=[1])
    return _finalize(df)


def read_history(config: StationConfig, path: str | Path | None = None) -> pd.DataFrame:
    """Read the raw history for a station, validating the expected schema."""
    resolved = resolve_history_path(config, path)
    if not resolved.exists():
        raise FileNotFoundError(
            f"History file for station {config.station_id} not found: {resolved}\n"
            f"Set the {DATA_DIR_ENV} environment variable to the folder holding "
            "the xlsx exports, or pass an explicit path."
        )
    if resolved.suffix.lower() in {".xlsx", ".xlsm"}:
        df = read_history_xlsx(resolved)
    else:
        df = read_history_csv(resolved)
    missing = [c for c in config.columns if c not in df.columns]
    if missing:
        raise ValueError(
            f"Station {config.station_id}: file {resolved.name} is missing expected "
            f"columns {missing[:8]}{'...' if len(missing) > 8 else ''}"
        )
    return df
