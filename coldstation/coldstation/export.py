"""Submission CSV export for the 「启成」 platform.

The official upload format has not been released, so every column name and
the timestamp format are configurable through a small JSON template
(``configs/qicheng_export_template.json``). When the real interface spec
arrives, edit the JSON — no code change needed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

DEFAULT_TEMPLATE = {
    "timestamp_column": "timeStamp",
    "timestamp_format": "%Y-%m-%d %H:%M:%S",
    "station_column": "stationId",
    "load_column": "TotalRealTimeLoad_pred",
    "equipment_column_suffix": "_pred",
    "float_format": "%.3f",
    "encoding": "utf-8-sig",
}


def load_template(path: str | Path | None = None) -> dict:
    template = dict(DEFAULT_TEMPLATE)
    if path is not None:
        template.update(json.loads(Path(path).read_text(encoding="utf-8")))
    return template


def build_submission_frame(
    station_id: str,
    load_pred: pd.Series,
    equipment_preds: dict[str, pd.Series] | None = None,
    template: dict | None = None,
) -> pd.DataFrame:
    """Assemble one station's hourly predictions into the submission layout."""
    tpl = template or dict(DEFAULT_TEMPLATE)
    index = load_pred.index
    out = pd.DataFrame(index=index)
    out[tpl["station_column"]] = station_id
    out[tpl["load_column"]] = load_pred
    for target_col, pred in (equipment_preds or {}).items():
        out[target_col + tpl["equipment_column_suffix"]] = pred.reindex(index)
    out.insert(0, tpl["timestamp_column"], index.strftime(tpl["timestamp_format"]))
    return out.reset_index(drop=True)


def write_submission(frame: pd.DataFrame, path: str | Path, template: dict | None = None) -> Path:
    tpl = template or dict(DEFAULT_TEMPLATE)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, float_format=tpl["float_format"], encoding=tpl["encoding"])
    return path
