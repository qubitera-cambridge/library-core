# Provenance: Quantum Krylov Subspace Linear Solver

- **This is a wrapper, not a copy.** The actual algorithm implementation lives in
  [`quantum-krylov-core`](https://github.com/qubitera-cambridge/quantum-krylov-core), a separate,
  privately-hosted qubitera-cambridge repo with its own extensive test suite (15+ test files
  covering classical/quantum/DF-VQLS reduced solvers, multiple basis types, warm starts, and
  accuracy regressions). `qiskit_impl.py` here just calls `quantum_krylov.solve(...)` and formats
  a `demo()` result — it does not reimplement any of the actual numerics.
- **Why vendor a wrapper instead of the real thing**: `quantum-krylov-core` is a mature,
  independently-versioned, multi-module package (basis construction, quantum estimation
  primitives, reduced solvers, orchestration — see its own `__init__.py` docstring for the full
  layering). Copying its source into library-core would mean maintaining two copies that drift;
  depending on it as a pinned package (like `library-ui` depends on `library-core`, and like
  Delphi depends on `pce-core`) keeps one source of truth.
- **Commit pinned**: `3939f4a1d61f65cfe2f59a98f1c73552d0a2ea1a` (see `requirements-krylov.txt`).
- **Private dependency**: this repo is private — installing `requirements-krylov.txt` requires
  Git access to qubitera-cambridge's private repositories. See `docs/private-dependencies.md`.
  library-core's default public CI does not install or test this wrapper for that reason; a
  separate `krylov` tox environment exists for anyone with access to run it.
- **Verification**: confirmed `quantum_krylov.solve(..., implementation='classical')` reproduces
  `numpy.linalg.solve` exactly for the demo's 2x2 system (that package's own correctness
  guarantee, re-checked here so a future upstream regression would be caught in library-core's
  suite too, not only upstream). The quantum (real_time basis, dimension=2) path was run directly
  and found to have ~7% relative error vs. the exact solution — reported honestly in `metadata.yaml`
  rather than cherry-picking a configuration that looks exact.
- **Algorithm dependency**: this package's own documentation states it builds on a Hadamard-test-
  style overlap estimation primitive (density matrix exponentiation) internally — see
  `metadata.yaml`'s `algorithm_dependencies: [hadamard-test]`, checked against the real catalogue
  by `tests/test_repo_structure.py`.
