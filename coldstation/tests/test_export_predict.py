import json

import pandas as pd

from coldstation.export import (
    DEFAULT_TEMPLATE,
    build_submission_frame,
    load_template,
    write_submission,
)
from coldstation.predict import predict_next_day


def test_submission_frame_default_template():
    idx = pd.date_range("2026-09-06", periods=24, freq="h")
    load_pred = pd.Series(range(24), index=idx, dtype=float)
    eq = {"ChPower01": pd.Series(1.0, index=idx)}
    frame = build_submission_frame("A", load_pred, eq)
    assert list(frame.columns) == [
        "timeStamp",
        "stationId",
        "TotalRealTimeLoad_pred",
        "ChPower01_pred",
    ]
    assert len(frame) == 24
    assert frame["timeStamp"].iloc[0] == "2026-09-06 00:00:00"


def test_template_override(tmp_path):
    tpl_path = tmp_path / "tpl.json"
    tpl_path.write_text(
        json.dumps({"timestamp_column": "time", "load_column": "load_kw"}),
        encoding="utf-8",
    )
    tpl = load_template(tpl_path)
    assert tpl["timestamp_column"] == "time"
    assert tpl["load_column"] == "load_kw"
    # Untouched keys keep their defaults.
    assert tpl["station_column"] == DEFAULT_TEMPLATE["station_column"]

    idx = pd.date_range("2026-09-06", periods=2, freq="h")
    frame = build_submission_frame("B", pd.Series([1.0, 2.0], index=idx), template=tpl)
    out = write_submission(frame, tmp_path / "sub.csv", tpl)
    read_back = pd.read_csv(out)
    assert list(read_back.columns) == ["time", "stationId", "load_kw"]


def test_predict_next_day_returns_24_hours(synthetic_hourly, station_c_config):
    load_pred, equipment_preds = predict_next_day(
        synthetic_hourly,
        station_c_config,
        equipment_targets=["ChPower01", "PriChWPVSDFreq01"],
    )
    assert len(load_pred) == 24
    assert load_pred.index.min() == synthetic_hourly.index.max() + pd.Timedelta(hours=1)
    assert (load_pred >= 0).all()
    assert set(equipment_preds) == {"ChPower01", "PriChWPVSDFreq01"}
    assert all(len(s) == 24 for s in equipment_preds.values())
