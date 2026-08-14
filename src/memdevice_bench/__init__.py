"""Public API for MemDeviceBench.

Public symbols are imported on demand so a focused task, such as metadata
validation, does not eagerly import the numerical and plotting stack.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS: dict[str, tuple[str, str]] = {
    "AnalysisReport": ("analysis", "AnalysisReport"),
    "DEVICE_PROFILE_TEMPLATES": ("device_profiles", "DEVICE_PROFILE_TEMPLATES"),
    "DataValidationError": ("schema", "DataValidationError"),
    "DatasetMetadata": ("metadata", "DatasetMetadata"),
    "DeviceMetadata": ("metadata", "DeviceMetadata"),
    "DeviceProfileTemplate": ("device_profiles", "DeviceProfileTemplate"),
    "EnergyReport": ("energy", "EnergyReport"),
    "ExperimentMetadata": ("metadata", "ExperimentMetadata"),
    "MetadataValidationError": ("metadata", "MetadataValidationError"),
    "MetadataValidationReport": ("metadata", "MetadataValidationReport"),
    "RetentionFit": ("retention", "RetentionFit"),
    "SYNTHETIC_PRESETS": ("synthetic", "SYNTHETIC_PRESETS"),
    "TAG_VOCABULARY": ("taxonomy", "TAG_VOCABULARY"),
    "ValidationReport": ("schema", "ValidationReport"),
    "analyze_trace": ("analysis", "analyze_trace"),
    "available_device_profiles": ("device_profiles", "available_device_profiles"),
    "available_presets": ("synthetic", "available_presets"),
    "check_programming_path_consistency": ("energy", "check_programming_path_consistency"),
    "compute_branch_metrics": ("metrics", "compute_branch_metrics"),
    "compute_cycle_summary": ("metrics", "compute_cycle_summary"),
    "device_profiles_as_dict": ("device_profiles", "device_profiles_as_dict"),
    "estimate_pulse_energy": ("energy", "estimate_pulse_energy"),
    "fit_power_law_retention": ("retention", "fit_power_law_retention"),
    "generate_synthetic_trace": ("synthetic", "generate_synthetic_trace"),
    "load_metadata": ("metadata", "load_metadata"),
    "load_trace": ("io", "load_trace"),
    "metadata_for_device_profile": ("device_profiles", "metadata_for_device_profile"),
    "metadata_for_preset": ("synthetic", "metadata_for_preset"),
    "metadata_summary": ("metadata", "metadata_summary"),
    "normalize_tag": ("taxonomy", "normalize_tag"),
    "normalize_tags": ("taxonomy", "normalize_tags"),
    "normalize_trace": ("io", "normalize_trace"),
    "save_metadata": ("metadata", "save_metadata"),
    "save_trace": ("io", "save_trace"),
    "validate_metadata": ("metadata", "validate_metadata"),
    "validate_trace": ("schema", "validate_trace"),
    "vocabulary_as_dict": ("taxonomy", "vocabulary_as_dict"),
}

__all__ = list(_EXPORTS)

__version__ = "0.2.0"


def __getattr__(name: str) -> Any:
    """Import a public symbol only when it is requested."""

    try:
        module_name, symbol_name = _EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
    value = getattr(import_module(f"{__name__}.{module_name}"), symbol_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    """Expose deferred public symbols to interactive tools."""

    return sorted({*globals(), *_EXPORTS})
