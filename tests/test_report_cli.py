from __future__ import annotations

import json
from pathlib import Path

from memdevice_bench.cli import main


def test_cli_generate_validate_and_analyze(tmp_path: Path) -> None:
    trace_path = tmp_path / "trace.csv"
    metadata_path = tmp_path / "trace.metadata.json"
    report_dir = tmp_path / "report"

    assert (
        main(
            [
                "generate",
                "--preset",
                "ecram-tft-3t",
                "--output",
                str(trace_path),
                "--cycles",
                "2",
                "--pulses",
                "10",
            ]
        )
        == 0
    )
    assert trace_path.exists()
    assert metadata_path.exists()
    assert main(["validate-metadata", str(metadata_path)]) == 0
    assert main(["validate", str(trace_path), "--metadata", str(metadata_path)]) == 0
    assert (
        main(
            [
                "analyze",
                str(trace_path),
                "--metadata",
                str(metadata_path),
                "--output-dir",
                str(report_dir),
            ]
        )
        == 0
    )

    expected = {
        "summary.json",
        "validation.json",
        "metadata.normalized.json",
        "branch_metrics.csv",
        "cycle_summary.csv",
        "endurance_summary.csv",
        "trace_with_energy.csv",
        "overview.png",
    }
    assert expected.issubset({path.name for path in report_dir.iterdir()})
    summary = json.loads((report_dir / "summary.json").read_text())
    assert summary["device_count"] == 1
    assert summary["cycle_count"] == 2
    assert summary["terminal_count"] == 3
    assert summary["technology_tags"] == ["ecram"]
    assert "tft" in summary["platform_tags"]
    assert summary["topology_tag"] == "three-terminal"
    assert "ecram" in summary["all_tags"]


def test_cli_initializes_metadata_from_device_profile(tmp_path: Path) -> None:
    metadata_path = tmp_path / "fram.metadata.json"
    assert (
        main(
            [
                "init-metadata",
                "--template",
                "fram-capacitor-2t",
                "--device-id",
                "fe-cap-01",
                "--output",
                str(metadata_path),
                "--profile",
                "polarization",
            ]
        )
        == 0
    )
    payload = json.loads(metadata_path.read_text())
    assert payload["device"]["terminal_count"] == 2
    assert payload["device"]["technology_tags"] == ["fram"]
    assert "capacitor" in payload["device"]["platform_tags"]
    assert payload["experiment"]["profile"] == "polarization"


def test_cli_device_profiles_command(capsys) -> None:
    assert main(["device-profiles"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert "rram-2t" in payload
    assert "tft-generic-3t" in payload
    assert "dual-gate-memtransistor-4t" in payload
    assert payload["fram-capacitor-2t"]["topology_tag"] == "two-terminal"
