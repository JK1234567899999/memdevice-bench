"""End-to-end pulse-update analysis composition."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from .energy import EnergyReport, check_programming_path_consistency, estimate_pulse_energy
from .io import normalize_trace
from .metadata import DatasetMetadata, metadata_summary, normalize_metadata, validate_metadata
from .metrics import (
    compute_branch_metrics,
    compute_cycle_summary,
    compute_endurance_summary,
    summarize_metrics,
)
from .schema import DataValidationError, ValidationReport, validate_trace


@dataclass(frozen=True)
class AnalysisReport:
    """Structured result of a complete pulse-update analysis."""

    trace: pd.DataFrame
    validation: ValidationReport
    branch_metrics: pd.DataFrame
    cycle_summary: pd.DataFrame
    endurance_summary: pd.DataFrame
    energy: EnergyReport | None
    metadata: DatasetMetadata | None
    notes: tuple[str, ...]
    summary: dict[str, Any]


def analyze_trace(
    df: pd.DataFrame,
    *,
    metadata: DatasetMetadata | None = None,
) -> AnalysisReport:
    """Normalize, validate, and analyze a pulse-update trace.

    Metadata is optional for legacy tables, but providing it enables topology-
    aware energy handling and makes technology/platform tags part of the report.
    """

    trace = normalize_trace(df)
    validation = validate_trace(trace, strict=True)
    branch = compute_branch_metrics(trace)
    cycle = compute_cycle_summary(trace)
    endurance = compute_endurance_summary(cycle)
    summary: dict[str, Any] = dict(summarize_metrics(branch, cycle))
    notes: list[str] = list(validation.warnings)

    normalized_metadata: DatasetMetadata | None = None
    terminal_count: int | None = None
    if metadata is not None:
        normalized_metadata = normalize_metadata(metadata)
        metadata_report = validate_metadata(normalized_metadata, strict=True)
        notes.extend(metadata_report.warnings)
        terminal_count = normalized_metadata.device.terminal_count
        summary.update(metadata_summary(normalized_metadata))
        notes.extend(check_programming_path_consistency(trace, terminal_count=terminal_count))

        table_device_ids = set(trace["device_id"].astype(str).unique())
        if normalized_metadata.device.device_id not in table_device_ids:
            raise DataValidationError(
                "metadata device_id does not match any device_id in the pulse table"
            )

    energy: EnergyReport | None = None
    if {"pulse_voltage_v", "pulse_width_s"}.issubset(trace.columns):
        try:
            energy = estimate_pulse_energy(trace, terminal_count=terminal_count)
        except DataValidationError as exc:
            notes.append(str(exc))
            summary.update(
                {
                    "energy_status": "not_computed",
                    "energy_note": str(exc),
                }
            )
        else:
            summary.update(
                {
                    "energy_status": "computed",
                    "energy_method": energy.method,
                    "energy_note": energy.note,
                    "total_programming_energy_j": energy.total_energy_j,
                    "median_pulse_energy_j": energy.median_energy_j,
                }
            )

    return AnalysisReport(
        trace=trace,
        validation=validation,
        branch_metrics=branch,
        cycle_summary=cycle,
        endurance_summary=endurance,
        energy=energy,
        metadata=normalized_metadata,
        notes=tuple(dict.fromkeys(notes)),
        summary=summary,
    )
