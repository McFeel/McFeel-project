"""MAPE scoring and extreme-condition flagging, following the competition
rules (附件1):

* Load forecast: 24h hourly MAPE <= 5% per station; extreme-condition
  MAPE <= 8% for the bonus.
* Equipment parameters: MAPE <= 6%; extreme-condition MAPE <= 10%.
* Extreme conditions: dry bulb >= 35C (high heat); wet bulb >= 28C or
  RH >= 85% (high humidity; RH is not in the exports so only the wet-bulb
  branch is evaluated); dry bulb <= -10C (extreme cold, northern public
  institutions only); adjacent-hour cooling-load change rate >= 20%
  (load jump).

Hours where the plant is effectively off are either excluded from MAPE or
counted separately — a tiny actual value makes percentage error meaningless
and the official rules do not define the off-hour treatment yet.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .stations import DRYBULB_COL, LOAD_COL, WETBULB_COL

HIGH_HEAT_DRYBULB = 35.0
HIGH_HUMIDITY_WETBULB = 28.0
EXTREME_COLD_DRYBULB = -10.0
LOAD_JUMP_RATE = 0.20

EXTREME_FLAGS = ["extreme_heat", "extreme_humidity", "extreme_cold", "load_jump"]


@dataclass
class MapeResult:
    mape: float | None
    n_scored: int
    n_excluded_off: int
    n_missing: int
    extra: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        d = {
            "mape_pct": None if self.mape is None else round(self.mape * 100, 3),
            "n_scored": self.n_scored,
            "n_excluded_off": self.n_excluded_off,
            "n_missing": self.n_missing,
        }
        d.update(self.extra)
        return d


def mape(
    actual: pd.Series,
    predicted: pd.Series,
    off_threshold: float = 0.0,
) -> MapeResult:
    """Mean absolute percentage error.

    Rows where the actual value is missing are dropped; rows where
    ``actual <= off_threshold`` (plant off / near-zero denominator) are
    excluded from the average and reported separately.
    """
    actual, predicted = actual.align(predicted, join="inner")
    valid = actual.notna() & predicted.notna()
    n_missing = int((~valid).sum())
    actual, predicted = actual[valid], predicted[valid]

    off = actual <= off_threshold
    n_off = int(off.sum())
    actual, predicted = actual[~off], predicted[~off]

    if len(actual) == 0:
        return MapeResult(mape=None, n_scored=0, n_excluded_off=n_off, n_missing=n_missing)
    value = float(np.mean(np.abs((predicted - actual) / actual)))
    return MapeResult(mape=value, n_scored=len(actual), n_excluded_off=n_off, n_missing=n_missing)


def default_off_threshold(load: pd.Series) -> float:
    """Off-hour threshold: 5% of the median positive load (assumption,
    replaceable once the official rule is known)."""
    positive = load[load > 0]
    if positive.empty:
        return 0.0
    return float(0.05 * positive.median())


def extreme_flags(hourly: pd.DataFrame, station_id: str | None = None) -> pd.DataFrame:
    """Boolean flags per hour for each extreme-condition category.

    ``extreme_cold`` only applies to northern public-institution stations per
    the rules; it is still computed for every station (it will simply never
    fire for southern stations in cooling season) so the caller can decide.
    """
    flags = pd.DataFrame(index=hourly.index)
    drybulb = hourly.get(DRYBULB_COL)
    wetbulb = hourly.get(WETBULB_COL)
    load = hourly.get(LOAD_COL)

    flags["extreme_heat"] = (
        (drybulb >= HIGH_HEAT_DRYBULB).fillna(False) if drybulb is not None else False
    )
    flags["extreme_humidity"] = (
        (wetbulb >= HIGH_HUMIDITY_WETBULB).fillna(False) if wetbulb is not None else False
    )
    flags["extreme_cold"] = (
        (drybulb <= EXTREME_COLD_DRYBULB).fillna(False) if drybulb is not None else False
    )

    if load is not None:
        prev = load.shift(1)
        rate = (load - prev).abs() / prev.abs()
        # Rate is undefined when the previous hour is ~0; treat as not a jump.
        jump = rate.where(prev.abs() > 1e-9) >= LOAD_JUMP_RATE
        flags["load_jump"] = jump.fillna(False)
    else:
        flags["load_jump"] = False

    flags["any_extreme"] = flags[EXTREME_FLAGS].any(axis=1)
    return flags


def mape_by_condition(
    actual: pd.Series,
    predicted: pd.Series,
    flags: pd.DataFrame,
    off_threshold: float = 0.0,
) -> dict[str, dict]:
    """Overall MAPE plus one MAPE per extreme-condition subset."""
    out: dict[str, dict] = {"overall": mape(actual, predicted, off_threshold).as_dict()}
    for name in EXTREME_FLAGS + ["any_extreme"]:
        mask = flags[name].reindex(actual.index).fillna(False).astype(bool)
        out[name] = mape(actual[mask], predicted[mask], off_threshold).as_dict()
    return out
