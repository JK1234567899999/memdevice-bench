# MemDeviceBench

**MemDeviceBench** is an open Python toolkit and metadata standard for reproducible benchmarking of **2-terminal, 3-terminal, 4-terminal, and multi-terminal memory/adaptive electronic devices**.

The project is deliberately **not named after ECRAM, RRAM, or any other single device family**. Device identity is represented by independent tag axes, so one dataset can carry several physically different descriptors without forcing them into one flat category.

> Status: `v0.2.0` alpha. The validated numerical core currently targets pulse-by-pulse conductance-update traces. DC I–V, transfer/output curves, polarization/PUND, transient waveforms, noise, and impedance are present in the taxonomy and roadmap, but are not all implemented as analysis profiles yet.

## The central idea: topology first, tags by axis

`RRAM`, `PRAM/PCM`, `FRAM`, `FeFET`, and `ECRAM` are technology or device-concept labels. `TFT`, `OECT`, `capacitor`, `resistor`, and `transistor` describe platforms. `2T`, `3T`, and `4T` describe the electrically accessible terminals of the measured DUT. A physically meaningful record therefore keeps these axes separate.

| Example DUT | Technology tags | Accessible topology | Platform tags | Possible mechanism tags |
|---|---|---:|---|---|
| oxide RRAM element | `rram` | 2T | `resistor`, `crossbar` | `filamentary`, `valence-change`, or `unknown` |
| PCM/PRAM cell | `pcm`, `pram` | 2T | `resistor` | `phase-change`, `thermal` |
| ferroelectric capacitor | `fram` | 2T | `capacitor` | `ferroelectric` |
| FeFET test structure | `fefet` | 3T | `fet`, `tft`, `transistor` | `ferroelectric` |
| ECRAM transistor | `ecram` | 3T | `tft`, `transistor` | `electrochemical`, `ion-insertion`, `redox` |
| generic memory TFT | `memtransistor` or `charge-trap-memory` | 3T | `tft`, `transistor` | `charge-trap`, `floating-gate`, or `unknown` |
| dual-gate memtransistor | `memtransistor` | 4T | `tft`, `transistor` | evidence-dependent |

A 3-terminal oxide ECRAM, for example, may be represented as:

```text
technology: ecram
platform:   tft, transistor, three-terminal
mechanism:  electrochemical, ion-insertion, redox
material:   oxide, electrolyte
behavior:   analog, multilevel, nonvolatile
experiment: pulse-update
```

The tag groups are:

- `technology_tags`: RRAM/ReRAM, PRAM/PCM, FRAM, FeFET, FTJ, ECRAM, CBRAM, MRAM, flash, memtransistor, and related concepts;
- `terminal_count`: integer number of electrically accessible DUT terminals;
- `platform_tags`: resistor, capacitor, diode, transistor, FET, TFT, MOSFET, OECT, crossbar, 1T1R/1T1C, and geometry tags;
- `mechanism_tags`: filamentary, valence-change, ECM, phase-change, ferroelectric, electrochemical, ionic, charge-trap, magnetic, tunneling, interfacial, and `unknown`/`mixed`;
- `material_tags`: oxide, chalcogenide, ferroelectric oxide, organic, 2D, electrolyte, silicon, and related systems;
- `behavior_tags`: analog, binary, multilevel, volatile/nonvolatile, threshold switching, stochastic, synaptic, and other observed behavior;
- `experiment.profile`: pulse update, DC I–V, transfer/output, retention, endurance, polarization, transient, impedance, noise, and related measurement types.

`terminal_count` refers to the interface of the **measured DUT**, not automatically to a circuit-cell label such as `1T1R` or `1T1C`. Circuit integration is recorded with separate platform tags.

## Why this project exists

Device papers frequently use incompatible column names, terminal conventions, state definitions, pulse timing, normalization choices, and energy assumptions. The problem becomes particularly serious when a two-terminal programming path and a three-terminal gate/electrolyte path are analyzed with the same current model.

MemDeviceBench provides:

- a canonical long-form CSV schema for pulse-by-pulse read conductance;
- a JSON metadata sidecar with controlled multi-axis tags;
- illustrative device-profile templates for RRAM, PCM/PRAM, FRAM, FeFET, ECRAM, TFT, OECT, MRAM, FTJ, and 4T memtransistors;
- validation for units, branch order, signs, timestamps, terminal-tag consistency, and read-current/read-voltage consistency;
- transparent linearity, monotonicity, update variability, symmetry, conductance-window, endurance, retention, and energy metrics;
- topology-aware energy handling that prevents channel read conductance from being substituted for an unmeasured 3T/4T programming current;
- multi-terminal programming-path provenance warnings that compare generic pulse current with terminal-resolved and read-path current when available;
- machine-readable JSON/CSV reports and an overview figure;
- contribution units for instrument importers, metrics, public datasets, and future experiment profiles.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

Inspect the vocabulary and common tag templates:

```bash
memdevice-bench taxonomy
memdevice-bench device-profiles
memdevice-bench presets
```

Generate and analyze a 2-terminal tutorial trace:

