# Provenance: Quantum Phase Estimation

- **Pattern source**: the standard QPE construction (Hadamards on a counting register,
  controlled-U^(2^k) applications, inverse QFT, measure) as presented in Nielsen & Chuang and
  demonstrated in Qiskit's own tutorials. Written against Qiskit 2.x's current API
  (`qiskit.circuit.library.QFTGate`) rather than copied from any single tutorial file, since older
  tutorial code uses the now-deprecated `QFT` class.
- **License of source pattern**: Apache-2.0 (Qiskit project).
- **Modifications from any single upstream reference**: parameterized over an arbitrary `theta`
  (demonstrated via a single-qubit phase gate `P(2*pi*theta)` with eigenstate `|1>`) and an
  arbitrary counting-register size, rather than a single hardcoded example.
- **Verification**: ran against `qiskit_aer.AerSimulator` and `qiskit.quantum_info.Statevector`
  for exactly-representable theta values (0, 1/8, 3/8, 5/8, 7/8 at n=3; 5/16 at n=4) — each
  concentrates probability 1.0 on the exact expected bitstring, an exact equality check rather
  than a threshold, since QPE's output is genuinely deterministic when theta fits exactly in the
  counting register's precision. Also verified non-exactly-representable theta values (0.1, 0.3,
  0.2) correctly peak at the nearest n-bit representable value. See `metadata.yaml`'s
  `benchmarks` and `test_qiskit_impl.py`.
- **A real bug caught during verification**: an early version of the test suite asserted directly
  on `Statevector(circuit).probabilities_dict()` without marginalizing out the target/eigenstate
  qubit, so expected 3-bit bitstrings like `"011"` were compared against the full circuit's 4-bit
  bitstrings (e.g. `"1011"`) and every exact-match test failed. Fixed by using
  `probabilities_dict(qargs=range(num_counting_qubits))` to marginalize to just the counting
  register before comparing.
