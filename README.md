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

Scaffolding stage — no algorithms vendored in yet. See `docs/SOURCES.md` for the upstream repos
under evaluation and their license compatibility.
