"""Input/output helpers and pulse-table normalization."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .schema import OPTIONAL_NUMERIC_COLUMNS, DataValidationError, validate_trace

_DIRECTION_MAP = {
    "1": "potentiation",
    "+1": "potentiation",
    "pot": "potentiation",
    "potentiation": "potentiation",
    "up": "potentiation",
    "increase": "potentiation",
    "set": "potentiation",
    "ltp": "potentiation",
    "-1": "depression",
    "dep": "depression",
    "depression": "depression",
    "down": "depression",
    "decrease": "depression",
    "reset": "depression",
    "ltd": "depression",
}


def _normalize_direction_value(value: object) -> str:
    key = str(value).strip().lower()
    if key not in _DIRECTION_MAP:
        raise DataValidationError(f"unrecognized direction value: {value!r}")
    return _DIRECTION_MAP[key]


def normalize_trace(df: pd.DataFrame) -> pd.DataFrame:
    """Return a canonical, sorted copy of a pulse-update trace."""

    normalized = df.copy()
    if "direction" not in normalized.columns:
        raise DataValidationError("missing required column: direction")
    normalized["direction"] = normalized["direction"].map(_normalize_direction_value)

    numeric_columns = ["cycle", "pulse_index", "conductance_s", *OPTIONAL_NUMERIC_COLUMNS]
    for column in dict.fromkeys(numeric_columns):
        if column in normalized.columns:
            normalized[column] = pd.to_numeric(normalized[column], errors="coerce")

    sort_columns = [
        column
        for column in ("device_id", "cycle", "direction", "pulse_index")
        if column in normalized.columns
    ]
    normalized = normalized.sort_values(sort_columns, kind="stable").reset_index(drop=True)
    return normalized


def load_trace(path: str | Path, *, strict: bool = True) -> pd.DataFrame:
    """Load, normalize, and optionally validate a canonical CSV trace."""

    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(source)
    if source.suffix.lower() != ".csv":
        raise DataValidationError("v0.2 supports canonical CSV pulse-update tables only")
    trace = normalize_trace(pd.read_csv(source))
    validate_trace(trace, strict=strict)
    return trace


def save_trace(df: pd.DataFrame, path: str | Path) -> Path:
    """Normalize, validate, and save a canonical CSV trace."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    normalized = normalize_trace(df)
    validate_trace(normalized, strict=True)
    normalized.to_csv(destination, index=False)
    return destination
