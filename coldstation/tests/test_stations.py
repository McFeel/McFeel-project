import pytest

from coldstation.stations import get_station


def test_column_counts_match_exports():
    assert len(get_station("A").columns) == 76
    assert len(get_station("B").columns) == 62
    assert len(get_station("C").columns) == 56


def test_station_quirks():
    a, b, c = (get_station(s) for s in "ABC")
    # A has both CWTempReturn and CWTempReturn01 (same Chinese label).
    assert "CWTempReturn" in a.columns and "CWTempReturn01" in a.columns
    # B has no cooling-tower outlet temperature columns.
    assert not any("CTOutletTemp" in col or "CTLeaveTemp" in col for col in b.columns)
    # B: 3 chilled-water pump frequencies but 4 pump powers/meters.
    assert "PriChWPVSDFreq03" in b.columns and "PriChWPVSDFreq04" not in b.columns
    assert "PriChWPPower04" in b.columns
    # C uses "Setting" naming and has no cooling-tower energy counters.
    assert "ChChWTempSupplySetting01" in c.columns
    assert "ChChWTempSupplySetPoint01" not in c.columns
    assert not any(col.startswith("CTPowerTotal") for col in c.columns)


def test_no_duplicate_columns():
    for sid in "ABC":
        cols = get_station(sid).columns
        assert len(cols) == len(set(cols)), f"duplicate columns in station {sid}"


def test_default_equipment_targets_are_real_columns():
    for sid in "ABC":
        cfg = get_station(sid)
        assert cfg.equipment_targets, sid
        assert all(t in cfg.columns for t in cfg.equipment_targets)


def test_replace_equipment_targets_validates():
    cfg = get_station("A")
    replaced = cfg.replace_equipment_targets(["ChPower01"])
    assert replaced.equipment_targets == ["ChPower01"]
    with pytest.raises(ValueError):
        cfg.replace_equipment_targets(["NotAColumn"])


def test_unknown_station():
    with pytest.raises(KeyError):
        get_station("D")
