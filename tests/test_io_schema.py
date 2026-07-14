from __future__ import annotations

import pandas as pd
import pytest

from memdevice_bench.io import normalize_trace
from memdevice_bench.schema import DataValidationError, validate_trace
from memdevice_bench.synthetic import generate_synthetic_trace


def test_synthetic_three_terminal_trace_is_valid() -> None:
    trace = generate_synthetic_trace(
        preset="ecram-tft-3t", cycles=2, pulses_per_branch=12
    )
    report = validate_trace(trace)
    assert report.valid
    assert report.row_count == 48
    assert report.device_count == 1
    assert report.cycle_count == 2
    assert {"gate_voltage_v", "drain_current_a"}.issubset(trace.columns)


def test_synthetic_four_terminal_trace_is_valid() -> None:
    trace = generate_synthetic_trace(
        preset="memtransistor-4t", cycles=1, pulses_per_branch=6
    )
    report = validate_trace(trace)
    assert report.valid
    assert {"body_voltage_v", "body_current_a"}.issubset(trace.columns)


def test_direction_aliases_are_normalized() -> None:
    frame = pd.DataFrame(
        {
            "device_id": ["d"] * 6,
            "cycle": [0] * 6,
            "pulse_index": [0, 1, 2, 0, 1, 2],
            "direction": ["SET", "set", "LTP", "RESET", "reset", "LTD"],
            "conductance_s": [1e-6, 2e-6, 3e-6, 3e-6, 2e-6, 1e-6],
        }
    )
    normalized = normalize_trace(frame)
    assert set(normalized["direction"]) == {"potentiation", "depression"}


def test_nonpositive_conductance_fails() -> None:
    trace = generate_synthetic_trace(
        preset="rram-2t", cycles=1, pulses_per_branch=5
    )
    trace.loc[0, "conductance_s"] = 0.0
    with pytest.raises(DataValidationError, match="strictly positive"):
        validate_trace(trace, strict=True)
