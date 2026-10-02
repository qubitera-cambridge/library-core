# QuAlgLib (qubitera)

A single repository bringing together quantum algorithm implementations curated from across the
ecosystem — Qiskit, Classiq's `classiq-library`, academic repos, and other sources — organized by
algorithm family rather than by source project.

## Why this exists

Quantum algorithm implementations are scattered across dozens of SDK-specific repos, each with its
own dependency stack and license. This repo re-homes individual algorithm implementations
(not whole upstream projects) under one roof, indexed the way
[quantumalgorithmzoo.org](https://quantumalgorithmzoo.org/) categorizes algorithms, with
per-file/per-directory provenance and license tracking so nothing's attribution gets lost.

## Structure

```
algorithms/
  algebraic-number-theoretic/   # Shor's, hidden subgroup problem, discrete log, ...
  oracular/                     # Grover's, Deutsch-Jozsa, Simon's, ...
  optimization-approximation/   # QAOA, VQE, ...
  simulation/                   # Hamiltonian simulation, ...
  ...
docs/
  SOURCES.md                    # Ledger of upstream repos considered and their license status
NOTICE                          # Aggregated third-party attributions
LICENSE                         # License for original/glue code in this repo
```

Each algorithm directory carries its own `PROVENANCE.md` noting: source repo, commit/version it was
pulled from, original license, and any modifications made.

## Status

Three algorithms vendored so far, all pattern-level reimplementations from Qiskit:

- `algorithms/oracular/grovers-algorithm/` — Grover's search
- `algorithms/algebraic-number-theoretic/quantum-phase-estimation/` — Quantum Phase Estimation
- `algorithms/simulation/trotterized-tfim/` — Trotterized Hamiltonian simulation (TFIM)

Each has a `metadata.yaml` (schema at `schema/algorithm.schema.json`), a `PROVENANCE.md`, and a
colocated test suite — see `docs/testing.md` for the testing architecture and
`docs/metadata-schema.md` for the metadata fields. See `docs/SOURCES.md` for the upstream repos
under evaluation for future vendoring, and `docs/FUTURE_INTEREST.md` for open ideas not yet ready
for that process.

## Documentation site

A browsable site (explanations, metadata, and live demo output) is generated directly from each
algorithm's files — see `docs/site-generation.md` for how it works and
`tox -e qiskit-docs && tox -e docs` to build it locally.
