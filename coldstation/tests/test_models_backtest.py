import numpy as np
import pandas as pd
import pytest

from coldstation.backtest import backtest_station, split_holdout
from coldstation.features import load_feature_frame, LOAD_LAGS_H
from coldstation.models import estimate_chillers_from_load, make_regressor
from coldstation.stations import LOAD_COL


def test_load_features_use_only_day_ahead_information(synthetic_hourly):
    feats = load_feature_frame(synthetic_hourly)
    # No load lag shorter than 24h may exist (24h-ahead forecasting).
    lag_cols = [c for c in feats.columns if c.startswith("load_lag_")]
    assert lag_cols == [f"load_lag_{h}h" for h in LOAD_LAGS_H]
    assert min(LOAD_LAGS_H) >= 24
    # lag-24 alignment check
    ts = feats.index[200]
    assert feats.loc[ts, "load_lag_24h"] == synthetic_hourly.loc[
        ts - pd.Timedelta(hours=24), LOAD_COL
    ]


def test_split_holdout_30_days(synthetic_hourly):
    train, holdout = split_holdout(synthetic_hourly, 30)
    assert holdout.index.min() > train.index.max()
    assert len(holdout) == 30 * 24
    assert len(train) + len(holdout) == len(synthetic_hourly)


def test_seq_model_slot_reserved():
    with pytest.raises(NotImplementedError):
        make_regressor("seq")
    with pytest.raises(ValueError):
        make_regressor("nope")


@pytest.mark.parametrize("model_name", ["hgb", "ridge"])
def test_backtest_learns_synthetic_signal(synthetic_hourly, station_c_config, model_name):
    result = backtest_station(
        synthetic_hourly,
        station_c_config,
        model_name=model_name,
        equipment_targets=["ChPower01", "PriChWPVSDFreq01"],
    )
    load_overall = result.load["overall"]
    assert load_overall["n_scored"] > 600
    # The synthetic signal is learnable: sanity bound, NOT a claim about
    # real-data MAPE (real xlsx never touches this repo/CI).
    assert load_overall["mape_pct"] < 15.0

    # Extreme-heat subset must be non-empty and scored separately.
    assert result.load["extreme_heat"]["n_scored"] > 0

    for target in ["ChPower01", "PriChWPVSDFreq01"]:
        assert result.equipment[target]["overall"]["mape_pct"] is not None
        assert result.equipment[target]["overall"]["mape_pct"] < 20.0


def test_backtest_report_saving(tmp_path, synthetic_hourly, station_c_config):
    result = backtest_station(
        synthetic_hourly, station_c_config, equipment_targets=["ChPower01"]
    )
    report_path = result.save(tmp_path)
    assert report_path.exists()
    assert (tmp_path / "backtest_C_hgb_load_predictions.csv").exists()


def test_estimate_chillers_from_load():
    train_load = pd.Series([500.0] * 50 + [1500.0] * 50)
    train_n_on = pd.Series([1.0] * 50 + [2.0] * 50)
    future = pd.Series([450.0, 1600.0])
    est = estimate_chillers_from_load(future, train_load, train_n_on)
    assert est.tolist() == [1.0, 2.0]
