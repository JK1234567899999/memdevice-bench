"""Canonical pulse-update table schema and validation."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = (
    "device_id",
    "cycle",
    "pulse_index",
    "direction",
    "conductance_s",
)

OPTIONAL_NUMERIC_COLUMNS = (
    "pulse_voltage_v",
    "pulse_width_s",
    "pulse_current_a",
    "read_voltage_v",
    "read_current_a",
    "timestamp_s",
    "gate_voltage_v",
    "drain_voltage_v",
    "source_voltage_v",
    "body_voltage_v",
    "gate_current_a",
    "drain_current_a",
    "source_current_a",
    "body_current_a",
)

OPTIONAL_TEXT_COLUMNS = (
    "pulse_terminal",
    "read_terminal",
    "state_label",
)


class DataValidationError(ValueError):
    """Raised when a trace violates the canonical schema."""


@dataclass(frozen=True)
class ValidationReport:
    """Validation result with errors and non-fatal warnings."""

    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    row_count: int
    device_count: int
    cycle_count: int

    @property
    def valid(self) -> bool:
        """Return True when no errors were found."""

        return not self.errors

    def raise_for_errors(self) -> None:
        """Raise a single readable exception when validation failed."""

        if self.errors:
            raise DataValidationError("; ".join(self.errors))


def _all_finite(series: pd.Series) -> bool:
    numeric = pd.to_numeric(series, errors="coerce")
    return bool(np.isfinite(numeric.to_numpy(dtype=float)).all())


def _append_duplicate_key_errors(df: pd.DataFrame, errors: list[str]) -> None:
    keys = ["device_id", "cycle", "direction", "pulse_index"]
    duplicated = df.duplicated(keys, keep=False)
    if duplicated.any():
        errors.append(
            f"{int(duplicated.sum())} rows have duplicate "
            "(device_id, cycle, direction, pulse_index) keys"
        )


def _check_group_order(df: pd.DataFrame, warnings: list[str]) -> None:
    keys = ["device_id", "cycle", "direction"]
    for key, group in df.groupby(keys, sort=False, dropna=False):
        pulse_index = pd.to_numeric(group["pulse_index"], errors="coerce").to_numpy()
        if len(pulse_index) > 1 and np.any(np.diff(pulse_index) <= 0):
            warnings.append(f"pulse_index is not strictly increasing within branch {key}")


def _check_readout_consistency(df: pd.DataFrame, warnings: list[str]) -> None:
    required = {"read_voltage_v", "read_current_a", "conductance_s"}
    if not required.issubset(df.columns):
        return
    voltage = pd.to_numeric(df["read_voltage_v"], errors="coerce")
    current = pd.to_numeric(df["read_current_a"], errors="coerce")
    conductance = pd.to_numeric(df["conductance_s"], errors="coerce")
    mask = voltage.notna() & current.notna() & conductance.notna() & (voltage.abs() > 0)
    if int(mask.sum()) < 3:
        return
    inferred = current[mask].abs() / voltage[mask].abs()
    relative_error = (inferred - conductance[mask]).abs() / conductance[mask].abs()
    if float(relative_error.median()) > 0.1:
        warnings.append(
            "median |I_read/V_read - conductance_s| mismatch exceeds 10%; check sign, units, "
            "series resistance, or whether conductance_s represents a fitted small-signal quantity"
        )


def validate_trace(df: pd.DataFrame, *, strict: bool = False) -> ValidationReport:
    """Validate a canonical MemDeviceBench pulse-update trace.

    ``terminal_count`` and technology labels intentionally live in a JSON
    metadata sidecar. The same table schema can therefore be used for 2-, 3-,
    and 4-terminal devices while preserving topology-specific voltage/current
    columns when they are available.
    """

    errors: list[str] = []
    warnings: list[str] = []

    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        errors.append(f"missing required columns: {', '.join(missing)}")
        report = ValidationReport(
            errors=tuple(errors),
            warnings=tuple(warnings),
            row_count=len(df),
            device_count=0,
            cycle_count=0,
        )
        if strict:
            report.raise_for_errors()
        return report

    if df.empty:
        errors.append("trace is empty")

    if df[list(REQUIRED_COLUMNS)].isna().any().any():
        errors.append("required columns contain missing values")

    for column in ("cycle", "pulse_index", "conductance_s"):
        if not _all_finite(df[column]):
            errors.append(f"{column} contains non-numeric or non-finite values")

    for column in OPTIONAL_NUMERIC_COLUMNS:
        has_values = column in df.columns and df[column].notna().any()
        if has_values and not _all_finite(df[column].dropna()):
            errors.append(f"{column} contains non-numeric or non-finite values")

    cycle = pd.to_numeric(df["cycle"], errors="coerce")
    pulse_index = pd.to_numeric(df["pulse_index"], errors="coerce")
    conductance = pd.to_numeric(df["conductance_s"], errors="coerce")

    if cycle.notna().any() and ((cycle < 0) | (cycle % 1 != 0)).any():
        errors.append("cycle must contain non-negative integers")
    if pulse_index.notna().any() and ((pulse_index < 0) | (pulse_index % 1 != 0)).any():
        errors.append("pulse_index must contain non-negative integers")
    if conductance.notna().any() and (conductance <= 0).any():
        errors.append("conductance_s must be strictly positive")

    valid_directions = {"potentiation", "depression"}
    direction_values = set(df["direction"].astype(str).str.lower().unique())
    unknown = direction_values - valid_directions
    if unknown:
        errors.append(f"unknown normalized direction values: {sorted(unknown)}")

    if "pulse_width_s" in df.columns:
        width = pd.to_numeric(df["pulse_width_s"], errors="coerce")
        if width.notna().any() and (width.dropna() <= 0).any():
            errors.append("pulse_width_s must be positive where provided")

    if "timestamp_s" in df.columns:
        timestamp_keys = ["device_id", "cycle", "direction"]
        for key, group in df.groupby(timestamp_keys, sort=False, dropna=False):
            group = group.sort_values("pulse_index", kind="stable")
            timestamp = (
                pd.to_numeric(group["timestamp_s"], errors="coerce")
                .dropna()
                .to_numpy()
            )
            if len(timestamp) > 1 and np.any(np.diff(timestamp) < 0):
                warnings.append(f"timestamp_s decreases within branch {key}")

    for column in OPTIONAL_TEXT_COLUMNS:
        if column in df.columns and df[column].dropna().astype(str).str.strip().eq("").any():
            warnings.append(f"{column} contains blank strings")

    _append_duplicate_key_errors(df, errors)
    _check_group_order(df, warnings)
    _check_readout_consistency(df, warnings)

    group_sizes = df.groupby(["device_id", "cycle", "direction"], dropna=False).size()
    short_groups = int((group_sizes < 3).sum())
    if short_groups:
        warnings.append(f"{short_groups} branches contain fewer than three states")

    if "pulse_current_a" not in df.columns:
        warnings.append(
            "pulse_current_a is absent; programming energy cannot be measured directly. "
            "A V²G_readt fallback is only defensible for an explicitly 2-terminal DUT."
        )

    report = ValidationReport(
        errors=tuple(dict.fromkeys(errors)),
        warnings=tuple(dict.fromkeys(warnings)),
        row_count=len(df),
        device_count=int(df["device_id"].nunique(dropna=True)),
        cycle_count=int(df[["device_id", "cycle"]].drop_duplicates().shape[0]),
    )
    if strict:
        report.raise_for_errors()
    return report


def require_columns(df: pd.DataFrame, columns: Iterable[str]) -> None:
    """Raise a validation error when any requested column is absent."""

    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise DataValidationError(f"missing required columns: {', '.join(missing)}")
