"""Dataset metadata and topology-aware tag validation."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .taxonomy import normalize_tags, terminal_platform_tag

METADATA_SCHEMA_VERSION = "0.2.0"


class MetadataValidationError(ValueError):
    """Raised when device or experiment metadata is invalid."""


@dataclass(frozen=True)
class MetadataValidationReport:
    """Errors and non-fatal physical-consistency warnings."""

    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return not self.errors

    def raise_for_errors(self) -> None:
        if self.errors:
            raise MetadataValidationError("; ".join(self.errors))


@dataclass(frozen=True)
class DeviceMetadata:
    """Controlled multi-axis description of the measured device under test."""

    device_id: str
    terminal_count: int
    technology_tags: tuple[str, ...]
    platform_tags: tuple[str, ...]
    mechanism_tags: tuple[str, ...] = ()
    material_tags: tuple[str, ...] = ()
    behavior_tags: tuple[str, ...] = ()
    custom_tags: tuple[str, ...] = ()
    notes: str = ""


@dataclass(frozen=True)
class ExperimentMetadata:
    """Description of the measurement represented by a table."""

    profile: str = "pulse-update"
    instrument: str = ""
    source_format: str = "canonical-csv"
    temperature_k: float | None = None
    notes: str = ""


@dataclass(frozen=True)
class DatasetMetadata:
    """Top-level sidecar metadata stored next to a measurement table."""

    device: DeviceMetadata
    experiment: ExperimentMetadata = ExperimentMetadata()
    schema_version: str = METADATA_SCHEMA_VERSION
    license: str = ""
    source_url: str = ""
    citation: str = ""


def _string_tuple(payload: dict[str, Any], key: str) -> tuple[str, ...]:
    value = payload.get(key, [])
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise MetadataValidationError(f"{key} must be a list of strings")
    return tuple(value)


def normalize_metadata(metadata: DatasetMetadata) -> DatasetMetadata:
    """Return metadata with canonical controlled tags and terminal topology."""

    if metadata.device.terminal_count < 2:
        raise MetadataValidationError("terminal_count must be >= 2")
    terminal_tag = terminal_platform_tag(metadata.device.terminal_count)

    try:
        technology = normalize_tags("technology", metadata.device.technology_tags)
        platform = set(normalize_tags("platform", metadata.device.platform_tags))
        mechanism = normalize_tags("mechanism", metadata.device.mechanism_tags)
        material = normalize_tags("material", metadata.device.material_tags)
        behavior = normalize_tags("behavior", metadata.device.behavior_tags)
        profile = normalize_tags("experiment", (metadata.experiment.profile,))[0]
    except ValueError as exc:
        raise MetadataValidationError(str(exc)) from exc

    platform.add(terminal_tag)
    custom = tuple(
        sorted({tag.strip().lower() for tag in metadata.device.custom_tags if tag.strip()})
    )
    return DatasetMetadata(
        schema_version=metadata.schema_version,
        device=DeviceMetadata(
            device_id=metadata.device.device_id.strip(),
            terminal_count=int(metadata.device.terminal_count),
            technology_tags=technology,
            platform_tags=tuple(sorted(platform)),
            mechanism_tags=mechanism,
            material_tags=material,
            behavior_tags=behavior,
            custom_tags=custom,
            notes=metadata.device.notes.strip(),
        ),
        experiment=ExperimentMetadata(
            profile=profile,
            instrument=metadata.experiment.instrument.strip(),
            source_format=metadata.experiment.source_format.strip(),
            temperature_k=metadata.experiment.temperature_k,
            notes=metadata.experiment.notes.strip(),
        ),
        license=metadata.license.strip(),
        source_url=metadata.source_url.strip(),
        citation=metadata.citation.strip(),
    )


def validate_metadata(
    metadata: DatasetMetadata, *, strict: bool = False
) -> MetadataValidationReport:
    """Validate schema fields and emit topology/technology consistency warnings."""

    errors: list[str] = []
    warnings: list[str] = []
    try:
        normalized = normalize_metadata(metadata)
    except MetadataValidationError as exc:
        report = MetadataValidationReport(errors=(str(exc),), warnings=())
        if strict:
            report.raise_for_errors()
        return report

    device = normalized.device
    if not device.device_id:
        errors.append("device_id must not be empty")
    if not device.technology_tags:
        errors.append("at least one technology tag is required")
    if metadata.schema_version != METADATA_SCHEMA_VERSION:
        warnings.append(
            f"metadata schema version is {metadata.schema_version!r}; "
            f"this package writes {METADATA_SCHEMA_VERSION!r}"
        )
    if normalized.experiment.temperature_k is not None and normalized.experiment.temperature_k <= 0:
        errors.append("temperature_k must be positive when provided")

    terminal_tags = {
        "two-terminal": 2,
        "three-terminal": 3,
        "four-terminal": 4,
        "multi-terminal": 5,
    }
    for tag, count in terminal_tags.items():
        if tag not in metadata.device.platform_tags:
            continue
        if count == 5 and device.terminal_count >= 5:
            continue
        if device.terminal_count != count:
            errors.append(
                f"platform tag {tag!r} conflicts with terminal_count={device.terminal_count}"
            )

    technology = set(device.technology_tags)
    platform = set(device.platform_tags)
    if "tft" in platform and device.terminal_count < 3:
        warnings.append(
            "a TFT platform normally exposes at least gate, source, and drain terminals"
        )
    if technology.intersection({"ecram", "fefet", "memtransistor"}) and device.terminal_count < 3:
        warnings.append(
            "the selected transistor-like memory technology is commonly measured with "
            ">=3 terminals; confirm that terminal_count describes the accessible DUT "
            "rather than a reduced test fixture"
        )
    two_terminal_families = {"rram", "cbram", "pcm", "pram", "mram"}
    if technology.intersection(two_terminal_families) and device.terminal_count > 2:
        warnings.append(
            "the selected memory element is commonly treated as 2-terminal; additional "
            "terminals may belong to a selector, body, or separate sense path and should "
            "be described in notes"
        )
    if "fram" in technology and "capacitor" not in platform and "1t1c-cell" not in platform:
        warnings.append(
            "FRAM may refer to a 2-terminal ferroelectric capacitor or a circuit-level 1T1C cell; "
            "add a platform tag so the measured object is unambiguous"
        )
    if normalized.experiment.profile != "pulse-update":
        warnings.append(
            f"profile {normalized.experiment.profile!r} is represented in the taxonomy, "
            "but the v0.2 analysis engine is validated primarily for pulse-update "
            "conductance traces"
        )

    report = MetadataValidationReport(
        errors=tuple(dict.fromkeys(errors)), warnings=tuple(dict.fromkeys(warnings))
    )
    if strict:
        report.raise_for_errors()
    return report


def metadata_from_dict(payload: dict[str, Any]) -> DatasetMetadata:
    """Construct metadata from decoded JSON."""

    try:
        device_payload = payload["device"]
    except KeyError as exc:
        raise MetadataValidationError("missing top-level 'device' object") from exc
    if not isinstance(device_payload, dict):
        raise MetadataValidationError("device must be an object")
    experiment_payload = payload.get("experiment", {})
    if not isinstance(experiment_payload, dict):
        raise MetadataValidationError("experiment must be an object")

    try:
        device = DeviceMetadata(
            device_id=str(device_payload["device_id"]),
            terminal_count=int(device_payload["terminal_count"]),
            technology_tags=_string_tuple(device_payload, "technology_tags"),
            platform_tags=_string_tuple(device_payload, "platform_tags"),
            mechanism_tags=_string_tuple(device_payload, "mechanism_tags"),
            material_tags=_string_tuple(device_payload, "material_tags"),
            behavior_tags=_string_tuple(device_payload, "behavior_tags"),
            custom_tags=_string_tuple(device_payload, "custom_tags"),
            notes=str(device_payload.get("notes", "")),
        )
    except KeyError as exc:
        raise MetadataValidationError(f"missing device field: {exc.args[0]}") from exc
    except (TypeError, ValueError) as exc:
        raise MetadataValidationError(f"invalid device field: {exc}") from exc

    temperature_raw = experiment_payload.get("temperature_k")
    temperature = None if temperature_raw is None else float(temperature_raw)
    experiment = ExperimentMetadata(
        profile=str(experiment_payload.get("profile", "pulse-update")),
        instrument=str(experiment_payload.get("instrument", "")),
        source_format=str(experiment_payload.get("source_format", "canonical-csv")),
        temperature_k=temperature,
        notes=str(experiment_payload.get("notes", "")),
    )
    metadata = DatasetMetadata(
        schema_version=str(payload.get("schema_version", METADATA_SCHEMA_VERSION)),
        device=device,
        experiment=experiment,
        license=str(payload.get("license", "")),
        source_url=str(payload.get("source_url", "")),
        citation=str(payload.get("citation", "")),
    )
    return normalize_metadata(metadata)


def metadata_to_dict(metadata: DatasetMetadata) -> dict[str, Any]:
    """Return normalized metadata as a JSON-serializable dictionary."""

    return asdict(normalize_metadata(metadata))


def load_metadata(path: str | Path, *, strict: bool = True) -> DatasetMetadata:
    """Read and validate a JSON metadata sidecar."""

    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(source)
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MetadataValidationError(f"invalid JSON in {source}: {exc}") from exc
    if not isinstance(payload, dict):
        raise MetadataValidationError("metadata root must be a JSON object")
    metadata = metadata_from_dict(payload)
    validate_metadata(metadata, strict=strict)
    return metadata


def save_metadata(metadata: DatasetMetadata, path: str | Path) -> Path:
    """Normalize, validate, and write a JSON metadata sidecar."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    normalized = normalize_metadata(metadata)
    validate_metadata(normalized, strict=True)
    destination.write_text(
        json.dumps(metadata_to_dict(normalized), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination


def metadata_summary(metadata: DatasetMetadata) -> dict[str, Any]:
    """Flatten high-value tags for inclusion in analysis summary JSON."""

    normalized = normalize_metadata(metadata)
    all_tags = sorted(
        {
            *normalized.device.technology_tags,
            *normalized.device.platform_tags,
            *normalized.device.mechanism_tags,
            *normalized.device.material_tags,
            *normalized.device.behavior_tags,
            *normalized.device.custom_tags,
        }
    )
    return {
        "metadata_schema_version": normalized.schema_version,
        "terminal_count": normalized.device.terminal_count,
        "topology_tag": terminal_platform_tag(normalized.device.terminal_count),
        "technology_tags": list(normalized.device.technology_tags),
        "platform_tags": list(normalized.device.platform_tags),
        "mechanism_tags": list(normalized.device.mechanism_tags),
        "material_tags": list(normalized.device.material_tags),
        "behavior_tags": list(normalized.device.behavior_tags),
        "custom_tags": list(normalized.device.custom_tags),
        "all_tags": all_tags,
        "experiment_profile": normalized.experiment.profile,
    }
