"""Cold-station load & equipment-parameter forecasting pipeline.

Reads desensitized 5-minute operational history exported from three
chiller-plant stations (A/B/C), cleans and aggregates it to hourly data,
trains load and equipment-parameter forecast models, backtests on the last
30 days (with a separate extreme-condition breakdown), and exports
submission CSVs with configurable column names.

Real training data (xlsx) is NEVER stored in this repository. The pipeline
reads it from a local folder pointed to by the COLD_STATION_DATA_DIR
environment variable.
"""

__version__ = "0.1.0"
