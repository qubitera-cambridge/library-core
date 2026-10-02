# Provenance: Hadamard Test

- **Pattern source**: the standard Hadamard test construction (ancilla in superposition,
  controlled-U, optional S-dagger for the imaginary component, final Hadamard + measurement) as
  presented in Nielsen & Chuang and widely used across the Qiskit ecosystem. Written
  independently against Qiskit 2.x's current API, not copied from a single file.
- **License of source pattern**: Apache-2.0-equivalent (standard textbook construction; no
  single copyrighted source file).
- **Why this was added**: library-core's `quantum-krylov-solver` and `df-vqls-solver` algorithms
  (see their own `PROVENANCE.md`) both build on this exact primitive internally (density matrix
  exponentiation and overlap estimation, respectively) — adding it here as its own catalogued
  algorithm makes that dependency relationship explicit and checkable (see
  `algorithm_dependencies` in each algorithm's `metadata.yaml`, and
  `tests/test_repo_structure.py`'s check that referenced ids actually exist).
- **Verification**: exact `Statevector` checks confirm the ancilla's measured probability
  difference equals the analytic `Re`/`Im<0|Rz(theta)|0>` value exactly (not just within
  tolerance) across 7 theta values and both real/imaginary components. A seeded sampled smoke
  test and the `demo()` function both independently confirm the sampled estimate matches theory
  within expected shot noise. See `metadata.yaml`'s `benchmarks`.
