"""Retention fitting utilities."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .schema import DataValidationError, require_columns


@dataclass(frozen=True)
class RetentionFit:
    """Power-law retention fit ``G/G0 = C * (t/t_ref)^(-nu)``."""

    exponent_nu: float
    prefactor_c: float
    r_squared: float
    point_count: int
    time_reference_s: float
    time_min_s: float
    time_max_s: float


def fit_power_law_retention(
    df: pd.DataFrame,
    *,
    time_column: str = "timestamp_s",
    conductance_column: str = "conductance_s",
) -> RetentionFit:
    """Fit a power law in log-log space after excluding invalid points."""

    require_columns(df, [time_column, conductance_column])
    time = pd.to_numeric(df[time_column], errors="coerce").to_numpy(dtype=float)
    conductance = pd.to_numeric(df[conductance_column], errors="coerce").to_numpy(dtype=float)

    mask = np.isfinite(time) & np.isfinite(conductance) & (time > 0) & (conductance > 0)
    time = time[mask]
    conductance = conductance[mask]
    if len(time) < 3:
        raise DataValidationError("retention fitting requires at least three positive points")

    order = np.argsort(time)
    time = time[order]
    conductance = conductance[order]
    time_reference = float(time[0])
    normalized_time = time / time_reference
    normalized_conductance = conductance / conductance[0]

    x = np.log(normalized_time)
    y = np.log(normalized_conductance)
    slope, intercept = np.polyfit(x, y, deg=1)
    predicted = slope * x + intercept
    residual = float(np.sum((y - predicted) ** 2))
    total = float(np.sum((y - np.mean(y)) ** 2))
    r_squared = 1.0 - residual / total if total > 0 else float("nan")

    return RetentionFit(
        exponent_nu=float(-slope),
        prefactor_c=float(np.exp(intercept)),
        r_squared=r_squared,
        point_count=int(len(time)),
        time_reference_s=time_reference,
        time_min_s=float(time.min()),
        time_max_s=float(time.max()),
    )
