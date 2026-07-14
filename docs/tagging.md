# Multi-axis device tagging

## 1. Why the taxonomy is multi-axis

The following terms are often presented as though they were mutually exclusive device classes, but they describe different physical or experimental dimensions:

- `RRAM`, `PCM/PRAM`, `FRAM`, `FeFET`, `ECRAM`, `MRAM`: technology or device concept;
- `TFT`, `OECT`, `MOSFET`, `resistor`, `capacitor`: device platform or form factor;
- `2T`, `3T`, `4T`: electrically accessible terminals of the measured DUT;
- `filamentary`, `phase-change`, `ferroelectric`, `electrochemical`, `charge-trap`: switching mechanism;
- `analog`, `binary`, `volatile`, `nonvolatile`: observed behavior;
- `pulse-update`, `dc-iv`, `polarization`, `retention`: measurement profile.

MemDeviceBench therefore stores each descriptor on an independent axis. A dataset is allowed to contain multiple tags on each axis when that is scientifically justified.

## 2. Terminal topology

`terminal_count` is an integer greater than or equal to two. The corresponding canonical platform tag is added automatically:

| `terminal_count` | Canonical topology tag |
|---:|---|
| 2 | `two-terminal` |
| 3 | `three-terminal` |
| 4 | `four-terminal` |
| 5 or more | `multi-terminal` |

The count refers to the **electrically accessible interface of the measured DUT**. It is not automatically the number of active elements in a memory cell.

Examples:

- bare RRAM crosspoint: usually 2T;
- integrated 1T1R cell: add `1t1r-cell`; determine terminal count from the actual external measurement nodes;
- ferroelectric capacitor: 2T capacitor test structure;
- 1T1C FRAM cell: add `1t1c-cell`; do not infer topology solely from the label;
- transistor with source, drain, gate, and body/back gate: 4T;
- four-wire Kelvin measurement of a nominally 2T material stack: document both the intrinsic element and the accessible measurement nodes in notes; do not hide the sensing topology.

A terminal tag that contradicts `terminal_count` is a validation error.

## 3. Controlled vocabulary

### Technology/device-concept tags

```text
rram, memristor, pram, pcm, fram, fefet, ftj, ecram, cbram,
mram, stt-mram, sot-mram, flash, floating-gate-memory,
charge-trap-memory, memtransistor, redox-transistor, memcapacitor,
memdiode, mott-memory, molecular-memory, selector, other
```

`PRAM` and `PCM` are both retained for discoverability. A dataset may carry both when the source community uses both names. `ReRAM`, `FeRAM`, `Fe-FET`, and similar aliases are normalized.

A technology tag does not prove a mechanism. For example, `rram` should not automatically imply `filamentary`; use `unknown`, `mixed`, or a more specific mechanism only when supported by device structure and measurement evidence.

### Platform/form-factor tags

```text
two-terminal, three-terminal, four-terminal, multi-terminal,
resistor, capacitor, diode, transistor, fet, tft, mosfet, oect,
electrolyte-gated-transistor, crosspoint, crossbar, 1r-cell,
1t1r-cell, 1s1r-cell, 1t1c-cell, vertical, planar, flexible, other
```

`OECT` and `electrolyte-gated-transistor` are not collapsed into one term. An OECT is a particular electrochemical transistor platform; an electrolyte-gated FET can operate through different interfacial or bulk mechanisms.

### Mechanism tags

```text
filamentary, valence-change, electrochemical-metallization,
phase-change, ferroelectric, electrochemical, ion-insertion,
ionic-gating, redox, charge-trap, floating-gate, magnetic,
magnetic-tunnel-junction, interfacial-barrier,
interfacial-switching, mott-transition, tunneling, thermal,
mixed, unknown
```

Mechanism labels should be treated as evidence-bearing metadata, not marketing names. Useful evidence may include polarity dependence, area scaling, temperature dependence, transient kinetics, composition/structural analysis, gate-current measurements, or direct observation of a phase/filament. Ambiguous cases should remain `unknown` or `mixed`.

### Material tags

```text
oxide, metal-oxide, ferroelectric-oxide, chalcogenide, organic,
polymer, two-dimensional, silicon, perovskite, nitride,
electrolyte, solid-electrolyte, ionic-liquid, metal, other
```

These are broad search tags, not a substitute for a complete stack. Exact composition, thickness, electrodes, encapsulation, and process history should be preserved in dataset notes or a future structured stack schema.

### Behavior tags

```text
analog, binary, multilevel, volatile, nonvolatile,
threshold-switching, bipolar, unipolar, incremental, gate-tunable,
stochastic, symmetric, asymmetric, potentiation-depression,
reservoir, synaptic
```

Behavior tags describe what was observed under stated conditions. For example, `nonvolatile` should be supported by a declared retention window, temperature, state-preparation method, and read protocol rather than inferred from the device name.

### Experiment-profile tags

