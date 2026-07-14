from __future__ import annotations

import numpy as np

from memdevice_bench.metrics import (
    compute_branch_metrics,
    compute_cycle_summary,
    compute_endurance_summary,
)
from memdevice_bench.synthetic import generate_synthetic_trace


def test_branch_metrics_are_physically_consistent() -> None:
    trace = generate_synthetic_trace(
        preset="rram-2t", cycles=2, pulses_per_branch=32, noise_fraction=0.001
    )
    metrics = compute_branch_metrics(trace)
    assert len(metrics) == 4
    assert (metrics["dynamic_range_ratio"] > 1).all()
    assert (metrics["monotonicity"] > 0.95).all()
    assert (metrics["linearity_nrmse"] >= 0).all()
    assert np.isfinite(metrics["update_cv"]).all()


def test_cycle_and_endurance_summary() -> None:
    trace = generate_synthetic_trace(
        preset="pcm-pram-2t", cycles=4, pulses_per_branch=16
    )
    cycle = compute_cycle_summary(trace)
    endurance = compute_endurance_summary(cycle)
    assert len(cycle) == 4
    assert len(endurance) == 1
    assert 0 <= cycle["update_asymmetry"].median() < 1
    assert endurance.loc[0, "cycle_count"] == 4
    assert np.isfinite(endurance.loc[0, "fractional_window_drift_per_100_cycles"])
