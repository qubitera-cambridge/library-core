"""Correctness tests for Grover's algorithm, colocated with its implementation.

Prefer exact Statevector assertions over sampled/shot-based ones wherever possible
so correctness checks are deterministic, not statistical — no flakiness, no seeds
to manage. One seeded AerSimulator smoke test covers the measurement/sampling path
itself.
"""

import importlib.util
import math
from pathlib import Path

import pytest
from qiskit.quantum_info import Statevector

# Load the sibling implementation module by explicit path rather than a plain
# `import qiskit_impl` — many algorithms across this repo will name their main
# file the same thing (e.g. every Qiskit-based algorithm's `qiskit_impl.py`),
# and a plain import would collide via sys.modules once more than one such
# test runs in the same pytest session.
_impl_path = Path(__file__).parent / "qiskit_impl.py"
_spec = importlib.util.spec_from_file_location("grovers_algorithm.qiskit_impl", _impl_path)
_qiskit_impl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_qiskit_impl)

build_grover_circuit = _qiskit_impl.build_grover_circuit
build_oracle = _qiskit_impl.build_oracle
optimal_iterations = _qiskit_impl.optimal_iterations


@pytest.mark.parametrize(
    "num_qubits,marked_states",
    [
        (3, ["011"]),
        (3, ["011", "100"]),
        (4, ["0110"]),
        (5, ["01011", "10110", "11111"]),
    ],
)
def test_oracle_flips_phase_from_superposition(num_qubits, marked_states):
    sv = Statevector.from_label("0" * num_qubits)
    for q in range(num_qubits):
        sv = sv.evolve(_h_on(num_qubits, q))
    oracle = build_oracle(num_qubits, marked_states).decompose(reps=5)
    sv = sv.evolve(oracle)

    n_items = 2**num_qubits
    expected_amp = 1 / math.sqrt(n_items)
    for i, amp in enumerate(sv.data):
        bitstring = format(i, f"0{num_qubits}b")
        expected_sign = -1 if bitstring in marked_states else 1
        assert amp.real == pytest.approx(expected_sign * expected_amp, abs=1e-9)
        assert amp.imag == pytest.approx(0, abs=1e-9)


def _h_on(num_qubits, qubit):
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(num_qubits)
    qc.h(qubit)
    return qc


@pytest.mark.parametrize(
    "num_qubits,num_marked,expected_iterations",
    [
        (3, 1, 2),
        (3, 2, 1),
        (4, 1, 3),
        (5, 3, 2),
    ],
)
def test_optimal_iterations_matches_known_values(num_qubits, num_marked, expected_iterations):
    assert optimal_iterations(num_qubits, num_marked) == expected_iterations


@pytest.mark.parametrize(
    "num_qubits,marked_states,min_success_probability",
    [
        (3, ["011"], 0.94),
        (3, ["011", "100"], 0.99),
        (4, ["0110"], 0.90),
        (5, ["01011", "10110", "11111"], 0.90),
    ],
)
def test_full_circuit_amplifies_marked_states(num_qubits, marked_states, min_success_probability):
    """Exact statevector check that Grover's amplifies marked states above the
    theoretical floor — no shot sampling, so no flakiness."""
    circuit = build_grover_circuit(num_qubits, marked_states)
    circuit.remove_final_measurements()
    sv = Statevector(circuit.decompose(reps=6))
    probs = sv.probabilities_dict()
    success_probability = sum(p for state, p in probs.items() if state in marked_states)
    assert success_probability >= min_success_probability


@pytest.mark.slow
def test_measurement_smoke_test_with_seeded_simulator():
    """One seeded, sampled end-to-end check covering the measurement/backend path
    that the exact-statevector tests above don't exercise."""
    from qiskit_aer import AerSimulator

    num_qubits, marked_states = 3, ["011", "100"]
    circuit = build_grover_circuit(num_qubits, marked_states).decompose(reps=5)

    sim = AerSimulator(seed_simulator=42)
    result = sim.run(circuit, shots=2000, seed_simulator=42).result()
    counts = result.get_counts()

    hits = sum(c for state, c in counts.items() if state in marked_states)
    assert hits / 2000 >= 0.95
