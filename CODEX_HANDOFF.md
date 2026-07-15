# MemDeviceBench — Codex handoff

Read this file first when starting work in a new Codex task.

## Project purpose

MemDeviceBench is an Apache-2.0 Python toolkit and metadata standard for reproducible
benchmarking of 2-terminal, 3-terminal, 4-terminal, and multi-terminal memory/adaptive
electronic devices. Its validated analysis core is pulse-by-pulse conductance-update
traces; other experiment profiles are represented in the taxonomy and roadmap but are
not yet general analysis engines.

Keep these scientific rules intact:

- Store technology, accessible terminal count, platform, mechanism, material, behavior,
  and experiment as separate tag axes. Do not turn them into one flat device enum.
- `terminal_count` is the electrically accessible measured DUT interface. Do not infer it
  from circuit labels such as `1T1R` or `1T1C`.
- Treat switching mechanisms as evidence-dependent. `unknown` and `mixed` are valid.
- Do not estimate 3T/4T programming energy from channel read conductance. It requires
  measured programming-path current; the V²Gread·t fallback is only for an explicit 2T DUT.
- The files in `examples/` are deterministic synthetic tutorial/test data, not experimental
  benchmark data or compact physical models.

## Current state (updated 2026-07-15)

- Public repository: <https://github.com/JK1234567899999/memdevice-bench>
- Branch: `main`; initial public commit: `a32b003719e22b5c249e3fd9deb1a13484bd8bde`
- The initial worktree was clean after push. Always run `git status --short --branch` before
  changing anything; preserve user changes if the worktree is no longer clean.
- GitHub CI and OpenSSF Scorecard passed on the initial public commit.
- The unreleased branch adds 3T/4T programming-path consistency warnings so a generic
  `pulse_current_a` can be compared with declared terminal-resolved and read-path current.
- No GitHub Release and no PyPI publication have been made. Do not create either merely as
  part of maintenance; use a clean version tag and confirm the release checklist first.

## Verified local baseline

The initial release was checked with Python 3.12. The latest local check after the
programming-path consistency addition also passed with 25 tests and 82.47% coverage:

- `ruff check .` passed.
- `mypy src/memdevice_bench` passed.
- `pytest --cov=memdevice_bench --cov-report=term-missing` passed: 25 tests, 82.47% coverage.
- `python -m build` and `python -m twine check dist/*` passed.

The developer extra pins `numpy<2.3` because newer NumPy stubs use Python 3.12-only syntax
while mypy intentionally checks the declared Python 3.10 compatibility floor.

## Start here

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest
ruff check .
mypy src/memdevice_bench
```

After activating the environment, `make check` runs Ruff, mypy, and pytest; `make build`
also builds and validates the distributions. Local environments, caches, coverage files, and
`dist/` are excluded by `.gitignore`.

## Repository map

| Path | Role |
| --- | --- |
| `src/memdevice_bench/` | Package code: schema, taxonomy, metadata, I/O, metrics, energy, analysis, reports, CLI, and deterministic synthetic traces. |
| `tests/` | Unit and CLI coverage for schema/metadata, metrics, energy/retention, and report generation. |
| `examples/` | Canonical 2T/3T/4T synthetic CSVs, metadata sidecars, generated reports, and editable profile templates. |
| `schema/` | Generated JSON schemas and device-profile template catalogue. Regenerate with `scripts/generate_json_schemas.py` after vocabulary changes. |
| `docs/` | Architecture, tagging, data format, metrics, dataset guidance, and Korean project brief. |
| `scripts/` | Regeneration helpers. `generate_all_examples.py` rewrites tracked example artifacts deterministically. |
| `.github/workflows/` | CI for Python 3.10–3.12, release-on-published-release workflow, and OpenSSF Scorecard. |
| `PROJECT_LAUNCH.md` | Checklist for future release/community work; treat it as guidance, not an instruction to publish automatically. |

## Safe next-work routine

1. Read `README.md`, `docs/tagging.md`, `docs/data-format.md`, and `docs/metrics.md` before
   changing semantics or metrics.
2. Keep new data non-confidential, redistributable, licensed, and accompanied by metadata and
   a dataset card when applicable.
3. Add or update tests for every behavior change, then run the verified local baseline.
4. Regenerate schemas/examples only when their source vocabulary or generator changes, and
   review the resulting CSV/JSON/PNG diffs before committing.
5. Do not merge Dependabot updates or publish packages/releases without reviewing their CI and
   compatibility impact.

## Useful commands

```bash
# CLI discovery and a reproducible 3T example
memdevice-bench taxonomy
memdevice-bench device-profiles
memdevice-bench generate --preset ecram-tft-3t --output /tmp/ecram.csv
memdevice-bench analyze /tmp/ecram.csv \
  --metadata /tmp/ecram.metadata.json \
  --output-dir /tmp/ecram-report

# Rebuild tracked derived artifacts after changing their generators
python scripts/generate_json_schemas.py
python scripts/generate_all_examples.py
```
