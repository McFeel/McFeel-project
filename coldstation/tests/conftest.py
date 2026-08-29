from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from coldstation.stations import (
    DRYBULB_COL,
    LOAD_COL,
    TIMESTAMP_COL,
    WETBULB_COL,
    get_station,
)

DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture
def sample_paths() -> dict[str, Path]:
    return {sid: DATA_DIR / f"station_{sid.lower()}_sample.csv" for sid in "ABC"}


def make_synthetic_hourly(n_days: int = 150, seed: int = 3) -> pd.DataFrame:
    """Synthetic hourly frame with learnable structure, matching the columns
    the pipeline needs for station C (2 chillers). Includes hot afternoons
    (dry bulb >= 35C) so extreme-condition subsets are non-empty."""
    rng = np.random.default_rng(seed)
    index = pd.date_range("2026-03-01", periods=n_days * 24, freq="h", name=TIMESTAMP_COL)
    hour = index.hour.to_numpy()
    day = np.arange(len(index)) / 24.0

    diurnal = np.sin(2 * np.pi * (hour - 14) / 24)
    seasonal = 6 * np.sin(2 * np.pi * day / 365 - 1.0)
    drybulb = 29 + 8 * diurnal + seasonal + rng.normal(0, 1.0, len(index))
    wetbulb = drybulb - 4 - rng.normal(1.0, 0.5, len(index))

    weekly = np.where(index.dayofweek >= 5, -150.0, 0.0)
    load = (
        900
        + 60 * (drybulb - 25)
        + 250 * diurnal
        + weekly
        + rng.normal(0, 25, len(index))
    ).clip(min=100)

    df = pd.DataFrame(index=index)
    df[DRYBULB_COL] = drybulb
    df[WETBULB_COL] = wetbulb
    df[LOAD_COL] = load
    df["ChAMPS01"] = (load / 20).clip(20, 95)
    df["ChAMPS02"] = np.where(load > 1200, (load / 25).clip(20, 95), 0.0)
    df["ChPower01"] = 0.18 * load + rng.normal(0, 4, len(index))
    df["PriChWPVSDFreq01"] = (28 + load / 80).clip(25, 50) + rng.normal(0, 0.4, len(index))
    return df


@pytest.fixture(scope="session")
def synthetic_hourly() -> pd.DataFrame:
    return make_synthetic_hourly()


@pytest.fixture
def station_c_config():
    return get_station("C").replace_equipment_targets(["ChPower01", "PriChWPVSDFreq01"])
