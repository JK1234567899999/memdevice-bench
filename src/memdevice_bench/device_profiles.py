"""Illustrative multi-axis tag templates for common device families.

Templates accelerate metadata creation but are not physical assertions.  Users
must edit mechanism, material, behavior, and terminal topology to match the
actual measured DUT and the evidence available for that sample.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .metadata import DatasetMetadata, DeviceMetadata, ExperimentMetadata, normalize_metadata
from .taxonomy import terminal_platform_tag


@dataclass(frozen=True)
class DeviceProfileTemplate:
    """Suggested starting tags for one common device/test-structure family."""

    terminal_count: int
    technology_tags: tuple[str, ...]
    platform_tags: tuple[str, ...]
    mechanism_tags: tuple[str, ...]
    material_tags: tuple[str, ...]
    behavior_tags: tuple[str, ...]
    description: str
    caution: str = (
        "Template only: verify terminal count, mechanism, materials, and behavior for the "
        "actual measured DUT before publication."
    )


DEVICE_PROFILE_TEMPLATES: dict[str, DeviceProfileTemplate] = {
    "rram-2t": DeviceProfileTemplate(
        terminal_count=2,
        technology_tags=("rram",),
        platform_tags=("resistor",),
        mechanism_tags=("unknown",),
        material_tags=("oxide",),
        behavior_tags=("nonvolatile",),
        description="Generic two-terminal RRAM/ReRAM element; mechanism intentionally unspecified.",
    ),
    "cbram-2t": DeviceProfileTemplate(
        terminal_count=2,
        technology_tags=("cbram",),
        platform_tags=("resistor",),
        mechanism_tags=("electrochemical-metallization", "filamentary"),
        material_tags=("solid-electrolyte", "metal"),
        behavior_tags=("bipolar", "nonvolatile"),
        description="Two-terminal conductive-bridge/electrochemical-metallization memory.",
    ),
    "pcm-pram-2t": DeviceProfileTemplate(
        terminal_count=2,
        technology_tags=("pcm", "pram"),
        platform_tags=("resistor",),
        mechanism_tags=("phase-change", "thermal"),
        material_tags=("chalcogenide",),
        behavior_tags=("multilevel", "nonvolatile"),
        description="Two-terminal phase-change memory (PCM/PRAM).",
    ),
    "fram-capacitor-2t": DeviceProfileTemplate(
        terminal_count=2,
        technology_tags=("fram",),
        platform_tags=("capacitor",),
        mechanism_tags=("ferroelectric",),
        material_tags=("ferroelectric-oxide",),
        behavior_tags=("binary", "nonvolatile"),
        description="Two-terminal ferroelectric capacitor test structure used in FRAM studies.",
        caution=(
            "This is a capacitor test structure, not automatically a complete 1T1C cell. "
            "Polarization/PUND analysis is outside the current pulse-conductance core."
        ),
    ),
    "ftj-2t": DeviceProfileTemplate(
        terminal_count=2,
        technology_tags=("ftj",),
        platform_tags=("two-terminal",),
        mechanism_tags=("ferroelectric", "tunneling"),
        material_tags=("ferroelectric-oxide",),
        behavior_tags=("multilevel", "nonvolatile"),
        description="Two-terminal ferroelectric tunnel junction.",
    ),
    "mram-mtj-2t": DeviceProfileTemplate(
        terminal_count=2,
        technology_tags=("mram",),
        platform_tags=("two-terminal",),
        mechanism_tags=("magnetic", "magnetic-tunnel-junction"),
        material_tags=("metal", "oxide"),
        behavior_tags=("binary", "nonvolatile"),
        description="Two-terminal magnetic tunnel junction read/write element.",
        caution=(
            "Use STT-MRAM or SOT-MRAM technology tags only when the write geometry and torque "
            "mechanism are established for the measured structure."
        ),
    ),
    "tft-generic-3t": DeviceProfileTemplate(
        terminal_count=3,
        technology_tags=("other",),
        platform_tags=("fet", "tft", "transistor"),
        mechanism_tags=("unknown",),
        material_tags=("oxide",),
        behavior_tags=("gate-tunable",),
        description="Generic three-terminal thin-film transistor; no memory mechanism assumed.",
    ),
    "fefet-tft-3t": DeviceProfileTemplate(
        terminal_count=3,
        technology_tags=("fefet",),
        platform_tags=("fet", "tft", "transistor"),
        mechanism_tags=("ferroelectric",),
        material_tags=("ferroelectric-oxide",),
        behavior_tags=("gate-tunable", "multilevel", "nonvolatile"),
        description="Three-terminal ferroelectric field-effect transistor test structure.",
    ),
    "ecram-tft-3t": DeviceProfileTemplate(
        terminal_count=3,
        technology_tags=("ecram",),
        platform_tags=("tft", "transistor"),
        mechanism_tags=("electrochemical", "ion-insertion", "redox"),
        material_tags=("electrolyte", "oxide"),
        behavior_tags=("analog", "multilevel", "nonvolatile", "potentiation-depression"),
        description="Three-terminal ECRAM implemented in a transistor/TFT-like geometry.",
    ),
    "oect-memory-3t": DeviceProfileTemplate(
        terminal_count=3,
        technology_tags=("redox-transistor",),
        platform_tags=("oect", "transistor"),
        mechanism_tags=("electrochemical", "ionic-gating", "redox"),
        material_tags=("electrolyte", "organic"),
        behavior_tags=("analog", "gate-tunable"),
        description="Three-terminal organic electrochemical transistor used as an adaptive device.",
        caution=(
            "OECT is a platform, not automatically a nonvolatile memory. Add volatile/nonvolatile "
            "only from measured retention."
        ),
    ),
    "charge-trap-tft-3t": DeviceProfileTemplate(
        terminal_count=3,
        technology_tags=("charge-trap-memory", "memtransistor"),
        platform_tags=("tft", "transistor"),
        mechanism_tags=("charge-trap",),
        material_tags=("oxide",),
        behavior_tags=("gate-tunable", "multilevel", "nonvolatile"),
        description="Three-terminal charge-trapping memory transistor/TFT.",
    ),
    "flash-mosfet-3t": DeviceProfileTemplate(
        terminal_count=3,
        technology_tags=("flash", "floating-gate-memory"),
        platform_tags=("fet", "mosfet", "transistor"),
        mechanism_tags=("floating-gate", "tunneling"),
        material_tags=("oxide", "silicon"),
        behavior_tags=("binary", "gate-tunable", "nonvolatile"),
        description="Reduced three-terminal floating-gate MOSFET test configuration.",
        caution=(
            "Many practical flash cells expose or control additional nodes. Set "
            "terminal_count from the measured DUT interface rather than this template name."
        ),
    ),
    "dual-gate-memtransistor-4t": DeviceProfileTemplate(
        terminal_count=4,
        technology_tags=("memtransistor",),
        platform_tags=("tft", "transistor"),
        mechanism_tags=("unknown",),
        material_tags=("two-dimensional",),
        behavior_tags=("analog", "gate-tunable", "multilevel"),
        description="Four-terminal memory transistor with an additional gate/body/write terminal.",
    ),
}


def available_device_profiles() -> tuple[str, ...]:
    """Return sorted profile-template names."""

    return tuple(sorted(DEVICE_PROFILE_TEMPLATES))


def device_profiles_as_dict() -> dict[str, dict[str, Any]]:
    """Return templates with the derived topology tag made explicit."""

    payload: dict[str, dict[str, Any]] = {}
    for name in available_device_profiles():
        template = DEVICE_PROFILE_TEMPLATES[name]
        item = asdict(template)
        topology = terminal_platform_tag(template.terminal_count)
        item["topology_tag"] = topology
        item["platform_tags"] = sorted({*template.platform_tags, topology})
        payload[name] = item
    return payload


def metadata_for_device_profile(
    profile: str,
    *,
    device_id: str,
    instrument: str = "",
    experiment_profile: str = "pulse-update",
    notes: str = "",
) -> DatasetMetadata:
    """Create normalized metadata from an illustrative profile template."""

    if profile not in DEVICE_PROFILE_TEMPLATES:
        choices = ", ".join(available_device_profiles())
        raise ValueError(f"unknown device profile {profile!r}; choose one of: {choices}")
    template = DEVICE_PROFILE_TEMPLATES[profile]
    device_notes = " ".join(part for part in (template.caution, notes.strip()) if part)
    return normalize_metadata(
        DatasetMetadata(
            device=DeviceMetadata(
                device_id=device_id,
                terminal_count=template.terminal_count,
                technology_tags=template.technology_tags,
                platform_tags=template.platform_tags,
                mechanism_tags=template.mechanism_tags,
                material_tags=template.material_tags,
                behavior_tags=template.behavior_tags,
                custom_tags=(f"template:{profile}",),
                notes=device_notes,
            ),
            experiment=ExperimentMetadata(
                profile=experiment_profile,
                instrument=instrument,
            ),
        )
    )
