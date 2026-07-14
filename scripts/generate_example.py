"""Generate deterministic 2T and 3T tutorial datasets and reports."""

from pathlib import Path

from memdevice_bench.io import save_trace
from memdevice_bench.metadata import save_metadata
from memdevice_bench.report import write_report
from memdevice_bench.synthetic import generate_synthetic_trace, metadata_for_preset

for preset, stem in (("rram-2t", "rram_2t"), ("ecram-tft-3t", "ecram_tft_3t")):
    output = Path(f"examples/{stem}.csv")
    metadata_output = Path(f"examples/{stem}.metadata.json")
    report_output = Path(f"examples/{stem}_report")
    trace = generate_synthetic_trace(
        preset=preset,
        cycles=4,
        pulses_per_branch=64,
        seed=7,
    )
    metadata = metadata_for_preset(preset)
    save_trace(trace, output)
    save_metadata(metadata, metadata_output)
    write_report(trace, report_output, metadata=metadata)
    print(output)
    print(metadata_output)
    print(report_output)
