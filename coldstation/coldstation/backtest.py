"""Holdout backtesting.

Per station: the LAST 30 days of available hourly data form the validation
window (mirroring the official 30-day validation set); everything before is
training. Reported per station:

* hourly load MAPE overall and per extreme-condition category
  (targets: <= 5% overall, <= 8% extreme);
* per-equipment-target MAPE overall and extreme (targets: <= 6% / <= 10%),
  with off-hours excluded and counted separately.

The 24h-ahead setting is honored structurally: load features only use lags
>= 24h, so every validation hour is predicted with information that would
have been available one day earlier.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .features import equipment_feature_frame, load_feature_frame
from .metrics import default_off_threshold, extreme_flags, mape_by_condition
from .models import fit_regressor, off_mask_for_target
from .stations import LOAD_COL, StationConfig

HOLDOUT_DAYS = 30


@dataclass
class BacktestResult:
    station_id: str
    model_name: str
    train_start: str
    train_end: str
    holdout_start: str
    holdout_end: str
    load: dict
    equipment: dict
    load_predictions: pd.DataFrame

    def summary(self) -> dict:
        return {
            "station": self.station_id,
            "model": self.model_name,
            "train_window": [self.train_start, self.train_end],
            "holdout_window": [self.holdout_start, self.holdout_end],
            "load_mape": self.load,
            "equipment_mape": self.equipment,
        }

    def save(self, out_dir: str | Path) -> Path:
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        report_path = out / f"backtest_{self.station_id}_{self.model_name}.json"
        report_path.write_text(
            json.dumps(self.summary(), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        self.load_predictions.to_csv(
            out / f"backtest_{self.station_id}_{self.model_name}_load_predictions.csv"
        )
        return report_path


def split_holdout(
    hourly: pd.DataFrame, holdout_days: int = HOLDOUT_DAYS
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split the hourly frame into (train, holdout-last-N-days)."""
    if hourly.empty:
        raise ValueError("Hourly frame is empty; nothing to backtest.")
    cutoff = hourly.index.max() - pd.Timedelta(days=holdout_days)
    train = hourly[hourly.index <= cutoff]
    holdout = hourly[hourly.index > cutoff]
    if train.empty or holdout.empty:
        raise ValueError(
            f"Not enough history for a {holdout_days}-day holdout: "
            f"{hourly.index.min()} .. {hourly.index.max()}"
        )
    return train, holdout


def backtest_station(
    hourly: pd.DataFrame,
    config: StationConfig,
    model_name: str = "hgb",
    holdout_days: int = HOLDOUT_DAYS,
    equipment_targets: list[str] | None = None,
) -> BacktestResult:
    train, holdout = split_holdout(hourly, holdout_days)
    flags = extreme_flags(holdout)
    off_threshold = default_off_threshold(train[LOAD_COL])

    # ---- Load model -------------------------------------------------------
    features = load_feature_frame(hourly)
    train_feats = features.loc[train.index]
    holdout_feats = features.loc[holdout.index]
    load_model = fit_regressor(train_feats, model_name=model_name)
    load_pred = load_model.predict(holdout_feats)
    load_actual = holdout[LOAD_COL]
    load_scores = mape_by_condition(load_actual, load_pred, flags, off_threshold)

    predictions = pd.DataFrame(
        {"actual_load": load_actual, "predicted_load": load_pred}
    ).join(flags)

    # ---- Equipment-parameter models --------------------------------------
    targets = equipment_targets if equipment_targets is not None else config.equipment_targets
    equipment_scores: dict[str, dict] = {}
    eq_features = equipment_feature_frame(hourly, config)
    for target_col in targets:
        if target_col not in hourly.columns:
            equipment_scores[target_col] = {"error": "column not present"}
            continue
        frame = eq_features.copy()
        frame["target"] = hourly[target_col]
        if frame.loc[train.index, "target"].notna().sum() < 24:
            equipment_scores[target_col] = {"error": "insufficient training data"}
            continue
        model = fit_regressor(frame.loc[train.index], model_name=model_name)
        pred = model.predict(frame.loc[holdout.index])
        actual = holdout[target_col]
        off = off_mask_for_target(actual, target_col)
        scores = mape_by_condition(actual[~off], pred[~off], flags)
        scores["overall"]["n_off_hours"] = int(off.sum())
        equipment_scores[target_col] = scores

    return BacktestResult(
        station_id=config.station_id,
        model_name=model_name,
        train_start=str(train.index.min()),
        train_end=str(train.index.max()),
        holdout_start=str(holdout.index.min()),
        holdout_end=str(holdout.index.max()),
        load=load_scores,
        equipment=equipment_scores,
        load_predictions=predictions,
    )
