"""Transparent pulse-update and endurance metrics."""

from __future__ import annotations

import math
from typing import cast

import numpy as np
import pandas as pd

from .schema import DataValidationError, require_columns, validate_trace

BRANCH_KEYS = ["device_id", "cycle", "direction"]


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0 or not math.isfinite(denominator):
        return math.nan
    return numerator / denominator


def _r_squared(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 2 or np.allclose(y, y[0]):
        return math.nan
    slope, intercept = np.polyfit(x, y, deg=1)
    predicted = slope * x + intercept
    residual = float(np.sum((y - predicted) ** 2))
    total = float(np.sum((y - np.mean(y)) ** 2))
    return 1.0 - residual / total if total > 0 else math.nan


def _linearity_nrmse(values: np.ndarray) -> float:
    span = float(values[-1] - values[0])
    if np.isclose(span, 0.0):
        return math.nan
    progress = (values - values[0]) / span
    ideal = np.linspace(0.0, 1.0, len(values))
    return float(np.sqrt(np.mean((progress - ideal) ** 2)))


def _saturation_index(delta_abs: np.ndarray) -> float:
    if len(delta_abs) < 7:
        return math.nan
    quarter = max(1, len(delta_abs) // 4)
    early = float(np.mean(delta_abs[:quarter]))
    late = float(np.mean(delta_abs[-quarter:]))
    return _safe_ratio(late, early)


def _branch_metric_row(key: tuple[object, ...], group: pd.DataFrame) -> dict[str, object]:
    group = group.sort_values("pulse_index", kind="stable")
    values = group["conductance_s"].to_numpy(dtype=float)
    delta = np.diff(values)
    delta_abs = np.abs(delta)
    direction = str(key[2])
    expected_sign = 1.0 if direction == "potentiation" else -1.0

    mean_abs_update = float(np.mean(delta_abs)) if len(delta_abs) else math.nan
    update_cv = (
        _safe_ratio(float(np.std(delta_abs, ddof=0)), mean_abs_update)
        if len(delta_abs)
        else math.nan
    )
    monotonicity = float(np.mean(np.sign(delta) == expected_sign)) if len(delta) else math.nan

    minimum = float(np.min(values))
    maximum = float(np.max(values))
    dynamic_range_ratio = _safe_ratio(maximum, minimum)

    return {
        "device_id": key[0],
        "cycle": int(cast(int, key[1])),
        "direction": direction,
        "state_count": int(len(values)),
        "pulse_update_count": int(len(delta)),
        "initial_conductance_s": float(values[0]),
        "final_conductance_s": float(values[-1]),
        "endpoint_change_s": float(values[-1] - values[0]),
        "conductance_min_s": minimum,
        "conductance_max_s": maximum,
        "dynamic_range_s": maximum - minimum,
        "dynamic_range_ratio": dynamic_range_ratio,
        "mean_abs_update_s": mean_abs_update,
        "median_abs_update_s": float(np.median(delta_abs)) if len(delta_abs) else math.nan,
        "update_cv": update_cv,
        "monotonicity": monotonicity,
        "linearity_nrmse": _linearity_nrmse(values),
        "linear_fit_r2": _r_squared(np.arange(len(values), dtype=float), values),
        "saturation_index": _saturation_index(delta_abs),
    }


def compute_branch_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute one transparent metric row per device/cycle/branch."""

    require_columns(df, [*BRANCH_KEYS, "pulse_index", "conductance_s"])
    validate_trace(df, strict=True)
    rows = [
        _branch_metric_row(key, group)
        for key, group in df.groupby(BRANCH_KEYS, sort=True, dropna=False)
    ]
    return pd.DataFrame(rows).sort_values(BRANCH_KEYS).reset_index(drop=True)


def _pair_asymmetry(branch_group: pd.DataFrame) -> float:
    lookup = branch_group.set_index("direction")["mean_abs_update_s"]
    if not {"potentiation", "depression"}.issubset(lookup.index):
        return math.nan
    potentiation = float(lookup.loc["potentiation"])
    depression = float(lookup.loc["depression"])
    return _safe_ratio(abs(potentiation - depression), potentiation + depression)


def compute_cycle_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate branch results into one row per device and cycle."""

    branch = compute_branch_metrics(df)
    rows: list[dict[str, object]] = []
    for key, group in branch.groupby(["device_id", "cycle"], sort=True):
        minimum = float(group["conductance_min_s"].min())
        maximum = float(group["conductance_max_s"].max())
        rows.append(
            {
                "device_id": key[0],
                "cycle": int(cast(int, key[1])),
                "conductance_min_s": minimum,
                "conductance_max_s": maximum,
                "window_s": maximum - minimum,
                "window_ratio": _safe_ratio(maximum, minimum),
                "update_asymmetry": _pair_asymmetry(group),
                "mean_linearity_nrmse": float(group["linearity_nrmse"].mean()),
                "mean_monotonicity": float(group["monotonicity"].mean()),
                "mean_update_cv": float(group["update_cv"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values(["device_id", "cycle"]).reset_index(drop=True)


def compute_endurance_summary(cycle_summary: pd.DataFrame) -> pd.DataFrame:
    """Estimate cycle-to-cycle window drift for each device."""

    require_columns(cycle_summary, ["device_id", "cycle", "window_s", "window_ratio"])
    rows: list[dict[str, object]] = []
    for device_id, group in cycle_summary.groupby("device_id", sort=True):
        group = group.sort_values("cycle")
        cycle = group["cycle"].to_numpy(dtype=float)
        window = group["window_s"].to_numpy(dtype=float)
        ratio = group["window_ratio"].to_numpy(dtype=float)

        if len(group) >= 2 and not np.allclose(cycle, cycle[0]):
            slope, _ = np.polyfit(cycle, window, deg=1)
            baseline = float(window[0])
            drift_per_100 = _safe_ratio(float(slope) * 100.0, baseline)
        else:
            drift_per_100 = math.nan

        rows.append(
            {
                "device_id": device_id,
                "cycle_count": int(len(group)),
                "initial_window_s": float(window[0]),
                "final_window_s": float(window[-1]),
                "initial_window_ratio": float(ratio[0]),
                "final_window_ratio": float(ratio[-1]),
                "fractional_window_drift_per_100_cycles": drift_per_100,
            }
        )
    return pd.DataFrame(rows)


def summarize_metrics(branch: pd.DataFrame, cycle: pd.DataFrame) -> dict[str, float | int]:
    """Create a compact JSON-serializable summary."""

    if branch.empty or cycle.empty:
        raise DataValidationError("cannot summarize empty metric tables")
    return {
        "device_count": int(branch["device_id"].nunique()),
        "cycle_count": int(cycle.shape[0]),
        "branch_count": int(branch.shape[0]),
        "median_window_ratio": float(cycle["window_ratio"].median()),
        "median_linearity_nrmse": float(branch["linearity_nrmse"].median()),
        "median_monotonicity": float(branch["monotonicity"].median()),
        "median_update_cv": float(branch["update_cv"].median()),
        "median_update_asymmetry": float(cycle["update_asymmetry"].median()),
    }
