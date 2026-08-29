"""Feature engineering for the hourly forecast models.

Load-model features use only information that is available when forecasting
the next 24 hours:

* lagged load at >= 24h (24/48/168h) plus a trailing daily mean ending at
  the 24h lag — no lag shorter than 24h, so the whole next day can be
  predicted in one shot without recursive error accumulation;
* calendar features (hour-of-day sin/cos, day-of-week, weekend flag);
* outdoor dry-bulb / wet-bulb temperature of the target hour. ASSUMPTION:
  the competition provides (or allows) weather forecasts for the scoring
  day; during backtests the recorded actual weather stands in for a perfect
  forecast. If only past weather is allowed, swap these for 24h-lagged
  weather via ``use_weather_lag_only=True``.

Equipment-parameter features condition on the same-hour load (actual during
training/backtest scoring of the equipment task, or the load forecast when
producing a real submission), weather, and the number of running chillers
derived from ChAMPS.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .stations import DRYBULB_COL, LOAD_COL, WETBULB_COL, StationConfig

LOAD_LAGS_H = (24, 48, 168)
AMPS_ON_THRESHOLD = 5.0  # chiller considered running above this amperage


def calendar_features(index: pd.DatetimeIndex) -> pd.DataFrame:
    hour = index.hour.to_numpy()
    out = pd.DataFrame(index=index)
    out["hour"] = hour
    out["hour_sin"] = np.sin(2 * np.pi * hour / 24)
    out["hour_cos"] = np.cos(2 * np.pi * hour / 24)
    out["dayofweek"] = index.dayofweek.to_numpy()
    out["is_weekend"] = (index.dayofweek >= 5).astype(int)
    return out


def load_feature_frame(
    hourly: pd.DataFrame,
    use_weather_lag_only: bool = False,
) -> pd.DataFrame:
    """Feature matrix + 'target' column for the hourly load model."""
    load = hourly[LOAD_COL]
    feats = calendar_features(hourly.index)

    for lag in LOAD_LAGS_H:
        feats[f"load_lag_{lag}h"] = load.shift(lag)
    # Trailing 24h mean ending 24h ago: yesterday's typical level.
    feats["load_mean_prev_day"] = load.shift(24).rolling(24, min_periods=12).mean()
    # Same-hour-last-week baseline is load_lag_168h; keep the ratio of the
    # two baselines as a trend signal.
    feats["baseline_trend"] = feats["load_lag_24h"] / feats["load_lag_168h"].replace(0, np.nan)

    for col in (DRYBULB_COL, WETBULB_COL):
        if col in hourly.columns:
            weather = hourly[col].shift(24) if use_weather_lag_only else hourly[col]
            feats[f"{col}_target_hour"] = weather
            feats[f"{col}_lag_24h"] = hourly[col].shift(24)

    feats["target"] = load
    return feats


def running_chillers(hourly: pd.DataFrame, config: StationConfig) -> pd.Series:
    """Number of chillers running per hour, derived from ChAMPS columns."""
    amps = hourly[[c for c in config.amps_cols if c in hourly.columns]]
    return (amps > AMPS_ON_THRESHOLD).sum(axis=1).astype(float)


def equipment_feature_frame(
    hourly: pd.DataFrame,
    config: StationConfig,
    load_series: pd.Series | None = None,
) -> pd.DataFrame:
    """Feature matrix for the equipment-parameter models.

    ``load_series`` defaults to the actual hourly load; pass the load
    forecast when generating a real submission so the equipment predictions
    are consistent with the predicted load.
    """
    load = hourly[LOAD_COL] if load_series is None else load_series.reindex(hourly.index)
    feats = calendar_features(hourly.index)
    feats["load"] = load
    feats["load_lag_24h"] = hourly[LOAD_COL].shift(24)
    feats["n_chillers_on"] = running_chillers(hourly, config)
    for col in (DRYBULB_COL, WETBULB_COL):
        if col in hourly.columns:
            feats[col] = hourly[col]
    return feats
