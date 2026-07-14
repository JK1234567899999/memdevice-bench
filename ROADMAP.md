# Roadmap

## v0.3 — real-data ingestion and uncertainty

- Keithley 4200A/4225-PMU, Keithley 2600-series, and Keysight B1500/WGFMU importers;
- QCoDeS and PyMeasure adapters;
- uncertainty propagation and replicate-level statistics;
- state-dependent asymmetry and read-disturb analysis;
- sampled transient waveform energy integration;
- explicit pulse-source bandwidth, compliance, and clipping checks;
- HTML report generation.

## v0.4 — experiment profiles

- DC I–V profile for set/reset event extraction and compliance metadata;
- TFT transfer/output profile for threshold shift, hysteresis, subthreshold swing, and mobility provenance;
- FRAM/FeFET polarization and PUND profile;
- retention profile with stretched-exponential and multi-timescale fitting;
- transient and impedance profiles;
- schema migration tooling.

## v0.5 — cross-device and cross-lab benchmarking

- condition-aware comparison tables that do not collapse pulse amplitude, width, read bias, and temperature;
- public dataset registry with licenses and versioned hashes;
- cross-laboratory reproducibility examples;
- optional xarray/HDF5 backend for waveform-heavy data;
- uncertainty-aware plots and report templates.

## v1.0 criteria

- stable multi-axis metadata and profile schemas with a migration policy;
- real datasets spanning at least three technology tags and two terminal topologies;
- independent laboratory review or adoption;
- published metric definitions and validation cases;
- reproducible release and archived DOI;
- documented security, deprecation, and governance processes.
