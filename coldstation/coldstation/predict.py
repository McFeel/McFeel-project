"""Producing a real next-24h submission (train on all data, forecast the
next day, export the configurable submission CSV).

Weather for the target day: pass a forecast CSV (columns: timeStamp,
OutdoorTdbin, OutdoorWetTemp — hourly). Without one, the pipeline falls
back to 24h-lagged weather (persistence), which is clearly weaker; get a
real forecast before submitting.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .features import (
    equipment_feature_frame,
    load_feature_frame,
    running_chillers,
)
from .models import estimate_chillers_from_load, fit_regressor
from .stations import DRYBULB_COL, LOAD_COL, TIMESTAMP_COL, WETBULB_COL, StationConfig

FORECAST_HOURS = 24


def _extended_frame(hourly: pd.DataFrame, weather_forecast: pd.DataFrame | None) -> pd.DataFrame:
    """Append the next 24 hourly rows (NaN except forecast weather)."""
    start = hourly.index.max() + pd.Timedelta(hours=1)
    future_index = pd.date_range(start, periods=FORECAST_HOURS, freq="h")
    future = pd.DataFrame(index=future_index, columns=hourly.columns, dtype=float)
    if weather_forecast is not None:
        wf = weather_forecast.set_index(TIMESTAMP_COL)
        for col in (DRYBULB_COL, WETBULB_COL):
            if col in wf.columns:
                future[col] = wf[col].reindex(future_index)
    extended = pd.concat([hourly, future])
    extended.index.name = hourly.index.name
    return extended


def predict_next_day(
    hourly: pd.DataFrame,
    config: StationConfig,
    model_name: str = "hgb",
    weather_forecast: pd.DataFrame | None = None,
    equipment_targets: list[str] | None = None,
) -> tuple[pd.Series, dict[str, pd.Series]]:
    """Return (hourly load forecast, {equipment target -> hourly forecast})
    for the 24 hours following the end of the history."""
    extended = _extended_frame(hourly, weather_forecast)
    future_index = extended.index[-FORECAST_HOURS:]
    use_lagged_weather = weather_forecast is None

    load_features = load_feature_frame(extended, use_weather_lag_only=use_lagged_weather)
    load_model = fit_regressor(load_features.loc[hourly.index], model_name=model_name)
    load_pred = load_model.predict(load_features.loc[future_index])

    # Equipment models condition on load and running-chiller count; both are
    # unknown for the future day, so use the load forecast and the
    # load->chiller-count heuristic learned from history.
    train_n_on = running_chillers(hourly, config)
    future_n_on = estimate_chillers_from_load(load_pred, hourly[LOAD_COL], train_n_on)

    combined_load = pd.concat([hourly[LOAD_COL], load_pred])
    eq_features = equipment_feature_frame(extended, config, load_series=combined_load)
    eq_features.loc[future_index, "n_chillers_on"] = future_n_on

    equipment_preds: dict[str, pd.Series] = {}
    targets = equipment_targets if equipment_targets is not None else config.equipment_targets
    for target_col in targets:
        if target_col not in hourly.columns:
            continue
        frame = eq_features.copy()
        frame["target"] = extended[target_col]
        if frame.loc[hourly.index, "target"].notna().sum() < 24:
            continue
        model = fit_regressor(frame.loc[hourly.index], model_name=model_name)
        equipment_preds[target_col] = model.predict(frame.loc[future_index])

    return load_pred, equipment_preds


def read_weather_forecast(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df[TIMESTAMP_COL] = pd.to_datetime(df[TIMESTAMP_COL])
    return df