```bash
memdevice-bench generate \
  --preset rram-2t \
  --output examples/rram_2t.csv \
  --cycles 4 \
  --pulses 64

memdevice-bench validate \
  examples/rram_2t.csv \
  --metadata examples/rram_2t.metadata.json

memdevice-bench analyze \
  examples/rram_2t.csv \
  --metadata examples/rram_2t.metadata.json \
  --output-dir examples/rram_2t_report
```

Create metadata from a profile template, then edit it for the actual sample:

```bash
memdevice-bench init-metadata \
  --template ecram-tft-3t \
  --device-id wafer03-d17 \
  --output wafer03-d17.metadata.json \
  --instrument "Keithley 4200A-SCS"
```

Or specify every axis manually:

```bash
memdevice-bench init-metadata \
  --output device.metadata.json \
  --device-id device-001 \
  --terminals 4 \
  --technology memtransistor \
  --platform tft transistor \
  --mechanism charge-trap \
  --material oxide two-dimensional \
  --behavior analog multilevel nonvolatile \
  --instrument "custom pulse/SMU setup"
```

Python API:

```python
from memdevice_bench import (
    analyze_trace,
    generate_synthetic_trace,
    metadata_for_preset,
)

trace = generate_synthetic_trace(
    preset="rram-2t",
    cycles=3,
    pulses_per_branch=64,
    seed=7,
)
metadata = metadata_for_preset("rram-2t")
report = analyze_trace(trace, metadata=metadata)
print(report.summary["all_tags"])
```

## Canonical pulse table

Required columns:

| Column | Meaning |
|---|---|
| `device_id` | Stable DUT identifier |
| `cycle` | Non-negative update-cycle index |
| `pulse_index` | Pulse order within each branch |
| `direction` | `potentiation` or `depression`; common aliases are normalized |
| `conductance_s` | Positive read-conductance magnitude in siemens |

Recommended generic columns:

| Column | Meaning |
|---|---|
| `pulse_voltage_v` | Signed voltage across the programming path |
| `pulse_width_s` | Programming-pulse duration |
| `pulse_current_a` | Current in the programming path |
| `read_voltage_v` | Read-path voltage |
| `read_current_a` | Read-path current |
| `timestamp_s` | Elapsed experiment time |
| `pulse_terminal` | Programming path, e.g. `gate-to-source` |
| `read_terminal` | Read path, e.g. `drain-to-source` |

Optional terminal-resolved columns include gate, drain, source, and body/back-gate voltages and currents. All canonical numerical fields use SI units.

## Topology-aware programming energy

The preferred energy expression is measured-path integration:

```text
E = |V_program I_program t_pulse|
```

A `V_program² G_read t_pulse` fallback is allowed only when metadata **explicitly identifies a 2-terminal DUT**. It is never silently applied to an unknown topology. For a known 3T/4T DUT, missing programming-path current produces `energy_status = not_computed` rather than substituting channel read conductance.

Even measured `VIt` remains an approximation when a scalar pulse current hides RC transients, displacement current, ionic relaxation, compliance clipping, waveform distortion, or finite-bandwidth sampling. Waveform-level integration is a roadmap item.

## Implemented pulse-update metrics

- conductance window and dynamic-range ratio;
- endpoint-normalized linearity NRMSE and linear-fit `R²`;
- monotonic update fraction;
- mean/median update magnitude and update coefficient of variation;
- early-to-late update ratio as a saturation indicator;
- potentiation/depression update asymmetry;
- cycle-to-cycle conductance-window drift;
- programming energy with explicit provenance;
- power-law retention exponent and fit quality.

No universal device-quality score is produced. Cross-technology comparison must retain pulse amplitude, width, read bias, temperature, topology, state-preparation, and metric-definition context.

## Synthetic presets

The package includes software-test traces for:

- `rram-2t`
- `pcm-pram-2t`
- `cbram-2t`
- `ecram-tft-3t`
- `fefet-tft-3t`
- `memtransistor-4t`

These traces test schemas and workflows. They are not compact physical models or literature benchmark data. FRAM is represented in the metadata templates, but no conductance-trajectory preset is presented as a substitute for polarization/PUND data.

## Documentation and projectization

- Korean overview: [`README.ko.md`](README.ko.md)
- tagging model: [`docs/tagging.md`](docs/tagging.md)
- data format: [`docs/data-format.md`](docs/data-format.md)
- metric definitions and limitations: [`docs/metrics.md`](docs/metrics.md)
- architecture: [`docs/architecture.md`](docs/architecture.md)
- Korean project brief: [`docs/project-brief-ko.md`](docs/project-brief-ko.md)
- reusable Korean project-builder prompt: [`prompts/MEMDEVICEBENCH_PROJECT_PROMPT_KO.md`](prompts/MEMDEVICEBENCH_PROJECT_PROMPT_KO.md)
- public launch plan: [`PROJECT_LAUNCH.md`](PROJECT_LAUNCH.md)
- community contribution map: [`COMMUNITY_TASKS.md`](COMMUNITY_TASKS.md)

## Development

```bash
pip install -e ".[dev]"
ruff check .
mypy src/memdevice_bench
pytest
python -m build
python -m twine check dist/*
```

Repository links target the `JK1234567899999/memdevice-bench` public project. Verify the package name on the target registry before publishing a package release.

## License

Apache-2.0. Dataset licenses remain dataset-specific and must be declared in each metadata sidecar and dataset card.
