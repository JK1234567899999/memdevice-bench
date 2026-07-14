"""Public API for MemDeviceBench."""

from .analysis import AnalysisReport, analyze_trace
from .device_profiles import (
    DEVICE_PROFILE_TEMPLATES,
    DeviceProfileTemplate,
    available_device_profiles,
    device_profiles_as_dict,
    metadata_for_device_profile,
)
from .energy import EnergyReport, estimate_pulse_energy
from .io import load_trace, normalize_trace, save_trace
from .metadata import (
    DatasetMetadata,
    DeviceMetadata,
    ExperimentMetadata,
    MetadataValidationError,
    MetadataValidationReport,
    load_metadata,
    metadata_summary,
    save_metadata,
    validate_metadata,
)
from .metrics import compute_branch_metrics, compute_cycle_summary
from .retention import RetentionFit, fit_power_law_retention
from .schema import DataValidationError, ValidationReport, validate_trace
from .synthetic import (
    SYNTHETIC_PRESETS,
    available_presets,
    generate_synthetic_trace,
    metadata_for_preset,
)
from .taxonomy import TAG_VOCABULARY, normalize_tag, normalize_tags, vocabulary_as_dict

__all__ = [
    "AnalysisReport",
    "DEVICE_PROFILE_TEMPLATES",
    "DataValidationError",
    "DatasetMetadata",
    "DeviceMetadata",
    "DeviceProfileTemplate",
    "EnergyReport",
    "ExperimentMetadata",
    "MetadataValidationError",
    "MetadataValidationReport",
    "RetentionFit",
    "SYNTHETIC_PRESETS",
    "TAG_VOCABULARY",
    "ValidationReport",
    "analyze_trace",
    "available_device_profiles",
    "available_presets",
    "compute_branch_metrics",
    "compute_cycle_summary",
    "device_profiles_as_dict",
    "estimate_pulse_energy",
    "fit_power_law_retention",
    "generate_synthetic_trace",
    "load_metadata",
    "load_trace",
    "metadata_for_device_profile",
    "metadata_for_preset",
    "metadata_summary",
    "normalize_tag",
    "normalize_tags",
    "normalize_trace",
    "save_metadata",
    "save_trace",
    "validate_metadata",
    "validate_trace",
    "vocabulary_as_dict",
]

__version__ = "0.2.0"
