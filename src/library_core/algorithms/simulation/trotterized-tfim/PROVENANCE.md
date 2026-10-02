# Provenance: Trotterized TFIM Simulation

- **Pattern source**: the standard first-order Trotter-Suzuki decomposition for a transverse-field
  Ising Hamiltonian (ZZ interaction via CX-RZ-CX, X field via RX), as presented in Qiskit's own
  tutorials and standard quantum simulation references (Lloyd 1996; Nielsen & Chuang Section 4.7).
- **License of source pattern**: Apache-2.0 (Qiskit project).
- **Modifications from any single upstream reference**: parameterized over arbitrary chain length,
  coupling `J`, field strength `h`, total time, and step count, rather than a single hardcoded
  example; includes a from-scratch classical reference implementation
  (`exact_tfim_hamiltonian`) used only for testing, not part of the quantum algorithm itself.
- **Verification**: compared the Trotterized circuit's final statevector against an exact
  classical reference computed via `scipy.linalg.expm` on the dense Hamiltonian matrix (tractable
  only for the small spin counts used here). Fidelity converges monotonically toward 1 as Trotter
  step count increases (0.50 at 1 step -> 0.91 at 2 -> 0.987 at 5 -> 0.9992 at 20 -> 0.99997 at
  100), which is itself the correctness signal: a sign error in the RZ/RX angles would not produce
  monotonic convergence to 1. See `metadata.yaml`'s `benchmarks` and `test_qiskit_impl.py`'s
  `test_trotter_fidelity_converges_monotonically`.
- **A different testing shape than Grover's or QPE**: Trotterization is an approximation by
  construction, so there is no single exact target statevector to assert equality against. The
  test suite instead asserts a fidelity floor at a given step count plus monotonic convergence —
  still a fully deterministic, non-sampled check (no shots, no seeds), just not an equality check.
  See `docs/testing.md` for how this fits alongside the repo's other testing patterns.
