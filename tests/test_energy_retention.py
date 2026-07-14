from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from memdevice_bench.energy import estimate_pulse_energy
from memdevice_bench.retention import fit_power_law_retention
from memdevice_bench.schema import DataValidationError
from memdevice_bench.synthetic import generate_synthetic_trace


def test_measured_energy_method_for_multiterminal_device() -> None:
    trace = generate_synthetic_trace(
        preset="ecram-tft-3t", cycles=1, pulses_per_branch=8
    )
    report = estimate_pulse_energy(trace, terminal_count=3)
    assert report.method == "measured_v_i_t"
    assert report.total_energy_j > 0
    assert (report.values_j > 0).all()


def test_estimated_energy_fallback_for_two_terminal_device() -> None:
    trace = generate_synthetic_trace(
        preset="rram-2t", cycles=1, pulses_per_branch=8
    ).drop(columns="pulse_current_a")
    report = estimate_pulse_energy(trace, terminal_count=2)
    assert report.method == "estimated_v2_g_read_t_assumes_two_terminal"
    assert report.total_energy_j > 0


def test_multiterminal_energy_without_program_current_is_rejected() -> None:
    trace = generate_synthetic_trace(
        preset="ecram-tft-3t", cycles=1, pulses_per_branch=8
    ).drop(columns="pulse_current_a")
    with pytest.raises(DataValidationError, match="multi-terminal DUT"):
        estimate_pulse_energy(trace, terminal_count=3)


def test_power_law_retention_fit_recovers_exponent() -> None:
    time = np.logspace(0, 4, 50)
    exponent = 0.035
    conductance = 100e-6 * (time / time[0]) ** (-exponent)
    frame = pd.DataFrame({"timestamp_s": time, "conductance_s": conductance})
    fit = fit_power_law_retention(frame)
    assert abs(fit.exponent_nu - exponent) < 1e-6
    assert fit.r_squared > 0.999999


def test_two_terminal_fallback_requires_explicit_topology() -> None:
    trace = generate_synthetic_trace(
        preset="rram-2t", cycles=1, pulses_per_branch=8
    ).drop(columns="pulse_current_a")
    with pytest.raises(DataValidationError, match="explicitly identifies a 2-terminal DUT"):
        estimate_pulse_energy(trace)
