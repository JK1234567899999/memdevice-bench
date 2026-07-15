"""Programming-energy estimation with topology-aware provenance."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .schema import DataValidationError, require_columns


@dataclass(frozen=True)
class EnergyReport:
    """Per-row energy and aggregate metadata."""

    values_j: pd.Series
    method: str
    total_energy_j: float
    median_energy_j: float
    note: str


_TERMINAL_CURRENT_COLUMNS = {
    "gate": "gate_current_a",
    "drain": "drain_current_a",
    "source": "source_current_a",
    "body": "body_current_a",
    "back-gate": "body_current_a",
    "backgate": "body_current_a",
}


def _current_column_for_terminal_path(value: object) -> str | None:
    """Infer a terminal-resolved current column from a path label when possible."""

    label = str(value).strip().lower()
    for terminal, column in _TERMINAL_CURRENT_COLUMNS.items():
        if label.startswith(terminal):
            return column
    return None


def _median_relative_difference(reference: np.ndarray, observed: np.ndarray) -> float:
    """Return a stable median difference between current magnitudes."""

    denominator = np.maximum(np.abs(reference), np.finfo(float).tiny)
    return float(np.median(np.abs(np.abs(observed) - np.abs(reference)) / denominator))


def check_programming_path_consistency(
    df: pd.DataFrame,
    *,
    terminal_count: int | None,
) -> tuple[str, ...]:
    """Return non-fatal warnings about multi-terminal programming-current provenance.

    The check is deliberately conservative: it only compares a generic
    ``pulse_current_a`` value with terminal-resolved currents when the declared
    ``pulse_terminal`` identifies the corresponding terminal. It does not infer
    device physics from a technology tag or reject a valid but unusual wiring
    scheme; users should document such schemes in metadata notes.
    """

    if terminal_count is None or terminal_count < 3 or "pulse_current_a" not in df.columns:
        return ()

    program_current = pd.to_numeric(df["pulse_current_a"], errors="coerce")
    finite_program = np.isfinite(program_current.to_numpy(dtype=float))
    if not finite_program.any():
        return ()

    warnings: list[str] = []
    if "pulse_terminal" not in df.columns:
        return (
            "multi-terminal trace provides pulse_current_a without pulse_terminal; "
            "cannot verify that it is a programming-path current",
        )

    pulse_terminal = df["pulse_terminal"].fillna("").astype(str).str.strip().str.lower()
    labeled_program = finite_program & pulse_terminal.ne("").to_numpy()
    unlabeled_count = int(finite_program.sum() - labeled_program.sum())
    if unlabeled_count:
        warnings.append(
            f"{unlabeled_count} multi-terminal rows provide pulse_current_a without a "
            "pulse_terminal label; their programming path cannot be checked"
        )

    if "read_terminal" not in df.columns:
        warnings.append(
            "multi-terminal trace has no read_terminal labels; programming and read paths "
            "cannot be distinguished"
        )
    else:
        read_terminal = df["read_terminal"].fillna("").astype(str).str.strip().str.lower()
        comparable_paths = labeled_program & read_terminal.ne("").to_numpy()
        same_path = pulse_terminal.eq(read_terminal).to_numpy() & comparable_paths
        same_path_count = int(same_path.sum())
        if same_path_count:
            warnings.append(
                f"{same_path_count} multi-terminal rows use the same pulse_terminal and "
                "read_terminal; verify that pulse_current_a is not a read-path current"
            )

    program_values = program_current.to_numpy(dtype=float)
    for current_column in sorted(set(_TERMINAL_CURRENT_COLUMNS.values())):
        if current_column not in df.columns:
            continue
        matching_terminal = np.array(
            [
                _current_column_for_terminal_path(value) == current_column
                for value in pulse_terminal
            ],
            dtype=bool,
        )
        terminal_current = pd.to_numeric(df[current_column], errors="coerce").to_numpy(dtype=float)
        mask = matching_terminal & finite_program & np.isfinite(terminal_current)
        if int(mask.sum()) < 3:
            continue
        mismatch = _median_relative_difference(terminal_current[mask], program_values[mask])
        if mismatch > 0.1:
            warnings.append(
                f"pulse_current_a differs from {current_column} on {int(mask.sum())} "
                f"programming-path rows (median relative mismatch {mismatch:.1%}); "
                "verify the programming-current mapping"
            )

    if {
        "read_current_a",
        "pulse_terminal",
        "read_terminal",
    }.issubset(df.columns):
        read_current = pd.to_numeric(df["read_current_a"], errors="coerce").to_numpy(dtype=float)
        different_paths = pulse_terminal.ne(read_terminal).to_numpy()
        mask = finite_program & np.isfinite(read_current) & labeled_program & different_paths
        if int(mask.sum()) >= 3:
            mismatch = _median_relative_difference(read_current[mask], program_values[mask])
            if mismatch <= 0.01:
                warnings.append(
                    "pulse_current_a closely matches read_current_a while programming and read "
                    "terminal paths differ; verify that a channel read current was not supplied "
                    "as programming current"
                )

    return tuple(dict.fromkeys(warnings))


def estimate_pulse_energy(
    df: pd.DataFrame,
    *,
    terminal_count: int | None = None,
) -> EnergyReport:
    """Estimate programming-pulse energy with explicit physical assumptions.

    Preferred method
    ----------------
    If ``pulse_current_a`` is complete, energy is ``abs(V_pulse I_pulse t)``.
    ``pulse_current_a`` must refer to current in the programming terminal/path.

    Two-terminal fallback
    ---------------------
    If programming current is unavailable, ``V_pulse**2 G_read t`` is allowed
    only when ``terminal_count`` is explicitly 2. This fallback
    assumes the read conductance approximates conductance during the program
    pulse. It is not used for a known 3- or 4-terminal device because channel
    conductance generally does not determine gate/electrolyte programming
    current.
    """

    require_columns(df, ["pulse_voltage_v", "pulse_width_s"])
    voltage = pd.to_numeric(df["pulse_voltage_v"], errors="coerce")
    width = pd.to_numeric(df["pulse_width_s"], errors="coerce")

    if voltage.isna().any() or width.isna().any():
        raise DataValidationError("pulse_voltage_v and pulse_width_s must be complete")
    if (width <= 0).any():
        raise DataValidationError("pulse_width_s must be positive")
    if terminal_count is not None and terminal_count < 2:
        raise DataValidationError("terminal_count must be >= 2")

    if "pulse_current_a" in df.columns and df["pulse_current_a"].notna().all():
        current = pd.to_numeric(df["pulse_current_a"], errors="coerce")
        if current.isna().any():
            raise DataValidationError("pulse_current_a contains non-numeric values")
        values = (voltage * current * width).abs()
        method = "measured_v_i_t"
        note = "Uses measured current in the programming path."
    else:
        if terminal_count != 2:
            raise DataValidationError(
                "programming energy was not computed: V²G_readt fallback requires metadata "
                "that explicitly identifies a 2-terminal DUT; a multi-terminal DUT or "
                "unknown topology requires measured programming-path current"
            )
        require_columns(df, ["conductance_s"])
        conductance = pd.to_numeric(df["conductance_s"], errors="coerce")
        if conductance.isna().any() or (conductance <= 0).any():
            raise DataValidationError("conductance_s must be positive and complete")
        values = voltage.pow(2) * conductance * width
        method = "estimated_v2_g_read_t_assumes_two_terminal"
        note = (
            "Fallback assumes a 2-terminal DUT and uses read conductance as the program-pulse "
            "conductance; switching transients and compliance behavior are not captured."
        )

    values = pd.Series(np.asarray(values, dtype=float), index=df.index, name="pulse_energy_j")
    return EnergyReport(
        values_j=values,
        method=method,
        total_energy_j=float(values.sum()),
        median_energy_j=float(values.median()),
        note=note,
    )
