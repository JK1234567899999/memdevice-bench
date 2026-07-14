# MemDeviceBench

MemDeviceBench is a topology- and mechanism-aware data standard and analysis pipeline for memory and adaptive electronic devices. It treats a device description as a combination of independent axes rather than a single label: technology, accessible terminal count, platform, physical mechanism, material system, observed behavior, and experiment profile.

The validated `v0.2` engine analyzes pulse-by-pulse conductance-update traces. Every reported metric can be traced to input rows, a documented equation, a normalized metadata sidecar, and a versioned implementation.

Start with the [tagging model](tagging.md), then the [data format](data-format.md). Use the CLI for routine reports or the Python API for custom analysis.
