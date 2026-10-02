# Provenance: Decomposition-Free Variational Quantum Linear Solver (DF-VQLS)

- **This is a wrapper, not a copy.** The actual algorithm implementation lives in
  [`df-vqls-core`](https://github.com/qubitera-cambridge/df-vqls-core), a separate, privately-hosted
  qubitera-cambridge repo with its own test suite (ansatz warm-starts, compute-uncompute overlap
  estimation, joint-conditional cost estimation, optimizer stopping criteria). `qiskit_impl.py`
  here just calls `df_vqls.DF_VQLS(...)` and formats a `demo()` result.
- **Why vendor a wrapper instead of the real thing**: same reasoning as `quantum-krylov-solver`'s
  provenance — `df-vqls-core` is a mature, multi-module package (ansatz, circuit builder, cost
  function/execution backends, optimizer, state preparer — see its own `__init__.py` docstring).
  Depending on it as a pinned package keeps one source of truth instead of two drifting copies.
- **Commit pinned**: `3e16e9e7ecd6f114cb9293a90dabee06606ed0f7` (see `requirements-dfvqls.txt`).
- **Private dependency**: this repo is private — installing `requirements-dfvqls.txt` requires Git
  access to qubitera-cambridge's private repositories. See `docs/private-dependencies.md`.
  library-core's default public CI does not install or test this wrapper for that reason; a
  separate `dfvqls` tox environment exists for anyone with access to run it.
- **Verification**: ran `df_vqls.DF_VQLS(...)` directly against a 2x2 diagonal system with
  `cost_estimator="joint_conditional"`; converged in 22 function evaluations with
  `target_met=True` and a solution direction matching the expected one to cosine similarity
  1.0000. `demo()` correctly compares by direction (cosine similarity), not value equality, since
  DF-VQLS recovers the solution up to scale/sign.
- **Algorithm dependency**: this package's own module docstring states every cost-function overlap
  is estimated via compute-uncompute (a Hadamard-test-family technique) — see `metadata.yaml`'s
  `algorithm_dependencies: [hadamard-test]`, checked against the real catalogue by
  `tests/test_repo_structure.py`.
