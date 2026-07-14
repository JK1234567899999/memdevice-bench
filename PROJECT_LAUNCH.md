# Public launch checklist

Repository-owner links are initialized for `JK1234567899999/memdevice-bench`.

## 1. Verify locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
make check
python -m build
python -m twine check dist/*
```

Run both topology paths:

```bash
memdevice-bench generate --preset rram-2t --output /tmp/rram.csv
memdevice-bench analyze /tmp/rram.csv \
  --metadata /tmp/rram.metadata.json \
  --output-dir /tmp/rram-report

memdevice-bench generate --preset ecram-tft-3t --output /tmp/ecram.csv
memdevice-bench analyze /tmp/ecram.csv \
  --metadata /tmp/ecram.metadata.json \
  --output-dir /tmp/ecram-report
```

Confirm that the reports contain the correct topology tags and that the 3T path uses programming-path current. Remove `pulse_current_a` from the 3T trace and verify that energy becomes `not_computed`.

## 2. Review the scientific claims

Before launch, check that:

- the project is described as technology-neutral and topology-aware;
- `TFT` appears as a platform tag, not a peer enum to RRAM/FRAM/ECRAM;
- mechanism tags are evidence-dependent;
- templates are described as starting points;
- synthetic traces are not described as compact physical models;
- unimplemented DC I–V, polarization, EIS, and waveform profiles are labeled roadmap items;
- no universal device-quality score is claimed.

## 3. Publish the repository

```bash
git init
git add .
git commit -m "Initial public release of MemDeviceBench"
gh repo create memdevice-bench --public --source=. --remote=origin --push
```

Enable branch protection, required CI, private vulnerability reporting, Discussions, and GitHub Pages.

Suggested topics:

```text
memory-devices, two-terminal, three-terminal, four-terminal,
rram, reram, pram, pcm, fram, fefet, ecram, cbram, mram,
tft, oect, memtransistor, analog-memory, neuromorphic-hardware,
semiconductor-devices, device-characterization, pulse-measurement,
retention, endurance, open-science
```

## 4. Release

Create a `v0.2.0` release only after CI passes from a clean tag. Connect an archival service before release when a DOI is needed. Use trusted publishing rather than a long-lived registry token. Verify that the package name is available before publishing.

## 5. First real-data validation

Validate at least:

- one real 2T RRAM/PCM/CBRAM dataset;
- one real 3T ECRAM/FeFET/TFT dataset;
- one 4T or separately gated transistor dataset;
- one measurement with sampled programming current/waveform.

Document pulse-source impedance, rise/fall time, compliance behavior, timing, read delay, integration time, cabling/probe bandwidth, and the actual write/read terminal paths.

## 6. Build a real contributor community

Request substantive contributions: instrument importers, metric tests, licensed dataset cards, artifact detectors, or new experiment-profile schemas. Do not split trivial edits to inflate contributor counts.

## 7. Evidence log

Maintain `IMPACT.md` with public releases, external adopters, dependent projects, downloads, contributors, citations, security work, and maintenance activity. Record only verifiable numbers and links.
