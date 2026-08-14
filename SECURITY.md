# Security Policy

## Supported versions

Only the latest released minor version is supported during the alpha stage.

## Reporting a vulnerability

Do not open a public issue for a vulnerability that could affect users or expose unpublished datasets. Use [GitHub private vulnerability reporting](https://github.com/JK1234567899999/memdevice-bench/security/advisories/new). If that form is unavailable, contact the maintainer through the private address configured in the repository security settings.

Include the affected version, reproduction steps, impact, and any suggested remediation. The project aims to acknowledge reports within seven days and coordinate disclosure before publishing a fix.

## Data safety

MemDeviceBench processes local files and does not upload data. Contributors must not add telemetry or network transmission without a design review and an explicit opt-in mechanism.

## Fuzzing scope

Pull requests run a bounded ClusterFuzzLite/Atheris target against malformed
metadata JSON input. The target is intended to detect decoder and metadata
validation crashes; it is not a substitute for scientific validation of a
measurement or for review of topology-specific analysis assumptions.
