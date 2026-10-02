"""Correctness tests for the Hadamard test, colocated with its implementation."""

import importlib.util
import math
from pathlib import Path

import pytest

pytest.importorskip("qiskit")

from qiskit.quantum_info import Statevector

_impl_path = Path(__file__).parent / "qiskit_impl.py"
_spec = importlib.util.spec_from_file_location("hadamard_test.qiskit_impl", _impl_path)
_qiskit_impl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_qiskit_impl)

build_hadamard_test_circuit = _qiskit_impl.build_hadamard_test_circuit
estimate_overlap = _qiskit_impl.estimate_overlap
demo = _qiskit_impl.demo


@pytest.mark.parametrize("theta_deg", [0, 30, 60, 90, 120, 180, 270])
@pytest.mark.parametrize("imaginary", [False, True])
def test_ancilla_probability_matches_exact_overlap(theta_deg, imaginary):
    """Exact statevector check: the ancilla's P(0)-P(1) should equal the
    analytic Re/Im<0|Rz(theta)|0> exactly, no sampling needed."""
    from qiskit import QuantumCircuit

    theta = math.radians(theta_deg)
    controlled_u = QuantumCircuit(1)
    controlled_u.rz(theta, 0)
    circuit = build_hadamard_test_circuit(controlled_u, imaginary=imaginary).decompose(reps=5)
    circuit.remove_final_measurements()

    sv = Statevector(circuit)
    probs = sv.probabilities_dict(qargs=[0])
    p0 = probs.get("0", 0.0)
    p1 = probs.get("1", 0.0)

    expected = math.cos(theta / 2) if not imaginary else -math.sin(theta / 2)
    assert (p0 - p1) == pytest.approx(expected, abs=1e-9)


def test_estimate_overlap_from_counts():
    assert estimate_overlap({"0": 750, "1": 250}, 1000) == pytest.approx(0.5)
    assert estimate_overlap({"0": 1000}, 1000) == pytest.approx(1.0)
    assert estimate_overlap({"1": 1000}, 1000) == pytest.approx(-1.0)


def test_demo_returns_expected_shape():
    result = demo()
    assert isinstance(result["description"], str) and result["description"]
    rows = result["result"]["estimates"]
    assert len(rows) == 4
    for row in rows:
        assert row["abs_error"] < 0.05  # well within sampling noise at 4000 shots


@pytest.mark.slow
def test_measurement_smoke_test_with_seeded_simulator():
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator

    controlled_u = QuantumCircuit(1)
    controlled_u.rz(math.pi / 3, 0)
    circuit = build_hadamard_test_circuit(controlled_u).decompose(reps=5)

    sim = AerSimulator(seed_simulator=5)
    counts = sim.run(circuit, shots=2000, seed_simulator=5).result().get_counts()
    estimate = estimate_overlap(counts, 2000)
    assert estimate == pytest.approx(math.cos(math.pi / 6), abs=0.05)
