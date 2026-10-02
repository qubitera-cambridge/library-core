"""Correctness tests for Quantum Phase Estimation, colocated with its
implementation. Prefer exact Statevector/probability assertions over sampled
ones — for theta values exactly representable in the counting register, QPE's
output distribution is deterministic (100% on one bitstring), so these need no
shot sampling or seeds at all.
"""

import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("qiskit")

from qiskit.quantum_info import Statevector

_impl_path = Path(__file__).parent / "qiskit_impl.py"
_spec = importlib.util.spec_from_file_location("quantum_phase_estimation.qiskit_impl", _impl_path)
_qiskit_impl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_qiskit_impl)

build_qpe_circuit = _qiskit_impl.build_qpe_circuit
nearest_representable_theta = _qiskit_impl.nearest_representable_theta


@pytest.mark.parametrize(
    "num_counting_qubits,theta,expected_bitstring",
    [
        (3, 0.0, "000"),
        (3, 1 / 8, "001"),
        (3, 3 / 8, "011"),
        (3, 5 / 8, "101"),
        (3, 7 / 8, "111"),
        (4, 5 / 16, "0101"),
    ],
)
def test_exact_theta_concentrates_on_expected_bitstring(num_counting_qubits, theta, expected_bitstring):
    """For theta exactly representable in the counting register, QPE's final
    state (pre-measurement) has probability 1 on exactly one bitstring — an
    exact equality check, not a threshold."""
    circuit = build_qpe_circuit(num_counting_qubits, theta)
    circuit.remove_final_measurements()
    sv = Statevector(circuit.decompose(reps=6))
    # Marginalize to just the counting register — the full statevector's
    # bitstrings also include the fixed target/eigenstate qubit.
    probs = sv.probabilities_dict(qargs=range(num_counting_qubits))
    assert probs[expected_bitstring] == pytest.approx(1.0, abs=1e-9)


@pytest.mark.parametrize(
    "num_counting_qubits,theta",
    [
        (3, 0.1),
        (3, 0.3),
        (4, 0.2),
    ],
)
def test_inexact_theta_peaks_at_nearest_representable_value(num_counting_qubits, theta):
    """For theta not exactly representable, QPE should still peak at the
    nearest n-bit value — not an exact match, but still a deterministic
    statevector-probability check, no sampling needed."""
    circuit = build_qpe_circuit(num_counting_qubits, theta)
    circuit.remove_final_measurements()
    sv = Statevector(circuit.decompose(reps=6))
    # Marginalize to just the counting register — the full statevector's
    # bitstrings also include the fixed target/eigenstate qubit.
    probs = sv.probabilities_dict(qargs=range(num_counting_qubits))

    nearest = nearest_representable_theta(num_counting_qubits, theta)
    nearest_bitstring = format(round(nearest * 2**num_counting_qubits), f"0{num_counting_qubits}b")

    top_bitstring = max(probs, key=probs.get)
    assert top_bitstring == nearest_bitstring


@pytest.mark.parametrize(
    "num_counting_qubits,theta,expected",
    [
        (3, 0.1, 0.125),
        (3, 0.3, 0.25),
        (3, 0.9, 0.875),
        (4, 0.2, 0.1875),
    ],
)
def test_nearest_representable_theta(num_counting_qubits, theta, expected):
    assert nearest_representable_theta(num_counting_qubits, theta) == pytest.approx(expected)


@pytest.mark.slow
def test_measurement_smoke_test_with_seeded_simulator():
    from qiskit_aer import AerSimulator

    circuit = build_qpe_circuit(3, 3 / 8).decompose(reps=6)
    sim = AerSimulator(seed_simulator=7)
    result = sim.run(circuit, shots=1000, seed_simulator=7).result()
    counts = result.get_counts()
    assert counts == {"011": 1000}
