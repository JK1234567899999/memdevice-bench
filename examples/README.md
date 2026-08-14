# Examples

This directory demonstrates the same pulse-update workflow across accessible terminal topologies.

| Trace | Tags | Purpose |
|---|---|---|
| `rram_2t.csv` | `rram`, `resistor`, `two-terminal`, `filamentary` | two-terminal programming/read path |
| `ecram_tft_3t.csv` | `ecram`, `tft`, `transistor`, `three-terminal`, `electrochemical` | separate gate programming and drain-source read paths |
| `memtransistor_4t.csv` | `memtransistor`, `charge-trap-memory`, `tft`, `four-terminal` | body/back-gate-aware table columns |

Each CSV has a matching `.metadata.json` sidecar and a topology-specific report directory. Reports include normalized tags, a flattened `all_tags` field, and topology-aware energy provenance.

`metadata/` contains illustrative device-profile templates spanning:

- RRAM, CBRAM, PCM/PRAM, FRAM, FTJ, and MRAM two-terminal structures;
- generic TFT, FeFET, ECRAM, OECT/redox transistor, charge-trap TFT, and flash MOSFET three-terminal structures;
- a dual-gate/four-terminal memtransistor.

Profiles are editable starting points, not physical assertions. Mechanism, material, behavior, and terminal count must be checked against the actual measured DUT. FRAM polarization, FTJ/MRAM switching, and generic TFT transfer-curve files are metadata-only examples because those numerical profiles are roadmap items rather than implemented pulse-update conductance analyses.

All generated traces are software-test/tutorial data, not compact physical models or literature reference datasets.

For the commands and scientific guardrails needed to move from these tutorial
files to a real measurement, see the [first-trace walkthrough](../docs/first-real-trace.md).
