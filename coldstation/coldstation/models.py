"""Forecast models.

Baseline philosophy: start with interpretable, robust tabular models
(gradient boosting + a linear reference), keep a registry slot open for
sequence models (LSTM / temporal transformer) once the tabular baseline is
validated on real data. Do NOT ship a univariate ETS/ARIMA-only solution —
the scoring rewards weather/calendar-conditioned accuracy, especially in
extreme conditions.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


def _hgb() -> HistGradientBoostingRegressor:
    return HistGradientBoostingRegressor(
        max_iter=400,
        learning_rate=0.06,
        max_depth=None,
        max_leaf_nodes=31,
        min_samples_leaf=20,
        l2_regularization=1.0,
        random_state=7,
    )


def _ridge() -> Pipeline:
    return Pipeline(
        [
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("model", Ridge(alpha=1.0)),
        ]
    )


def make_regressor(name: str):
    """Model registry. 'seq' is a reserved slot for a sequence model."""
    if name == "hgb":
        return _hgb()
    if name == "ridge":
        return _ridge()
    if name == "seq":
        raise NotImplementedError(
            "Sequence-model slot: implement a model exposing fit(X, y) / "
            "predict(X) (e.g. LSTM or temporal transformer over the hourly "
            "frame) and register it here. The tabular baseline must be "
            "beaten on the 30-day holdout before switching."
        )
    raise ValueError(f"Unknown model '{name}'. Available: hgb, ridge, seq (slot).")


@dataclass
class FittedModel:
    name: str
    feature_cols: list[str]
    estimator: object

    def predict(self, features: pd.DataFrame) -> pd.Series:
        X = features[self.feature_cols]
        pred = self.estimator.predict(X)
        return pd.Series(pred, index=features.index, name="prediction")


def fit_regressor(
    features: pd.DataFrame,
    target_col: str = "target",
    model_name: str = "hgb",
    non_negative: bool = True,
) -> FittedModel:
    """Fit one regressor on rows where the target is present."""
    feature_cols = [c for c in features.columns if c != target_col]
    y = features[target_col]
    train_mask = y.notna()
    if model_name == "ridge":
        # The linear pipeline imputes NaN features; HGB handles NaN natively.
        train_mask &= features[feature_cols].notna().any(axis=1)
    X = features.loc[train_mask, feature_cols]
    estimator = make_regressor(model_name)
    estimator.fit(X, y[train_mask])
    fitted = FittedModel(name=model_name, feature_cols=feature_cols, estimator=estimator)
    if non_negative:
        original = fitted.predict

        def _clipped(feats: pd.DataFrame) -> pd.Series:
            return original(feats).clip(lower=0.0)

        fitted.predict = _clipped  # type: ignore[method-assign]
    return fitted


def estimate_chillers_from_load(
    load: pd.Series,
    train_load: pd.Series,
    train_n_on: pd.Series,
) -> pd.Series:
    """Heuristic for real submissions: the number of running chillers is an
    operational decision that is unknown 24h ahead, so map forecast load to
    the historically most common chiller count at that load level."""
    valid = train_load.notna() & train_n_on.notna()
    tl, tn = train_load[valid], train_n_on[valid]
    if tl.empty:
        return pd.Series(np.nan, index=load.index)
    # Boundary between k and k+1 chillers = median load observed at each count.
    medians = tl.groupby(tn).median().sort_index()
    counts = medians.index.to_numpy(dtype=float)
    centers = medians.to_numpy(dtype=float)
    order = np.argsort(centers)
    centers, counts = centers[order], counts[order]

    def nearest(value: float) -> float:
        if np.isnan(value):
            return np.nan
        return float(counts[int(np.argmin(np.abs(centers - value)))])

    return load.map(nearest)


def off_mask_for_target(target: pd.Series, target_col: str) -> pd.Series:
    """Hours where the equipment behind ``target_col`` is off.

    ASSUMPTION (replaceable): off-hours are excluded from equipment MAPE and
    reported separately, because a near-zero denominator makes percentage
    error meaningless and the official rules do not define the treatment.
    Only power/frequency/amperage style targets have an off state;
    temperatures and setpoints are always scored.
    """
    if not any(k in target_col for k in ("Power", "Freq", "AMPS")):
        return pd.Series(False, index=target.index)
    positive = target[target > 0]
    threshold = max(1e-6, 0.02 * float(positive.median())) if not positive.empty else 1e-6
    return target.fillna(0.0) <= threshold
