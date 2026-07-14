"""Regenerate tagged 2T/3T/4T examples, profile metadata, and reports."""

from __future__ import annotations

import json
from pathlib import Path

from memdevice_bench.device_profiles import (
    available_device_profiles,
    device_profiles_as_dict,
    metadata_for_device_profile,
)
from memdevice_bench.io import save_trace
from memdevice_bench.metadata import save_metadata
from memdevice_bench.report import write_report
from memdevice_bench.synthetic import generate_synthetic_trace, metadata_for_preset

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
METADATA_DIR = EXAMPLES / "metadata"
METADATA_DIR.mkdir(parents=True, exist_ok=True)

trace_specs = [
    ("rram-2t", "rram_2t", 2, 32),
    ("ecram-tft-3t", "ecram_tft_3t", 2, 32),
    ("memtransistor-4t", "memtransistor_4t", 2, 32),
]

for preset, stem, cycles, pulses in trace_specs:
    device_id = f"{stem}-demo"
    trace = generate_synthetic_trace(
        preset=preset,
        device_id=device_id,
        cycles=cycles,
        pulses_per_branch=pulses,
        seed=7,
    )
    metadata = metadata_for_preset(preset, device_id=device_id)
    save_trace(trace, EXAMPLES / f"{stem}.csv")
    save_metadata(metadata, EXAMPLES / f"{stem}.metadata.json")
    write_report(trace, EXAMPLES / f"{stem}_report", metadata=metadata)

profile_overrides = {
    "fram-capacitor-2t": "polarization",
    "ftj-2t": "switching",
    "mram-mtj-2t": "switching",
    "tft-generic-3t": "transfer-curve",
    "flash-mosfet-3t": "switching",
}
for profile in available_device_profiles():
    experiment_profile = profile_overrides.get(profile, "pulse-update")
    save_metadata(
        metadata_for_device_profile(
            profile,
            device_id=f"{profile}-example",
            experiment_profile=experiment_profile,
        ),
        METADATA_DIR / f"{profile}.json",
    )

(EXAMPLES / "device_profile_catalog.json").write_text(
    json.dumps(device_profiles_as_dict(), indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(f"Regenerated examples under {EXAMPLES}")
