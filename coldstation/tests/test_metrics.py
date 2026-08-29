import numpy as np
import pandas as pd

from coldstation.metrics import (
    EXTREME_FLAGS,
    default_off_threshold,
    extreme_flags,
    mape,
    mape_by_condition,
)
from coldstation.stations import DRYBULB_COL, LOAD_COL, WETBULB_COL


def _series(values):
    idx = pd.date_range("2026-06-01", periods=len(values), freq="h")
    return pd.Series(values, index=idx, dtype=float)


def test_mape_basic():
    actual = _series([100, 200, 400])
    pred = _series([110, 180, 400])
    result = mape(actual, pred)
    assert result.n_scored == 3
    expected = (0.10 + 0.10 + 0.0) / 3
    assert abs(result.mape - expected) < 1e-12


def test_mape_excludes_off_and_missing():
    actual = _series([0.0, np.nan, 100.0, 100.0])
    pred = _series([50.0, 50.0, 90.0, 110.0])
    result = mape(actual, pred, off_threshold=1.0)
    assert result.n_scored == 2
    assert result.n_excluded_off == 1
    assert result.n_missing == 1
    assert abs(result.mape - 0.10) < 1e-12


def test_mape_empty():
    result = mape(_series([np.nan]), _series([1.0]))
    assert result.mape is None and result.n_scored == 0


def test_default_off_threshold():
    load = _series([0, 0, 1000, 1000, 2000])
    assert default_off_threshold(load) == 0.05 * 1000


def test_extreme_flags_categories():
    idx = pd.date_range("2026-06-01", periods=5, freq="h")
    hourly = pd.DataFrame(
        {
            DRYBULB_COL: [36.0, 30.0, -12.0, 30.0, 30.0],
            WETBULB_COL: [25.0, 29.0, -15.0, 20.0, 20.0],
            LOAD_COL: [1000.0, 1000.0, 1000.0, 1300.0, 1310.0],
        },
        index=idx,
    )
    flags = extreme_flags(hourly)
    assert flags["extreme_heat"].tolist() == [True, False, False, False, False]
    assert flags["extreme_humidity"].tolist() == [False, True, False, False, False]
    assert flags["extreme_cold"].tolist() == [False, False, True, False, False]
    # Hour 3: 1000 -> 1300 is a 30% jump; hour 4: <20% change.
    assert flags["load_jump"].tolist() == [False, False, False, True, False]
    assert flags["any_extreme"].sum() == 4


def test_mape_by_condition_reports_all_subsets():
    idx = pd.date_range("2026-06-01", periods=6, freq="h")
    hourly = pd.DataFrame(
        {
            DRYBULB_COL: [36.0, 36.0, 30.0, 30.0, 30.0, 30.0],
            WETBULB_COL: [25.0] * 6,
            LOAD_COL: [1000.0] * 6,
        },
        index=idx,
    )
    flags = extreme_flags(hourly)
    actual = pd.Series([100.0] * 6, index=idx)
    pred = pd.Series([110.0, 90.0, 100.0, 100.0, 100.0, 100.0], index=idx)
    scores = mape_by_condition(actual, pred, flags)
    assert set(scores) == {"overall"} | set(EXTREME_FLAGS) | {"any_extreme"}
    assert scores["extreme_heat"]["n_scored"] == 2
    assert abs(scores["extreme_heat"]["mape_pct"] - 10.0) < 1e-9
    assert scores["extreme_cold"]["n_scored"] == 0
