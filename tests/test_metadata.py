from __future__ import annotations

from pathlib import Path

import pytest

from memdevice_bench.analysis import analyze_trace
from memdevice_bench.metadata import (
    DatasetMetadata,
    DeviceMetadata,
    MetadataValidationError,
    load_metadata,
    normalize_metadata,
    save_metadata,
    validate_metadata,
)
from memdevice_bench.schema import DataValidationError
from memdevice_bench.synthetic import generate_synthetic_trace, metadata_for_preset
from memdevice_bench.taxonomy import normalize_tag


def test_aliases_and_terminal_tag_are_normalized() -> None:
    metadata = DatasetMetadata(
        device=DeviceMetadata(
            device_id="d1",
            terminal_count=3,
            technology_tags=("electrochemical-ram",),
            platform_tags=("thin-film-transistor",),
            mechanism_tags=("ionic",),
            material_tags=("2d",),
            behavior_tags=("multi-level", "non-volatile"),
        )
    )
    normalized = normalize_metadata(metadata)
    assert normalized.device.technology_tags == ("ecram",)
    assert {"tft", "three-terminal"}.issubset(normalized.device.platform_tags)
    assert normalized.device.mechanism_tags == ("ion-insertion",)
    assert normalize_tag("technology", "ReRAM") == "rram"


def test_conflicting_terminal_tag_is_invalid() -> None:
    metadata = DatasetMetadata(
        device=DeviceMetadata(
            device_id="d1",
            terminal_count=3,
            technology_tags=("ecram",),
            platform_tags=("two-terminal", "tft"),
        )
    )
    report = validate_metadata(metadata)
    assert not report.valid
    assert any("conflicts" in error for error in report.errors)
    with pytest.raises(MetadataValidationError):
        validate_metadata(metadata, strict=True)


def test_metadata_roundtrip(tmp_path: Path) -> None:
    source = metadata_for_preset("fefet-tft-3t", device_id="fe-1")
    path = save_metadata(source, tmp_path / "fe-1.metadata.json")
    loaded = load_metadata(path)
    assert loaded == source
    assert "three-terminal" in loaded.device.platform_tags


def test_metadata_device_id_must_match_trace() -> None:
    trace = generate_synthetic_trace(
        preset="rram-2t", device_id="trace-device", cycles=1, pulses_per_branch=5
    )
    metadata = metadata_for_preset("rram-2t", device_id="other-device")
    with pytest.raises(DataValidationError, match="does not match"):
        analyze_trace(trace, metadata=metadata)


def test_analysis_skips_invalid_multiterminal_fallback() -> None:
    trace = generate_synthetic_trace(
        preset="ecram-tft-3t", cycles=1, pulses_per_branch=5
    ).drop(columns="pulse_current_a")
    metadata = metadata_for_preset("ecram-tft-3t")
    report = analyze_trace(trace, metadata=metadata)
    assert report.energy is None
    assert report.summary["energy_status"] == "not_computed"


def test_common_device_profile_templates_keep_axes_separate() -> None:
    from memdevice_bench.device_profiles import metadata_for_device_profile

    metadata = metadata_for_device_profile(
        "ecram-tft-3t", device_id="e-1", experiment_profile="retention"
    )
    assert metadata.device.terminal_count == 3
    assert metadata.device.technology_tags == ("ecram",)
    assert {"tft", "transistor", "three-terminal"}.issubset(
        metadata.device.platform_tags
    )
    assert "ecram" not in metadata.device.platform_tags
    assert metadata.experiment.profile == "retention"


def test_electrolyte_gated_transistor_is_not_collapsed_into_oect() -> None:
    assert normalize_tag("platform", "electrolyte-gated-fet") == (
        "electrolyte-gated-transistor"
    )
    assert normalize_tag("platform", "organic-electrochemical-transistor") == "oect"
