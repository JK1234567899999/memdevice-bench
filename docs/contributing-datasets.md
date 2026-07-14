# Contributing datasets

A public dataset contribution should contain:

- a dataset card based on `datasets/TEMPLATE.md`;
- a canonical CSV or a script that downloads data from a stable public archive;
- a JSON metadata sidecar using controlled tags;
- license, provenance, and citation information;
- terminal definitions and a wiring/schematic description where topology is nontrivial;
- instrument, pulse, read, environment, and device-stack metadata;
- a statement of whether conductance is read before or after each pulse;
- validation output and at least one expected metric value.

Do not infer missing units, switching mechanisms, or terminal meanings. Use `unknown` or explicit notes where evidence is incomplete. Synthetic data must be labeled as synthetic and must not be presented as a physical compact model.