```text
pulse-update, dc-iv, transfer-curve, output-curve, retention,
endurance, transient, noise, variability, impedance, polarization,
switching, switching-speed, temperature, frequency, read-disturb,
write-disturb, stp, ltp, ppf, stdp, reservoir-computing
```

The current numerical engine is validated primarily for `pulse-update`. Other profiles define the project extension path and should not be described as fully implemented until their schema, metrics, and tests exist.

## 4. Example tag records

### Two-terminal RRAM

```json
{
  "terminal_count": 2,
  "technology_tags": ["rram"],
  "platform_tags": ["resistor", "crossbar", "two-terminal"],
  "mechanism_tags": ["unknown"],
  "material_tags": ["oxide"],
  "behavior_tags": ["analog", "multilevel", "nonvolatile"]
}
```

A generic template uses `unknown` mechanism. Change it to `filamentary`, `valence-change`, or `interfacial-switching` only when warranted.

### Two-terminal PCM/PRAM

```json
{
  "terminal_count": 2,
  "technology_tags": ["pcm", "pram"],
  "platform_tags": ["resistor", "two-terminal"],
  "mechanism_tags": ["phase-change", "thermal"],
  "material_tags": ["chalcogenide"],
  "behavior_tags": ["multilevel", "nonvolatile"]
}
```

### Two-terminal FRAM capacitor

```json
{
  "terminal_count": 2,
  "technology_tags": ["fram"],
  "platform_tags": ["capacitor", "two-terminal"],
  "mechanism_tags": ["ferroelectric"],
  "material_tags": ["ferroelectric-oxide"],
  "behavior_tags": ["binary", "nonvolatile"]
}
```

This describes a capacitor test structure, not automatically a complete 1T1C cell. Polarization/PUND data require a dedicated experiment profile.

### Three-terminal ECRAM/TFT

```json
{
  "terminal_count": 3,
  "technology_tags": ["ecram"],
  "platform_tags": ["tft", "transistor", "three-terminal"],
  "mechanism_tags": ["electrochemical", "ion-insertion", "redox"],
  "material_tags": ["electrolyte", "oxide"],
  "behavior_tags": ["analog", "multilevel", "nonvolatile"]
}
```

### Generic three-terminal TFT

```json
{
  "terminal_count": 3,
  "technology_tags": ["other"],
  "platform_tags": ["fet", "tft", "transistor", "three-terminal"],
  "mechanism_tags": ["unknown"],
  "material_tags": ["oxide"],
  "behavior_tags": ["gate-tunable"]
}
```

This record does not claim memory behavior. Add a memory technology and retention-related behavior only from actual evidence.

### Four-terminal memtransistor

```json
{
  "terminal_count": 4,
  "technology_tags": ["memtransistor"],
  "platform_tags": ["tft", "transistor", "four-terminal"],
  "mechanism_tags": ["unknown"],
  "material_tags": ["two-dimensional"],
  "behavior_tags": ["analog", "gate-tunable", "multilevel"]
}
```

The fourth terminal may be a body/back gate or a separate write terminal. Define the actual write and read paths in `pulse_terminal`, `read_terminal`, and notes.

## 5. Illustrative templates versus scientific metadata

`memdevice-bench device-profiles` exposes common starting templates. They are deliberately labeled illustrative because:

- the same technology can operate through more than one mechanism;
- terminal count depends on the measured interface;
- volatile/nonvolatile behavior depends on time window and conditions;
- platform labels do not by themselves imply memory;
- materials and mechanisms may be disputed or sample-dependent.

Use templates to reduce clerical errors, then edit the sidecar before analysis or publication.

## 6. Alias normalization

Examples of accepted aliases include:

- `ReRAM` → `rram`
- `FeRAM` → `fram`
- `Fe-FET` → `fefet`
- `2T` → `two-terminal`
- `thin-film-transistor` → `tft`
- `ECM` → `electrochemical-metallization`
- `intercalation` → `ion-insertion`
- `2D` → `two-dimensional`
- `non-volatile` → `nonvolatile`
- `I-V` → `dc-iv`

The CLI command `memdevice-bench taxonomy` prints the complete canonical vocabulary and alias map.

## 7. Metadata example

```json
{
  "schema_version": "0.2.0",
  "device": {
    "device_id": "wafer03-d17",
    "terminal_count": 3,
    "technology_tags": ["ecram"],
    "platform_tags": ["tft", "transistor", "three-terminal"],
    "mechanism_tags": ["electrochemical", "ion-insertion", "redox"],
    "material_tags": ["electrolyte", "oxide"],
    "behavior_tags": ["analog", "multilevel", "nonvolatile"],
    "custom_tags": ["protonic"],
    "notes": ""
  },
  "experiment": {
    "profile": "pulse-update",
    "instrument": "Keithley 4200A-SCS",
    "source_format": "canonical-csv",
    "temperature_k": 300.0,
    "notes": ""
  },
  "license": "",
  "source_url": "",
  "citation": ""
}
```

`device.device_id` must match at least one `device_id` in the associated numerical table.
