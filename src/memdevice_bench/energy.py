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
