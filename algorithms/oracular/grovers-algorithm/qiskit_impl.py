"""Grover's search algorithm: find a marked item in an unstructured search space
of N = 2^n items using O(sqrt(N)) oracle queries, versus O(N) classically.

Adapted from the Qiskit textbook / tutorials (Apache-2.0). See PROVENANCE.md.
"""

from __future__ import annotations

import math

from qiskit import QuantumCircuit
from qiskit.circuit.library import MCMTGate, ZGate
from qiskit.circuit.library.grover_operator import grover_operator
from qiskit.quantum_info import Statevector


def build_oracle(num_qubits: int, marked_states: list[str]) -> QuantumCircuit:
    """Phase-flip oracle that marks each bitstring in `marked_states` (MSB-first, as
    Qiskit prints them) by applying a controlled-Z pattern conditioned on that state.
    """
    qc = QuantumCircuit(num_qubits)
    for target in marked_states:
        rev_target = target[::-1]  # convert to little-endian for qubit ordering
        zero_indices = [i for i in range(num_qubits) if rev_target[i] == "0"]
        if zero_indices:
            qc.x(zero_indices)
        qc.compose(MCMTGate(ZGate(), num_qubits - 1, 1), inplace=True)
        if zero_indices:
            qc.x(zero_indices)
    return qc


def optimal_iterations(num_qubits: int, num_marked: int) -> int:
    """Number of Grover iterations that maximizes success probability.

    Uses the exact rotation angle theta = arcsin(sqrt(M/N)) rather than the
    small-angle approximation pi/4 * sqrt(N/M), which overshoots once M/N
    isn't small (e.g. N=8, M=2 optimizes at 1 iteration, not 2).
    """
    n_items = 2**num_qubits
    theta = math.asin(math.sqrt(num_marked / n_items))
    return max(1, round(math.pi / (4 * theta) - 0.5))


def build_grover_circuit(num_qubits: int, marked_states: list[str]) -> QuantumCircuit:
    oracle = build_oracle(num_qubits, marked_states)
    grover_op = grover_operator(oracle)
    iterations = optimal_iterations(num_qubits, len(marked_states))

    qc = QuantumCircuit(num_qubits)
    qc.h(range(num_qubits))
    for _ in range(iterations):
        qc.compose(grover_op, inplace=True)
    qc.measure_all()
    return qc


def demo() -> dict:
    """One concrete, reproducible run of this algorithm, for the documentation
    site to render — not a test. Returns a JSON-serializable dict:
      - description: str, one-line summary of what this run demonstrates
      - parameters: dict of the inputs used
      - result: dict of the outputs

    See docs/site-generation.md for the convention this follows.
    """
    from qiskit_aer import AerSimulator

    num_qubits = 3
    marked_states = ["011", "100"]
    shots = 2000
    seed = 42
    iterations = optimal_iterations(num_qubits, len(marked_states))

    circuit = build_grover_circuit(num_qubits, marked_states).decompose(reps=5)
    sim = AerSimulator(seed_simulator=seed)
    counts = sim.run(circuit, shots=shots, seed_simulator=seed).result().get_counts()
    hits = sum(c for state, c in counts.items() if state in marked_states)

    return {
        "description": (
            f"Searching {2**num_qubits} items for {len(marked_states)} marked "
            f"state(s) using {iterations} Grover iteration(s)"
        ),
        "parameters": {
            "num_qubits": num_qubits,
            "marked_states": marked_states,
            "iterations": iterations,
            "shots": shots,
            "seed": seed,
        },
        "result": {
            "counts": dict(counts),
            "success_rate": hits / shots,
        },
    }


if __name__ == "__main__":
    result = demo()
    print(result["description"])
    print("Parameters:", result["parameters"])
    print("Measurement counts:", result["result"]["counts"])
    print(f"Success rate: {result['result']['success_rate']:.2%}")
