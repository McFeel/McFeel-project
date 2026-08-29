"""Command-line entry point.

Examples (run from the ``coldstation/`` folder):

    # Where is my data? What does it look like?
    python -m coldstation inspect --station A

    # 30-day holdout backtest with extreme-condition breakdown
    python -m coldstation backtest --station A --model hgb

    # Train on everything and export a next-24h submission CSV
    python -m coldstation predict --station A --out out/submission_A.csv
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .backtest import backtest_station
from .cleaning import prepare_hourly
from .export import build_submission_frame, load_template, write_submission
from .io import DATA_DIR_ENV, data_dir, read_history, resolve_history_path
from .predict import predict_next_day, read_weather_forecast
from .stations import LOAD_COL, get_station


def _load_hourly(args) -> tuple:
    config = get_station(args.station)
    if args.targets:
        config = config.replace_equipment_targets(args.targets.split(","))
    raw = read_history(config, args.input)
    hourly, report = prepare_hourly(raw)
    return config, hourly, report


def cmd_inspect(args) -> int:
    config = get_station(args.station)
    path = resolve_history_path(config, args.input)
    print(f"Data dir ({DATA_DIR_ENV}): {data_dir()}")
    print(f"Station {config.station_id}: {path} (exists: {path.exists()})")
    if not path.exists():
        return 1
    config, hourly, report = _load_hourly(args)
    print(f"Cleaning report: {json.dumps(report.as_dict(), indent=2)}")
    print(f"Hourly rows: {len(hourly)} ({hourly.index.min()} .. {hourly.index.max()})")
    coverage = hourly[LOAD_COL].notna().mean()
    print(f"Hourly load coverage: {coverage:.1%}")
    print(f"Equipment targets ({len(config.equipment_targets)}): {config.equipment_targets}")
    return 0


def cmd_backtest(args) -> int:
    config, hourly, report = _load_hourly(args)
    result = backtest_station(
        hourly, config, model_name=args.model, holdout_days=args.holdout_days
    )
    print(json.dumps(result.summary(), ensure_ascii=False, indent=2))
    report_path = result.save(args.out)
    print(f"\nSaved report to {report_path}", file=sys.stderr)
    return 0


def cmd_predict(args) -> int:
    config, hourly, report = _load_hourly(args)
    weather = read_weather_forecast(args.weather) if args.weather else None
    load_pred, equipment_preds = predict_next_day(
        hourly, config, model_name=args.model, weather_forecast=weather
    )
    template = load_template(args.template)
    frame = build_submission_frame(config.station_id, load_pred, equipment_preds, template)
    out_path = write_submission(frame, args.out, template)
    print(f"Wrote {len(frame)} hourly rows to {out_path}")
    if weather is None:
        print(
            "WARNING: no weather forecast supplied (--weather); used 24h-lagged "
            "weather as a fallback. Provide a real forecast before submitting.",
            file=sys.stderr,
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="coldstation",
        description="Cold-station load & equipment-parameter forecasting pipeline",
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--station", required=True, choices=["A", "B", "C"], help="station id")
        p.add_argument("--input", default=None, help="explicit path to the history file")
        p.add_argument(
            "--targets",
            default=None,
            help="comma-separated equipment target columns (overrides the default assumption)",
        )

    p_inspect = sub.add_parser("inspect", help="check data location, schema and coverage")
    common(p_inspect)
    p_inspect.set_defaults(func=cmd_inspect)

    p_backtest = sub.add_parser("backtest", help="30-day holdout backtest with extreme breakdown")
    common(p_backtest)
    p_backtest.add_argument("--model", default="hgb", help="hgb | ridge | seq (slot)")
    p_backtest.add_argument("--holdout-days", type=int, default=30)
    p_backtest.add_argument("--out", default="out", help="output folder for reports")
    p_backtest.set_defaults(func=cmd_backtest)

    p_predict = sub.add_parser("predict", help="train on all data, export next-24h submission CSV")
    common(p_predict)
    p_predict.add_argument("--model", default="hgb")
    p_predict.add_argument("--weather", default=None, help="hourly weather forecast CSV")
    p_predict.add_argument("--template", default=None, help="submission template JSON")
    p_predict.add_argument("--out", default="out/submission.csv", help="output CSV path")
    p_predict.set_defaults(func=cmd_predict)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
