"""Deterministic synthetic pulse traces and tagged device presets.

The generator is intended for software tests and tutorials. It is not a
compact physical model of any listed memory technology.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .metadata import DatasetMetadata, DeviceMetadata, ExperimentMetadata, normalize_metadata


@dataclass(frozen=True)
class SyntheticPreset:
    """Metadata and numerical defaults for a tutorial dataset."""

    terminal_count: int
    technology_tags: tuple[str, ...]
    platform_tags: tuple[str, ...]
    mechanism_tags: tuple[str, ...]
    material_tags: tuple[str, ...]
    behavior_tags: tuple[str, ...]
    g_min_s: float
    g_max_s: float
    pulse_voltage_v: float
    pulse_width_s: float
    programming_current_a: float | None


SYNTHETIC_PRESETS: dict[str, SyntheticPreset] = {
    "rram-2t": SyntheticPreset(
        terminal_count=2,
        technology_tags=("rram",),
        platform_tags=("resistor", "crossbar"),
        mechanism_tags=("filamentary", "valence-change"),
        material_tags=("oxide", "metal-oxide"),
        behavior_tags=("analog", "multilevel", "nonvolatile", "bipolar"),
        g_min_s=10e-6,
        g_max_s=120e-6,
        pulse_voltage_v=1.2,
        pulse_width_s=1e-6,
        programming_current_a=None,
    ),
    "pcm-pram-2t": SyntheticPreset(
        terminal_count=2,
        technology_tags=("pcm", "pram"),
        platform_tags=("resistor",),
        mechanism_tags=("phase-change", "thermal"),
        material_tags=("chalcogenide",),
        behavior_tags=("analog", "multilevel", "nonvolatile"),
        g_min_s=4e-6,
        g_max_s=80e-6,
        pulse_voltage_v=1.8,
        pulse_width_s=50e-9,
        programming_current_a=None,
    ),
    "cbram-2t": SyntheticPreset(
        terminal_count=2,
        technology_tags=("cbram",),
        platform_tags=("resistor", "crossbar"),
        mechanism_tags=("filamentary", "electrochemical-metallization"),
        material_tags=("solid-electrolyte",),
        behavior_tags=("analog", "multilevel", "nonvolatile", "bipolar"),
        g_min_s=6e-6,
        g_max_s=150e-6,
        pulse_voltage_v=0.8,
        pulse_width_s=5e-6,
        programming_current_a=None,
    ),
    "ecram-tft-3t": SyntheticPreset(
        terminal_count=3,
        technology_tags=("ecram",),
        platform_tags=("transistor", "tft"),
        mechanism_tags=("electrochemical", "ion-insertion", "redox"),
        material_tags=("oxide", "electrolyte"),
        behavior_tags=("analog", "multilevel", "nonvolatile", "potentiation-depression"),
        g_min_s=15e-6,
        g_max_s=180e-6,
        pulse_voltage_v=1.0,
        pulse_width_s=1e-3,
        programming_current_a=120e-9,
    ),
    "fefet-tft-3t": SyntheticPreset(
        terminal_count=3,
        technology_tags=("fefet",),
        platform_tags=("transistor", "tft"),
        mechanism_tags=("ferroelectric",),
        material_tags=("ferroelectric-oxide",),
        behavior_tags=("analog", "multilevel", "nonvolatile"),
        g_min_s=8e-6,
        g_max_s=140e-6,
        pulse_voltage_v=3.0,
        pulse_width_s=1e-6,
        programming_current_a=20e-9,
    ),
    "memtransistor-4t": SyntheticPreset(
        terminal_count=4,
        technology_tags=("memtransistor", "charge-trap-memory"),
        platform_tags=("transistor", "tft"),
        mechanism_tags=("charge-trap", "interfacial-barrier"),
        material_tags=("oxide", "two-dimensional"),
        behavior_tags=("analog", "multilevel", "nonvolatile", "synaptic"),
        g_min_s=2e-6,
        g_max_s=70e-6,
        pulse_voltage_v=4.0,
        pulse_width_s=10e-3,
        programming_current_a=5e-9,
    ),
}


def available_presets() -> tuple[str, ...]:
    """Return sorted names accepted by the synthetic generator."""

    return tuple(sorted(SYNTHETIC_PRESETS))


def metadata_for_preset(
    preset: str,
    *,
    device_id: str = "synthetic-001",
    instrument: str = "synthetic-generator",
) -> DatasetMetadata:
    """Return normalized metadata for a named synthetic preset."""

    if preset not in SYNTHETIC_PRESETS:
        raise ValueError(f"unknown preset {preset!r}; choose from {available_presets()}")
    spec = SYNTHETIC_PRESETS[preset]
    return normalize_metadata(
        DatasetMetadata(
            device=DeviceMetadata(
                device_id=device_id,
                terminal_count=spec.terminal_count,
                technology_tags=spec.technology_tags,
                platform_tags=spec.platform_tags,
                mechanism_tags=spec.mechanism_tags,
                material_tags=spec.material_tags,
                behavior_tags=spec.behavior_tags,
                custom_tags=("synthetic", "tutorial"),
                notes=(
                    "Synthetic software-test dataset. Numerical trajectories are not a compact "
                    "physical model of the tagged technology."
                ),
            ),
            experiment=ExperimentMetadata(
                profile="pulse-update",
                instrument=instrument,
                source_format="generated-canonical-csv",
                temperature_k=300.0,
                notes="Bidirectional pulse-update tutorial trace.",
            ),
            license="CC0-1.0",
        )
    )


def _trajectory(start: float, stop: float, count: int, curvature: float) -> np.ndarray:
    x = np.linspace(0.0, 1.0, count)
    progress = x if abs(curvature) < 1e-12 else np.expm1(curvature * x) / np.expm1(curvature)
    return start + (stop - start) * progress


def generate_synthetic_trace(
    *,
    preset: str = "rram-2t",
    device_id: str = "synthetic-001",
    cycles: int = 3,
    pulses_per_branch: int = 64,
    g_min_s: float | None = None,
    g_max_s: float | None = None,
    potentiation_curvature: float = 1.0,
    depression_curvature: float = 0.7,
    noise_fraction: float = 0.003,
    pulse_voltage_v: float | None = None,
    pulse_width_s: float | None = None,
    seed: int = 7,
) -> pd.DataFrame:
    """Generate a reproducible tagged-device pulse-update trace.

    Terminal-specific columns are added for 3- and 4-terminal presets. The
    output contains generic ``pulse_voltage_v`` and ``pulse_current_a``
    columns so that the programming path is explicit in software tests.
    """

    if preset not in SYNTHETIC_PRESETS:
        raise ValueError(f"unknown preset {preset!r}; choose from {available_presets()}")
    spec = SYNTHETIC_PRESETS[preset]
    g_min = spec.g_min_s if g_min_s is None else g_min_s
    g_max = spec.g_max_s if g_max_s is None else g_max_s
    pulse_voltage = spec.pulse_voltage_v if pulse_voltage_v is None else pulse_voltage_v
    pulse_width = spec.pulse_width_s if pulse_width_s is None else pulse_width_s

    if cycles < 1:
        raise ValueError("cycles must be >= 1")
    if pulses_per_branch < 3:
        raise ValueError("pulses_per_branch must be >= 3")
    if not (0 < g_min < g_max):
        raise ValueError("require 0 < g_min_s < g_max_s")
    if noise_fraction < 0:
        raise ValueError("noise_fraction must be non-negative")
    if pulse_width <= 0:
        raise ValueError("pulse_width_s must be positive")

    rng = np.random.default_rng(seed)
    rows: list[dict[str, object]] = []
    timestamp = 0.0
    read_voltage = 0.1

    for cycle in range(cycles):
        window_scale = 1.0 - 0.004 * cycle
        cycle_min = g_min * (1.0 + 0.002 * cycle)
        cycle_max = g_min + (g_max - g_min) * window_scale

        branch_specs = (
            ("potentiation", cycle_min, cycle_max, potentiation_curvature, abs(pulse_voltage)),
            ("depression", cycle_max, cycle_min, depression_curvature, -abs(pulse_voltage)),
        )
        for direction, start, stop, curvature, voltage in branch_specs:
            ideal = _trajectory(start, stop, pulses_per_branch, curvature)
            noise = rng.normal(0.0, noise_fraction * (g_max - g_min), pulses_per_branch)
            measured = np.maximum(ideal + noise, np.finfo(float).tiny)

            if direction == "potentiation":
                measured = np.maximum.accumulate(measured)
            else:
                measured = np.minimum.accumulate(measured)

            for pulse_index, conductance in enumerate(measured):
                timestamp += pulse_width + 1e-3
                if spec.terminal_count == 2:
                    program_current = voltage * conductance
                    pulse_terminal = "terminal-1-to-terminal-2"
                    read_terminal = "terminal-1-to-terminal-2"
                else:
                    nominal_current = spec.programming_current_a or 100e-9
                    variability = 1.0 + 0.08 * np.sin(2 * np.pi * pulse_index / pulses_per_branch)
                    program_current = np.sign(voltage) * nominal_current * variability
                    pulse_terminal = "gate-to-source"
                    read_terminal = "drain-to-source"

                row: dict[str, object] = {
                    "device_id": device_id,
                    "cycle": cycle,
                    "pulse_index": pulse_index,
                    "direction": direction,
                    "conductance_s": float(conductance),
                    "pulse_voltage_v": float(voltage),
                    "pulse_width_s": float(pulse_width),
                    "pulse_current_a": float(program_current),
                    "read_voltage_v": read_voltage,
                    "read_current_a": float(read_voltage * conductance),
                    "timestamp_s": timestamp,
                    "pulse_terminal": pulse_terminal,
                    "read_terminal": read_terminal,
                }
                if spec.terminal_count >= 3:
                    row.update(
                        {
                            "gate_voltage_v": float(voltage),
                            "gate_current_a": float(program_current),
                            "drain_voltage_v": read_voltage,
                            "drain_current_a": float(read_voltage * conductance),
                            "source_voltage_v": 0.0,
                            "source_current_a": float(-read_voltage * conductance),
                        }
                    )
                if spec.terminal_count >= 4:
                    row.update({"body_voltage_v": 0.0, "body_current_a": 0.0})
                rows.append(row)

    return pd.DataFrame(rows)
