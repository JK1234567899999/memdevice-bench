# Data format

MemDeviceBench separates numerical pulse data from device/dataset metadata:

1. a long-form CSV table containing one measured state per programming pulse;
2. a JSON metadata sidecar containing terminal topology and controlled tags.

This avoids repeating static device descriptors in every data row and allows a table to retain terminal-resolved electrical quantities.

## Pulse-update CSV

### Required fields

- `device_id`: stable string identifier.
- `cycle`: non-negative integer update-cycle index.
- `pulse_index`: non-negative integer index within one branch.
- `direction`: normalized to `potentiation` or `depression`.
- `conductance_s`: finite, strictly positive read-conductance magnitude in siemens.

Accepted direction aliases include `set/reset`, `LTP/LTD`, `up/down`, `increase/decrease`, and `+1/-1`. Direction refers to intended read-conductance evolution, not simply pulse-voltage polarity.

### Recommended generic fields

- `pulse_voltage_v`: signed voltage across the programming path.
- `pulse_width_s`: positive pulse duration in seconds.
- `pulse_current_a`: measured current in the programming path.
- `read_voltage_v`: read-path voltage.
- `read_current_a`: read-path current.
- `timestamp_s`: monotonically non-decreasing elapsed time.
- `pulse_terminal`: text such as `terminal-1-to-terminal-2` or `gate-to-source`.
- `read_terminal`: text such as `drain-to-source`.

### Optional terminal-resolved fields

- voltages: `gate_voltage_v`, `drain_voltage_v`, `source_voltage_v`, `body_voltage_v`;
- currents: `gate_current_a`, `drain_current_a`, `source_current_a`, `body_current_a`.

The generic `pulse_voltage_v` and `pulse_current_a` must identify the actual programming path used for energy integration. For a three-terminal device, these are commonly gate/electrolyte quantities, whereas `read_voltage_v` and `read_current_a` represent the channel read path.

## Row convention

By default, each row represents the state measured **after** the corresponding programming pulse. An importer for pre-pulse readout must state that convention in experiment notes and transform it before using standard update metrics. Mixing pre- and post-pulse rows in one dataset is invalid.

## Metadata sidecar

A complete sidecar contains:

```json
{
  "schema_version": "0.2.0",
  "device": {
    "device_id": "wafer03-d17",
    "terminal_count": 3,
    "technology_tags": ["ecram"],
    "platform_tags": ["tft", "transistor", "three-terminal"],
    "mechanism_tags": ["electrochemical", "ion-insertion", "redox"],
    "material_tags": ["oxide", "electrolyte"],
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

`device.device_id` must match at least one `device_id` in the associated table.

## Unit discipline

All canonical numerical columns use SI units. Importers must not infer ambiguous prefixes from unlabeled raw files. Preserve raw exports separately and document conversion factors in code or dataset cards.

When `read_current_a` and `read_voltage_v` are present, the validator compares `|I/V|` with `conductance_s` and warns when the median mismatch exceeds 10%. A mismatch can reflect unit/sign errors, series resistance, nonlinear read bias, or a conductance value obtained from a fit rather than a single operating point.
