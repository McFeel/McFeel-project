"""Per-station schema configuration for stations A / B / C.

The three stations export the same kind of 5-minute history but with
different equipment counts and slightly different column naming
(e.g. station C uses ``ChChWTempSupplySetting`` instead of
``ChChWTempSupplySetPoint``). Everything station-specific lives here so the
rest of the pipeline is station-agnostic.

Equipment-parameter target columns are a DEFAULT ASSUMPTION (chilled-water
setpoint, VSD frequencies, powers, leaving-water temperatures where present)
because the official field list has not been released. Override them with
``StationConfig.replace_equipment_targets`` once the official scope arrives.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace


def numbered(prefix: str, count: int) -> list[str]:
    """['Foo01', 'Foo02', ...] column names."""
    return [f"{prefix}{i:02d}" for i in range(1, count + 1)]


TIMESTAMP_COL = "timeStamp"
LOAD_COL = "TotalRealTimeLoad"
DRYBULB_COL = "OutdoorTdbin"
WETBULB_COL = "OutdoorWetTemp"
HISTORY_SHEET = "历史数据"

# Placeholder used by the SCADA export for missing points (seen as
# -8888.7998 in station A). Anything at or below this is treated as missing.
SENTINEL_THRESHOLD = -8000.0


@dataclass(frozen=True)
class StationConfig:
    station_id: str
    default_filename: str
    n_chillers: int
    columns: list[str]
    amps_cols: list[str]
    setpoint_cols: list[str]
    freq_cols: list[str]
    power_cols: list[str]
    leave_temp_cols: list[str]
    equipment_targets: list[str] = field(default_factory=list)

    def replace_equipment_targets(self, targets: list[str]) -> "StationConfig":
        unknown = [t for t in targets if t not in self.columns]
        if unknown:
            raise ValueError(
                f"Station {self.station_id}: unknown target columns {unknown}"
            )
        return replace(self, equipment_targets=list(targets))


def _default_targets(cfg_kwargs: dict) -> list[str]:
    return (
        cfg_kwargs["setpoint_cols"]
        + cfg_kwargs["freq_cols"]
        + cfg_kwargs["power_cols"]
        + cfg_kwargs["leave_temp_cols"]
    )


def _station_a() -> StationConfig:
    n = 3
    freq_cols = (
        numbered("PriChWPVSDFreq", 3) + numbered("CWPVSDFreq", 3) + numbered("CTVSDFreq", 3)
    )
    power_cols = (
        numbered("ChPower", n)
        + numbered("PriChWPPower", 3)
        + numbered("CWPPower", 3)
        + numbered("CTPower", 3)
    )
    columns = (
        [TIMESTAMP_COL]
        + numbered("ChAMPS", n)
        + numbered("ChChWTempSupplySetPoint", n)
        + numbered("ChEvapTemp", n)
        + numbered("ChLeaveEvapTemp", n)
        + numbered("ChEnterEvapTemp", n)
        + numbered("ChCondTemp", n)
        + numbered("ChLeaveCondTemp", n)
        + numbered("ChEnterCondTemp", n)
        + numbered("ChRealtimeEfficiencyKW", n)
        + ["PriChWDiffPress", "PriChWFlow01", "PriChWTempSupply01", "PriChWTempReturn01"]
        + ["CWFlow01", "CWTempSupply01", "CWTempReturn", "CWTempReturn01"]
        + numbered("CTOutletTemp", 3)
        + [WETBULB_COL, DRYBULB_COL]
        + freq_cols
        + power_cols
        + numbered("ChPowerTotal", n)
        + numbered("PriChWPPowerTotal", 3)
        + numbered("CWPPowerTotal", 3)
        + numbered("CTPowerTotal", 3)
        + [LOAD_COL, "CoolingCapacityTotalDaily"]
    )
    kwargs = dict(
        station_id="A",
        default_filename="训练数据项目A历史数据_2025-04-01_2025-10-31.xlsx",
        n_chillers=n,
        columns=columns,
        amps_cols=numbered("ChAMPS", n),
        setpoint_cols=numbered("ChChWTempSupplySetPoint", n),
        freq_cols=freq_cols,
        power_cols=power_cols,
        leave_temp_cols=numbered("ChLeaveEvapTemp", n) + numbered("CTOutletTemp", 3),
    )
    return StationConfig(**kwargs, equipment_targets=_default_targets(kwargs))


def _station_b() -> StationConfig:
    n = 2
    freq_cols = (
        numbered("PriChWPVSDFreq", 3) + numbered("CWPVSDFreq", 4) + numbered("CTVSDFreq", 3)
    )
    power_cols = (
        numbered("ChPower", n)
        + numbered("PriChWPPower", 4)
        + numbered("CWPPower", 4)
        + numbered("CTPower", 3)
    )
    columns = (
        [TIMESTAMP_COL]
        + numbered("ChAMPS", n)
        + numbered("ChChWTempSupplySetPoint", n)
        + numbered("ChLeaveEvapTemp", n)
        + numbered("ChEnterEvapTemp", n)
        + numbered("ChLeaveCondTemp", n)
        + numbered("ChEnterCondTemp", n)
        + numbered("ChRealtimeEfficiency", n)
        + ["PriChWPress", "PriChWFlow01", "PriChWTempSupply01", "PriChWTempReturn01"]
        + ["CWFlow01", "CWTempSupply01", "CWTempReturn01"]
        + [WETBULB_COL, DRYBULB_COL]
        + freq_cols
        + power_cols
        + numbered("ChPowerTotal", n)
        + numbered("PriChWPPowerTotal", 4)
        + numbered("CWPPowerTotal", 4)
        + numbered("CTPowerTotal", 3)
        + [LOAD_COL, "CoolingCapacityTotalDaily"]
    )
    kwargs = dict(
        station_id="B",
        default_filename="训练数据项目B历史数据_2023-04-01_2023-10-31.xlsx",
        n_chillers=n,
        columns=columns,
        amps_cols=numbered("ChAMPS", n),
        setpoint_cols=numbered("ChChWTempSupplySetPoint", n),
        freq_cols=freq_cols,
        power_cols=power_cols,
        # Station B has no cooling-tower outlet temperature columns.
        leave_temp_cols=numbered("ChLeaveEvapTemp", n),
    )
    return StationConfig(**kwargs, equipment_targets=_default_targets(kwargs))


def _station_c() -> StationConfig:
    n = 2
    freq_cols = (
        numbered("PriChWPVSDFreq", 3) + numbered("CWPVSDFreq", 3) + numbered("CTVSDFreq", 2)
    )
    power_cols = (
        numbered("ChPower", n)
        + numbered("PriChWPPower", 3)
        + numbered("CWPPower", 3)
        + numbered("CTPower", 2)
    )
    columns = (
        [TIMESTAMP_COL]
        + numbered("ChAMPS", n)
        # Station C names the setpoint "Setting", not "SetPoint".
        + numbered("ChChWTempSupplySetting", n)
        + numbered("ChEvapTemp", n)
        + numbered("ChLeaveEvapTemp", n)
        + numbered("ChEnterEvapTemp", n)
        + numbered("ChCondTemp", n)
        + numbered("ChLeaveCondTemp", n)
        + numbered("ChEnterCondTemp", n)
        + ["PriChWDP01", "PriChWFlow", "PriChWTempSupply01", "PriChWTempReturn01"]
        + ["CWFlow01", "CWTempSupply01", "CWTempReturn01"]
        + numbered("CTLeaveTemp", 2)
        + [WETBULB_COL, DRYBULB_COL]
        + freq_cols
        + power_cols
        + numbered("ChPowerTotal", n)
        + numbered("PriChWPPowerTotal", 3)
        + numbered("CWPPowerTotal", 3)
        # Station C has no cooling-tower energy (PowerTotal) columns.
        + [LOAD_COL, "CoolingCapacityTotalDaily"]
    )
    kwargs = dict(
        station_id="C",
        default_filename="训练数据项目C历史数据_2026-01-01_2026-07-31.xlsx",
        n_chillers=n,
        columns=columns,
        amps_cols=numbered("ChAMPS", n),
        setpoint_cols=numbered("ChChWTempSupplySetting", n),
        freq_cols=freq_cols,
        power_cols=power_cols,
        leave_temp_cols=numbered("ChLeaveEvapTemp", n) + numbered("CTLeaveTemp", 2),
    )
    return StationConfig(**kwargs, equipment_targets=_default_targets(kwargs))


STATIONS: dict[str, StationConfig] = {
    "A": _station_a(),
    "B": _station_b(),
    "C": _station_c(),
}


def get_station(station_id: str) -> StationConfig:
    key = station_id.upper()
    if key not in STATIONS:
        raise KeyError(f"Unknown station '{station_id}'. Expected one of {sorted(STATIONS)}.")
    return STATIONS[key]
