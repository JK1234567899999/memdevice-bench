# Changelog

## Unreleased

- Added non-fatal 3T/4T programming-path consistency warnings that compare generic pulse
  current with declared terminal-resolved and read-path currents when available.

## 0.2.0

- Renamed and generalized the project from an ECRAM-focused package to MemDeviceBench.
- Added independent technology, terminal topology, platform, mechanism, material, behavior, and experiment tags.
- Added editable device-profile templates spanning RRAM, PCM/PRAM, FRAM, FeFET, ECRAM, TFT, OECT, MRAM, FTJ, and 4T memtransistors.
- Added JSON metadata sidecars with normalization and physical-consistency validation.
- Added RRAM, PCM/PRAM, CBRAM, ECRAM/TFT, FeFET/TFT, and four-terminal memtransistor synthetic presets.
- Added terminal-resolved voltage/current columns.
- Made energy analysis topology-aware and restricted `V²G_readt` fallback to metadata explicitly identifying a 2-terminal DUT.
- Added metadata-aware CLI, reports, schemas, tests, project brief, and reusable project-builder prompt.

## 0.1.0

- Initial pulse-update validation, metrics, retention, energy, synthetic data, reporting, and community scaffolding.
