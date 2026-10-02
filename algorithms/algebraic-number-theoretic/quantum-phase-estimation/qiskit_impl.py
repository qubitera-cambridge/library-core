"""Quantum Phase Estimation (QPE): given a unitary U and one of its eigenstates
|psi> with eigenvalue e^{2*pi*i*theta}, estimate theta to n bits of precision
using n counting qubits and an inverse QFT.

This implementation demonstrates QPE on a single-qubit phase gate P(2*pi*theta)
with eigenstate |1>, the simplest standard textbook case — the phase gate's
eigenvalue *is* e^{2*pi*i*theta} by construction, so theta is whatever's passed
in, not something derived from a more complex unitary.

Adapted from the standard QPE construction described in Nielsen & Chuang and
Qiskit's own textbook/tutorials (Apache-2.0). See PROVENANCE.md.
"""

from __future__ import annotations

import math

from qiskit import QuantumCircuit
from qiskit.circuit.library import QFTGate


def build_qpe_circuit(num_counting_qubits: int, theta: float) -> QuantumCircuit:
    """Counting register is qubits [0, num_counting_qubits); the target
    (eigenstate) qubit is the last one. Counting qubit k controls a
    phase-gate application of angle 2*pi*theta*2^k onto the target.
    """
    target = num_counting_qubits
    qc = QuantumCircuit(num_counting_qubits + 1, num_counting_qubits)

    qc.x(target)  # prepare |1>, an eigenstate of P(phi) with eigenvalue e^{i*phi}
    qc.h(range(num_counting_qubits))
    for k in range(num_counting_qubits):
        angle = 2 * math.pi * theta * (2**k)
        qc.cp(angle, k, target)
    qc.append(QFTGate(num_counting_qubits).inverse(), range(num_counting_qubits))
    qc.measure(range(num_counting_qubits), range(num_counting_qubits))
    return qc


def nearest_representable_theta(num_counting_qubits: int, theta: float) -> float:
    """The theta value an n-bit counting register would round theta to."""
    n_bins = 2**num_counting_qubits
    return round(theta * n_bins) % n_bins / n_bins


if __name__ == "__main__":
    from qiskit_aer import AerSimulator

    num_counting_qubits = 3
    sim = AerSimulator()

    print("Exactly representable theta values (should concentrate ~100%):")
    for theta in [0.0, 1 / 8, 3 / 8, 5 / 8, 7 / 8]:
        circuit = build_qpe_circuit(num_counting_qubits, theta)
        counts = sim.run(circuit.decompose(reps=6), shots=2000).result().get_counts()
        top_bitstring = max(counts, key=counts.get)
        print(f"  theta={theta:.3f}  top_bitstring={top_bitstring}  counts={counts}")

    print("\nNon-exactly-representable theta (should peak near nearest n-bit value):")
    for theta in [0.1, 0.3]:
        circuit = build_qpe_circuit(num_counting_qubits, theta)
        counts = sim.run(circuit.decompose(reps=6), shots=4000).result().get_counts()
        top_bitstring = max(counts, key=counts.get)
        nearest = nearest_representable_theta(num_counting_qubits, theta)
        print(f"  theta={theta:.3f}  nearest_representable={nearest:.3f}  top_bitstring={top_bitstring}")
