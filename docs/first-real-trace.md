# First trace walkthrough

This walkthrough turns one pulse-update measurement into a reproducible
MemDeviceBench report. It is deliberately small: it preserves the measured
terminal topology and does not claim a compact device model.

## 1. Start from the closest runnable example

The repository includes ready-to-run tutorial traces for each supported
topology:

| Measured DUT interface | Runnable trace | What it demonstrates |
|---|---|---|
| 2-terminal element | `examples/rram_2t.csv` | A shared programming/read path and an energy fallback permitted only for an explicit 2T DUT. |
| 3-terminal transistor-like device | `examples/ecram_tft_3t.csv` | Gate/electrolyte programming separated from drain-source readout. |
| 4-terminal device | `examples/memtransistor_4t.csv` | Terminal-resolved fields without silently treating a body/back-gate as part of a 2T path. |

Run one without changing the source data:

```bash
python -m pip install memdevice-bench
memdevice-bench validate examples/ecram_tft_3t.csv \
  --metadata examples/ecram_tft_3t.metadata.json
memdevice-bench analyze examples/ecram_tft_3t.csv \
  --metadata examples/ecram_tft_3t.metadata.json \
  --output-dir /tmp/memdevicebench-ecram-report
```

The report directory contains a normalized metadata record, machine-readable
summary JSON/CSV files, and an overview plot. Tutorial traces are synthetic and
must not be cited as measured-device evidence.

## 2. Normalize a real measurement table

Copy an original export before editing it. The analysis table requires these
five SI-unit columns:

```text
device_id, cycle, pulse_index, direction, conductance_s
```

For a 3T or 4T device, retain the actual write and read paths where available:

```text
pulse_voltage_v, pulse_width_s, pulse_current_a,
read_voltage_v, read_current_a, pulse_terminal, read_terminal
```

Do not use channel read conductance as a proxy for unmeasured gate, electrolyte,
or body programming current. If the programming-path current is unavailable,
the report should state that programming energy was not computed.

## 3. Create a metadata sidecar

Use a profile as a starting point, then edit it to match the actual DUT and
measurement conditions:

```bash
memdevice-bench init-metadata \
  --template ecram-tft-3t \
  --device-id your-device-id \
  --instrument "your instrument" \
  --output your-trace.metadata.json
```

Terminal count describes the electrically accessible measurement interface; it
is not automatically the same thing as an array-cell label such as `1T1R` or
`1T1C`.

## 4. Validate before reporting metrics

```bash
memdevice-bench validate your-trace.csv --metadata your-trace.metadata.json
memdevice-bench analyze your-trace.csv \
  --metadata your-trace.metadata.json \
  --output-dir your-trace-report
```

Record the pulse source, read delay/integration time, compliance, terminal
definitions, and any missing programming-current measurement in the metadata
or accompanying dataset card. A valid file format does not by itself validate a
physical mechanism or experimental conclusion.
