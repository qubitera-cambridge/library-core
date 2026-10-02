"""The Hadamard test: estimate Re or Im <psi|U|psi> for a unitary U and state
|psi>, using one ancilla qubit and a controlled-U. A basic interference/
overlap-estimation subroutine other algorithms build on (e.g. quantum-krylov's
density matrix exponentiation, df-vqls's overlap estimation) — see
`algorithm_dependencies` in metadata.yaml for which library-core algorithms
reference this one.

Adapted from the standard construction in Nielsen & Chuang and Qiskit's own
tutorials (Apache-2.0). See PROVENANCE.md.
"""

from __future__ import annotations

import math

from qiskit import QuantumCircuit


def build_hadamard_test_circuit(controlled_u: QuantumCircuit, imaginary: bool = False) -> QuantumCircuit:
    """`controlled_u` must be a circuit on n qubits that will be applied
    controlled on the ancilla (qubit 0 of the returned circuit maps to the
    ancilla; qubits 1..n are the system, prepared in |0...0> by default —
    compose a state-prep circuit onto the system qubits first if a different
    |psi> is needed).
    """
    n_system = controlled_u.num_qubits
    qc = QuantumCircuit(n_system + 1, 1)
    ancilla = 0
    system = list(range(1, n_system + 1))

    qc.h(ancilla)
    if imaginary:
        qc.sdg(ancilla)
    qc.compose(controlled_u.control(1, annotated=False), qubits=[ancilla] + system, inplace=True)
    qc.h(ancilla)
    qc.measure(ancilla, 0)
    return qc


def estimate_overlap(counts: dict, shots: int) -> float:
    """<Re or Im><psi|U|psi> = P(0) - P(1) on the ancilla."""
    p0 = counts.get("0", 0) / shots
    p1 = counts.get("1", 0) / shots
    return p0 - p1


def demo() -> dict:
    """Estimate Re<0|Rz(theta)|0> for a few theta values, comparing against
    the exact analytic value cos(theta/2)."""
    from qiskit_aer import AerSimulator

    shots = 4000
    seed = 11
    results = []
    for theta_deg in [0, 60, 120, 180]:
        theta = math.radians(theta_deg)
        controlled_u = QuantumCircuit(1)
        controlled_u.rz(theta, 0)

        circuit = build_hadamard_test_circuit(controlled_u, imaginary=False).decompose(reps=5)
        sim = AerSimulator(seed_simulator=seed)
        counts = sim.run(circuit, shots=shots, seed_simulator=seed).result().get_counts()
        estimate = estimate_overlap(counts, shots)
        exact = math.cos(theta / 2)
        results.append(
            {
                "theta_deg": theta_deg,
                "estimate": estimate,
                "exact": exact,
                "abs_error": abs(estimate - exact),
            }
        )

    return {
        "description": "Hadamard test estimates of Re<0|Rz(theta)|0> = cos(theta/2) for several theta",
        "parameters": {"shots": shots, "seed": seed},
        "result": {"estimates": results},
    }


if __name__ == "__main__":
    result = demo()
    print(result["description"])
    for row in result["result"]["estimates"]:
        print(f"  theta={row['theta_deg']:4d}deg  estimate={row['estimate']:.4f}  exact={row['exact']:.4f}  abs_error={row['abs_error']:.4f}")
