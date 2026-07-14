"""Regenerate JSON schemas and profile templates from the Python vocabulary."""

from __future__ import annotations

import json
from pathlib import Path

from memdevice_bench.device_profiles import device_profiles_as_dict
from memdevice_bench.taxonomy import TAG_VOCABULARY

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schema"


def tag_array(group: str, *, min_items: int = 0) -> dict[str, object]:
    """Build a JSON Schema array for one controlled tag group."""

    payload: dict[str, object] = {
        "type": "array",
        "uniqueItems": True,
        "items": {"type": "string", "enum": sorted(TAG_VOCABULARY[group])},
    }
    if min_items:
        payload["minItems"] = min_items
    return payload


metadata_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "urn:memdevice-bench:schema:metadata:0.2.0",
    "title": "MemDeviceBench dataset metadata",
    "description": (
        "Topology-aware metadata for memory and adaptive electronic-device datasets. "
        "Controlled tags are separated by physical axis."
    ),
    "type": "object",
    "required": ["schema_version", "device", "experiment"],
    "properties": {
        "schema_version": {"type": "string"},
        "device": {
            "type": "object",
            "required": [
                "device_id",
                "terminal_count",
                "technology_tags",
                "platform_tags",
                "mechanism_tags",
                "material_tags",
                "behavior_tags",
                "custom_tags",
                "notes",
            ],
            "properties": {
                "device_id": {"type": "string", "minLength": 1},
                "terminal_count": {"type": "integer", "minimum": 2},
                "technology_tags": tag_array("technology", min_items=1),
                "platform_tags": tag_array("platform"),
                "mechanism_tags": tag_array("mechanism"),
                "material_tags": tag_array("material"),
                "behavior_tags": tag_array("behavior"),
                "custom_tags": {
                    "type": "array",
                    "uniqueItems": True,
                    "items": {"type": "string", "minLength": 1},
                },
                "notes": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "experiment": {
            "type": "object",
            "required": [
                "profile",
                "instrument",
                "source_format",
                "temperature_k",
                "notes",
            ],
            "properties": {
                "profile": {
                    "type": "string",
                    "enum": sorted(TAG_VOCABULARY["experiment"]),
                },
                "instrument": {"type": "string"},
                "source_format": {"type": "string"},
                "temperature_k": {
                    "anyOf": [
                        {"type": "number", "exclusiveMinimum": 0},
                        {"type": "null"},
                    ]
                },
                "notes": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "license": {"type": "string"},
        "source_url": {"type": "string"},
        "citation": {"type": "string"},
    },
    "additionalProperties": False,
}

pulse_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "urn:memdevice-bench:schema:pulse-update-row:0.2.0",
    "title": "MemDeviceBench canonical pulse-update row",
    "description": (
        "One canonical row represents the positive read-conductance magnitude measured after a "
        "programming pulse. Static device identity and terminal topology live in a "
        "metadata sidecar."
    ),
    "type": "object",
    "required": ["device_id", "cycle", "pulse_index", "direction", "conductance_s"],
    "properties": {
        "device_id": {"type": "string", "minLength": 1},
        "cycle": {"type": "integer", "minimum": 0},
        "pulse_index": {"type": "integer", "minimum": 0},
        "direction": {"type": "string", "enum": ["potentiation", "depression"]},
        "conductance_s": {"type": "number", "exclusiveMinimum": 0},
        "pulse_voltage_v": {"type": "number"},
        "pulse_width_s": {"type": "number", "exclusiveMinimum": 0},
        "pulse_current_a": {"type": "number"},
        "read_voltage_v": {"type": "number"},
        "read_current_a": {"type": "number"},
        "timestamp_s": {"type": "number", "minimum": 0},
        "pulse_terminal": {"type": "string"},
        "read_terminal": {"type": "string"},
        "state_label": {"type": "string"},
        "gate_voltage_v": {"type": "number"},
        "drain_voltage_v": {"type": "number"},
        "source_voltage_v": {"type": "number"},
        "body_voltage_v": {"type": "number"},
        "gate_current_a": {"type": "number"},
        "drain_current_a": {"type": "number"},
        "source_current_a": {"type": "number"},
        "body_current_a": {"type": "number"},
    },
    "additionalProperties": True,
}

SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
for name, payload in (
    ("memdevice-bench-metadata.schema.json", metadata_schema),
    ("memdevice-bench-pulse-update.schema.json", pulse_schema),
    ("device-profile-templates.json", device_profiles_as_dict()),
):
    path = SCHEMA_DIR / name
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(path)
