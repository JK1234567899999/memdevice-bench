"""Compare the same analysis workflow across 2T and 3T software-test traces."""

from memdevice_bench import analyze_trace, generate_synthetic_trace, metadata_for_preset

for preset in ("rram-2t", "ecram-tft-3t"):
    trace = generate_synthetic_trace(
        preset=preset,
        cycles=3,
        pulses_per_branch=64,
        seed=7,
    )
    metadata = metadata_for_preset(preset)
    report = analyze_trace(trace, metadata=metadata)
    print(preset)
    print("  topology:", report.summary["topology_tag"])
    print("  tags:", ", ".join(report.summary["all_tags"]))
    print("  energy:", report.summary.get("energy_method", "not computed"))
