# Provenance: Grover's Algorithm

- **Pattern source**: Qiskit's own tutorials/textbook demonstrate this construction (oracle +
  diffusion operator, repeated for the optimal iteration count). This implementation is written
  against Qiskit 2.x's current API (`qiskit.circuit.library.grover_operator.grover_operator`,
  `MCMTGate`) rather than copied verbatim from any single tutorial file, since older tutorial code
  uses the now-deprecated `GroverOperator` class.
- **License of source pattern**: Apache-2.0 (Qiskit project).
- **Modifications from any single upstream reference**:
  - Custom `build_oracle` using a multi-controlled-Z phase oracle (ancilla-free), parameterized by
    an arbitrary list of marked bitstrings rather than a single hardcoded target.
  - `optimal_iterations` uses the exact rotation-angle formula
    (`theta = arcsin(sqrt(M/N))`, `t = round(pi/(4*theta) - 0.5)`) rather than the common
    small-angle approximation `pi/4 * sqrt(N/M)`, which was found during verification to overshoot
    for larger M/N ratios (see commit history / improvement_opportunities in metadata.yaml).
- **Verification**: Run against `qiskit_aer.AerSimulator` across n=3,4,5 qubits with 1-3 marked
  states; success rates 95-100%, matching Grover's theoretical bound. See `metadata.yaml`
  `benchmarks` for recorded runs.
