# library-core

The quantum algorithm library at the heart of QuAlgLib — implementations curated from across the
ecosystem (Qiskit, Classiq's `classiq-library`, academic repos, and other sources), organized by
algorithm family rather than by source project, and exposed as an installable Python package so
other projects (the `library-ui` documentation site, [Delphi](https://github.com/qubitera-cambridge/delphi))
can depend on it directly.

## Why this exists

Quantum algorithm implementations are scattered across dozens of SDK-specific repos, each with its
own dependency stack and license. This repo re-homes individual algorithm implementations
(not whole upstream projects) under one roof, indexed the way
[quantumalgorithmzoo.org](https://quantumalgorithmzoo.org/) categorizes algorithms, with
per-file/per-directory provenance and license tracking so nothing's attribution gets lost.

This repo is the library itself — correctness, metadata, provenance, licensing. It deliberately
does *not* contain the documentation site (that's [`library-ui`](https://github.com/qubitera-cambridge/library-ui),
which depends on this repo via `pip install library-core`) or anything Delphi-specific. Splitting
these out means neither consumer pulls in dependencies it doesn't need — Delphi gets a lightweight
algorithm catalogue with no MkDocs/Jinja2 in its dependency tree, and the docs site never needs
whatever Delphi-specific machinery might come later.

## Structure

```
src/library_core/
  __init__.py, catalogue.py     # Public API: list_algorithms(), get_explanation(),
                                 #   get_provenance(), load_implementation(), run_demo()
  algorithms/
    algebraic-number-theoretic/   # Shor's, hidden subgroup problem, discrete log, ...
    oracular/                     # Grover's, Deutsch-Jozsa, Simon's, ...
    optimization-approximation/   # QAOA, VQE, ...
    simulation/                   # Hamiltonian simulation, ...
    subroutines/                  # Hadamard test, ... — primitives other algorithms build on
    linear-algebra/                 # Quantum Krylov, DF-VQLS, ...
    ...
docs/
  SOURCES.md                    # Ledger of upstream repos considered and their license status
NOTICE                          # Aggregated third-party attributions
LICENSE                         # License for original/glue code in this repo
```

Each algorithm directory carries its own `PROVENANCE.md` noting: source repo, commit/version it was
pulled from, original license, and any modifications made.

## Using this as a dependency

```bash
pip install git+https://github.com/qubitera-cambridge/library-core.git
```

```python
import library_core

for algo in library_core.list_algorithms():
    print(algo["id"], algo["category"], algo["problem_class"])

result = library_core.run_demo("grovers-algorithm", "qiskit")
```

See `src/library_core/catalogue.py` for the full API (`list_algorithms`, `get_algorithm`,
`get_explanation`, `get_provenance`, `load_implementation`, `run_demo`).

## Status

Six algorithms so far:

- `oracular/grovers-algorithm/` — Grover's search (pattern-level reimplementation from Qiskit)
- `algebraic-number-theoretic/quantum-phase-estimation/` — Quantum Phase Estimation (from Qiskit)
- `simulation/trotterized-tfim/` — Trotterized Hamiltonian simulation (from Qiskit)
- `subroutines/hadamard-test/` — the Hadamard test overlap-estimation primitive (from Qiskit)
- `linear-algebra/quantum-krylov-solver/` — thin wrapper around the sibling private repo
  [`quantum-krylov-core`](https://github.com/qubitera-cambridge/quantum-krylov-core)
- `linear-algebra/df-vqls-solver/` — thin wrapper around the sibling private repo
  [`df-vqls-core`](https://github.com/qubitera-cambridge/df-vqls-core)

Each has a `metadata.yaml` (schema at `schema/algorithm.schema.json`), a `PROVENANCE.md`, and a
colocated test suite — see `docs/testing.md` for the testing architecture and
`docs/metadata-schema.md` for the metadata fields. `metadata.yaml`'s `algorithm_dependencies`
field (e.g. both linear solvers depend on `hadamard-test`) is checked against the real catalogue
by `tests/test_repo_structure.py`, so a dangling or typo'd reference fails structurally, not
silently. See `docs/SOURCES.md` for the upstream repos under evaluation for future vendoring,
`docs/FUTURE_INTEREST.md` for open ideas not yet ready for that process, and
`docs/private-dependencies.md` for how the two linear-solver wrappers' private dependencies are
kept out of the default public CI matrix.
