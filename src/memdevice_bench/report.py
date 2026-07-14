"""Filesystem report generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from .analysis import AnalysisReport, analyze_trace
from .metadata import DatasetMetadata, metadata_to_dict


def _json_default(value: Any) -> Any:
    if hasattr(value, "item"):
        return value.item()
    raise TypeError(f"cannot serialize {type(value)!r}")


def _plot_overview(report: AnalysisReport, destination: Path) -> None:
    figure, axis = plt.subplots(figsize=(9, 5.5))
    trace = report.trace.copy()

    for (device_id, cycle, direction), group in trace.groupby(
        ["device_id", "cycle", "direction"], sort=True
    ):
        group = group.sort_values("pulse_index")
        label = f"{device_id} | cycle {cycle} | {direction}"
        axis.plot(group["pulse_index"], group["conductance_s"] * 1e6, label=label)

    axis.set_xlabel("Pulse index within branch")
    axis.set_ylabel("Read conductance (µS)")
    title = "Pulse-by-pulse conductance update"
    if report.metadata is not None:
        tags = ", ".join(report.metadata.device.technology_tags)
        title += f" | {report.metadata.device.terminal_count}T | {tags}"
    axis.set_title(title)
    axis.grid(True, alpha=0.25)
    if trace.groupby(["device_id", "cycle", "direction"]).ngroups <= 12:
        axis.legend(fontsize=7, ncol=2)
    figure.tight_layout()
    figure.savefig(destination, dpi=180)
    plt.close(figure)


def write_report(
    df: pd.DataFrame,
    output_dir: str | Path,
    *,
    metadata: DatasetMetadata | None = None,
) -> AnalysisReport:
    """Analyze a trace and write JSON, CSV, and PNG artifacts."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    report = analyze_trace(df, metadata=metadata)

    (destination / "summary.json").write_text(
        json.dumps(report.summary, indent=2, sort_keys=True, default=_json_default) + "\n",
        encoding="utf-8",
    )
    (destination / "validation.json").write_text(
        json.dumps(
            {
                "valid": report.validation.valid,
                "errors": report.validation.errors,
                "warnings": report.validation.warnings,
                "analysis_notes": report.notes,
                "row_count": report.validation.row_count,
                "device_count": report.validation.device_count,
                "cycle_count": report.validation.cycle_count,
            },
            indent=2,
            default=_json_default,
        )
        + "\n",
        encoding="utf-8",
    )
    if report.metadata is not None:
        (destination / "metadata.normalized.json").write_text(
            json.dumps(metadata_to_dict(report.metadata), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    report.branch_metrics.to_csv(destination / "branch_metrics.csv", index=False)
    report.cycle_summary.to_csv(destination / "cycle_summary.csv", index=False)
    report.endurance_summary.to_csv(destination / "endurance_summary.csv", index=False)
    if report.energy is not None:
        report.trace.assign(pulse_energy_j=report.energy.values_j).to_csv(
            destination / "trace_with_energy.csv", index=False
        )
    _plot_overview(report, destination / "overview.png")
    return report
