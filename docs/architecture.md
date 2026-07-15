# Architecture

## Separation of concerns

MemDeviceBench uses five layers:

1. **Taxonomy** — controlled multi-axis tags and aliases in `taxonomy.py`.
2. **Device-profile templates** — editable, non-authoritative starting tag combinations in `device_profiles.py`.
3. **Metadata** — JSON sidecar parsing, normalization, and physical-consistency warnings in `metadata.py`.
4. **Numerical table** — canonical pulse-update CSV normalization and validation in `io.py` and `schema.py`.
5. **Analysis/reporting** — transparent metrics, topology-aware energy handling, and report generation.

This structure permits new experiment profiles to be added without redefining device identity.

## Current package modules

- `taxonomy.py`: vocabulary, aliases, terminal topology tags.
- `device_profiles.py`: illustrative RRAM/PCM/FRAM/FeFET/ECRAM/TFT/OECT/4T metadata templates.
- `device_profiles.py`: illustrative RRAM, PCM/PRAM, FRAM, FeFET, ECRAM, TFT, OECT, MRAM, FTJ, and 4T tag templates.
- `metadata.py`: dataclasses, JSON I/O, consistency checks.
- `schema.py`: numerical table validation.
- `io.py`: CSV load/save and direction normalization.
- `metrics.py`: branch, cycle, and endurance metrics.
- `energy.py`: measured programming energy, restricted two-terminal fallback, and
  multi-terminal programming-path provenance checks.
- `retention.py`: power-law retention fit.
- `synthetic.py`: tagged software-test presets.
- `analysis.py`: composition and metadata integration.
- `report.py`: JSON/CSV/PNG artifacts.
- `cli.py`: user-facing commands.

## Extension interface

A future profile should define:

- required and optional canonical columns;
- SI unit conventions;
- metadata fields unique to that profile;
- validation rules and known artifacts;
- metrics with equations and failure behavior;
- at least one synthetic invariant test and one real public-data regression test.

Proposed profile packages:

- `profiles/dc_iv.py`
- `profiles/transfer.py`
- `profiles/polarization.py`
- `profiles/transient.py`
- `profiles/impedance.py`

The project should not use a universal device score. Cross-technology comparisons must expose measurement conditions and metric definitions.
