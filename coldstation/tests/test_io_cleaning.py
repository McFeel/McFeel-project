import numpy as np
import pandas as pd
import pytest

from coldstation.cleaning import aggregate_hourly, clean_raw, prepare_hourly
from coldstation.io import read_history
from coldstation.stations import LOAD_COL, TIMESTAMP_COL, get_station


@pytest.mark.parametrize("station_id", ["A", "B", "C"])
def test_read_sample_matches_schema(station_id, sample_paths):
    config = get_station(station_id)
    df = read_history(config, sample_paths[station_id])
    assert list(df.columns) == config.columns
    assert len(df) == 48  # two header rows skipped
    assert pd.api.types.is_datetime64_any_dtype(df[TIMESTAMP_COL])
    # All value columns parsed as numeric.
    assert all(
        pd.api.types.is_numeric_dtype(df[c]) for c in df.columns if c != TIMESTAMP_COL
    )


def test_missing_file_error_mentions_env_var():
    config = get_station("A")
    with pytest.raises(FileNotFoundError, match="COLD_STATION_DATA_DIR"):
        read_history(config, "/nonexistent/file.xlsx")


def test_sentinel_and_bounds_cleaning(sample_paths):
    config = get_station("A")
    raw = read_history(config, sample_paths["A"])
    assert (raw["CWTempReturn"] <= -8000).any()  # sample includes -8888.7998

    cleaned, report = clean_raw(raw)
    assert report.sentinel_cells > 0
    assert report.out_of_bounds_cells >= 2  # negative load + 99 Hz frequency
    assert not (cleaned["CWTempReturn"].dropna() <= -8000).any()
    assert not (cleaned[LOAD_COL].dropna() < 0).any()
    assert not (cleaned["PriChWPVSDFreq01"].dropna() > 60).any()


def test_clean_raw_builds_regular_grid(sample_paths):
    config = get_station("B")
    raw = read_history(config, sample_paths["B"])
    # Drop two rows to create a gap; the grid must restore them as NaN rows.
    raw_gappy = raw.drop(index=[10, 11]).reset_index(drop=True)
    cleaned, report = clean_raw(raw_gappy)
    assert report.n_missing_grid_rows == 2
    assert len(cleaned) == 48
    assert (cleaned.index[1] - cleaned.index[0]) == pd.Timedelta(minutes=5)


def test_hourly_aggregation_and_coverage_mask(sample_paths):
    config = get_station("C")
    raw = read_history(config, sample_paths["C"])
    hourly, _ = prepare_hourly(raw)
    assert len(hourly) == 4  # 48 x 5min = 4 hours

    cleaned, _ = clean_raw(raw)
    # Wipe most of the first hour for one column: below min coverage -> NaN.
    cleaned.iloc[0:8, cleaned.columns.get_loc(LOAD_COL)] = np.nan
    hourly2 = aggregate_hourly(cleaned, min_points=6)
    assert np.isnan(hourly2[LOAD_COL].iloc[0])
    assert not np.isnan(hourly2[LOAD_COL].iloc[2])
