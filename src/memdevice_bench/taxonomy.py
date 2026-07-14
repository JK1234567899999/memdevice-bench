"""Controlled, multi-axis tags for memory and adaptive electronic devices.

The taxonomy deliberately separates memory technology, device platform,
physical mechanism, material system, observed behavior, and experiment type.
A device can therefore be tagged as, for example, ``ecram`` + ``tft`` +
``three-terminal`` without treating those labels as mutually exclusive classes.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

TAG_VOCABULARY: Mapping[str, frozenset[str]] = {
    "technology": frozenset(
        {
            "rram",
            "memristor",
            "pram",
            "pcm",
            "fram",
            "fefet",
            "ftj",
            "ecram",
            "cbram",
            "mram",
            "stt-mram",
            "sot-mram",
            "flash",
            "floating-gate-memory",
            "charge-trap-memory",
            "memtransistor",
            "redox-transistor",
            "memcapacitor",
            "memdiode",
            "mott-memory",
            "molecular-memory",
            "selector",
            "other",
        }
    ),
    "platform": frozenset(
        {
            "two-terminal",
            "three-terminal",
            "four-terminal",
            "multi-terminal",
            "resistor",
            "capacitor",
            "diode",
            "transistor",
            "fet",
            "tft",
            "mosfet",
            "oect",
            "electrolyte-gated-transistor",
            "crosspoint",
            "crossbar",
            "1r-cell",
            "1t1r-cell",
            "1s1r-cell",
            "1t1c-cell",
            "vertical",
            "planar",
            "flexible",
            "other",
        }
    ),
    "mechanism": frozenset(
        {
            "filamentary",
            "valence-change",
            "electrochemical-metallization",
            "phase-change",
            "ferroelectric",
            "electrochemical",
            "ion-insertion",
            "ionic-gating",
            "redox",
            "charge-trap",
            "floating-gate",
            "magnetic",
            "magnetic-tunnel-junction",
            "interfacial-barrier",
            "interfacial-switching",
            "mott-transition",
            "tunneling",
            "thermal",
            "mixed",
            "unknown",
        }
    ),
    "material": frozenset(
        {
            "oxide",
            "metal-oxide",
            "ferroelectric-oxide",
            "chalcogenide",
            "organic",
            "polymer",
            "two-dimensional",
            "silicon",
            "perovskite",
            "nitride",
            "electrolyte",
            "solid-electrolyte",
            "ionic-liquid",
            "metal",
            "other",
        }
    ),
    "behavior": frozenset(
        {
            "analog",
            "binary",
            "multilevel",
            "volatile",
            "nonvolatile",
            "threshold-switching",
            "bipolar",
            "unipolar",
            "incremental",
            "gate-tunable",
            "stochastic",
            "symmetric",
            "asymmetric",
            "potentiation-depression",
            "reservoir",
            "synaptic",
        }
    ),
    "experiment": frozenset(
        {
            "pulse-update",
            "dc-iv",
            "transfer-curve",
            "output-curve",
            "retention",
            "endurance",
            "transient",
            "noise",
            "variability",
            "impedance",
            "polarization",
            "switching",
            "switching-speed",
            "temperature",
            "frequency",
            "read-disturb",
            "write-disturb",
            "stp",
            "ltp",
            "ppf",
            "stdp",
            "reservoir-computing",
        }
    ),
}

_TAG_ALIASES: Mapping[str, Mapping[str, str]] = {
    "technology": {
        "reram": "rram",
        "re-ram": "rram",
        "resistive-ram": "rram",
        "resistive-random-access-memory": "rram",
        "memristive-device": "memristor",
        "phase-change-memory": "pcm",
        "phase-change-ram": "pram",
        "feram": "fram",
        "fe-ram": "fram",
        "ferroelectric-ram": "fram",
        "fe-fet": "fefet",
        "ferroelectric-fet": "fefet",
        "ferroelectric-tunnel-junction": "ftj",
        "electrochemical-ram": "ecram",
        "conductive-bridge-ram": "cbram",
        "magnetoresistive-ram": "mram",
        "sttmram": "stt-mram",
        "spin-transfer-torque-mram": "stt-mram",
        "sotmram": "sot-mram",
        "spin-orbit-torque-mram": "sot-mram",
        "memory-transistor": "memtransistor",
        "memory-diode": "memdiode",
    },
    "platform": {
        "2t": "two-terminal",
        "2-terminal": "two-terminal",
        "two-terminal-device": "two-terminal",
        "3t": "three-terminal",
        "3-terminal": "three-terminal",
        "three-terminal-device": "three-terminal",
        "4t": "four-terminal",
        "4-terminal": "four-terminal",
        "four-terminal-device": "four-terminal",
        "n-terminal": "multi-terminal",
        "thin-film-transistor": "tft",
        "field-effect-transistor": "fet",
        "organic-electrochemical-transistor": "oect",
        "egt": "electrolyte-gated-transistor",
        "electrolyte-gated-fet": "electrolyte-gated-transistor",
        "cross-point": "crosspoint",
        "1r": "1r-cell",
        "1t1r": "1t1r-cell",
        "1s1r": "1s1r-cell",
        "1t1c": "1t1c-cell",
    },
    "mechanism": {
        "vcm": "valence-change",
        "ecm": "electrochemical-metallization",
        "electrochemical-metallization-mechanism": "electrochemical-metallization",
        "phase-change-memory": "phase-change",
        "ionic": "ion-insertion",
        "intercalation": "ion-insertion",
        "electrolyte-gating": "ionic-gating",
        "trapping": "charge-trap",
        "mtj": "magnetic-tunnel-junction",
        "interface-switching": "interfacial-switching",
        "mott": "mott-transition",
    },
    "material": {
        "2d": "two-dimensional",
        "2-d": "two-dimensional",
        "hfo2": "ferroelectric-oxide",
        "hafnia": "ferroelectric-oxide",
        "ion-gel": "electrolyte",
    },
    "behavior": {
        "non-volatile": "nonvolatile",
        "multi-level": "multilevel",
        "gradual": "incremental",
        "gate-controlled": "gate-tunable",
        "probabilistic": "stochastic",
        "pot-dep": "potentiation-depression",
    },
    "experiment": {
        "pulse": "pulse-update",
        "pulse-train": "pulse-update",
        "iv": "dc-iv",
        "i-v": "dc-iv",
        "transfer": "transfer-curve",
        "output": "output-curve",
        "eis": "impedance",
        "read-disturbance": "read-disturb",
        "write-disturbance": "write-disturb",
        "short-term-plasticity": "stp",
        "long-term-plasticity": "ltp",
        "paired-pulse-facilitation": "ppf",
        "spike-timing-dependent-plasticity": "stdp",
        "reservoir": "reservoir-computing",
    },
}


def _slug(value: str) -> str:
    return "-".join(value.strip().lower().replace("_", "-").split())


def normalize_tag(group: str, value: str) -> str:
    """Normalize one tag and verify that it belongs to ``group``."""

    if group not in TAG_VOCABULARY:
        raise ValueError(f"unknown tag group: {group!r}")
    slug = _slug(value)
    normalized = _TAG_ALIASES.get(group, {}).get(slug, slug)
    if normalized not in TAG_VOCABULARY[group]:
        choices = ", ".join(sorted(TAG_VOCABULARY[group]))
        raise ValueError(f"unknown {group} tag {value!r}; choose one of: {choices}")
    return normalized


def normalize_tags(group: str, values: Iterable[str]) -> tuple[str, ...]:
    """Normalize, deduplicate, and sort a collection of controlled tags."""

    return tuple(sorted({normalize_tag(group, value) for value in values}))


def terminal_platform_tag(terminal_count: int) -> str:
    """Return the canonical platform tag implied by accessible DUT terminals."""

    if terminal_count == 2:
        return "two-terminal"
    if terminal_count == 3:
        return "three-terminal"
    if terminal_count == 4:
        return "four-terminal"
    if terminal_count >= 5:
        return "multi-terminal"
    raise ValueError("terminal_count must be >= 2")


def vocabulary_as_dict(*, include_aliases: bool = True) -> dict[str, object]:
    """Return a JSON-serializable copy of the vocabulary and accepted aliases."""

    payload: dict[str, object] = {
        "groups": {group: sorted(tags) for group, tags in TAG_VOCABULARY.items()},
        "terminal_count": {
            "2": "two-terminal",
            "3": "three-terminal",
            "4": "four-terminal",
            "5+": "multi-terminal",
        },
    }
    if include_aliases:
        payload["aliases"] = {
            group: dict(sorted(aliases.items())) for group, aliases in _TAG_ALIASES.items()
        }
    return payload
