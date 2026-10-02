"""Correctness tests for Trotterized TFIM time evolution, colocated with its
implementation.

Trotterization is an approximation by construction, so there's no single exact
target statevector to assert equality against — unlike Grover's or QPE. The
correctness criterion here is instead: fidelity against an exact classically-
computed reference (via matrix exponential) must (a) already be high at a
modest step count, and (b) converge monotonically toward 1 as steps increase.
This is still a fully deterministic, non-sampled check — no shots, no seeds —
just a different shape of "exact" than equality against one target state.
"""

import importlib.util
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("qiskit")

from qiskit.quantum_info import Statevector
from scipy.linalg import expm

_impl_path = Path(__file__).parent / "qiskit_impl.py"
_spec = importlib.util.spec_from_file_location("trotterized_tfim.qiskit_impl", _impl_path)
_qiskit_impl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_qiskit_impl)

trotter_circuit = _qiskit_impl.trotter_circuit
exact_tfim_hamiltonian = _qiskit_impl.exact_tfim_hamiltonian


def _exact_evolution(num_spins, J, h, total_time):
    hamiltonian = exact_tfim_hamiltonian(num_spins, J, h)
    initial_state = np.zeros(2**num_spins, dtype=complex)
    initial_state[0] = 1.0
    return expm(-1j * hamiltonian * total_time) @ initial_state


def _fidelity(state_a, state_b):
    return abs(np.vdot(state_a, state_b)) ** 2


@pytest.mark.parametrize(
    "num_spins,J,h,total_time,steps,min_fidelity",
    [
        (3, 1.0, 0.5, 1.0, 20, 0.999),
        (3, 1.0, 0.5, 1.0, 100, 0.9999),
        (2, 1.0, 1.0, 0.5, 20, 0.999),
    ],
)
def test_trotter_fidelity_at_high_step_count(num_spins, J, h, total_time, steps, min_fidelity):
    exact_final = _exact_evolution(num_spins, J, h, total_time)
    circuit = trotter_circuit(num_spins, J, h, total_time, steps)
    trotter_final = Statevector(circuit).data
    assert _fidelity(exact_final, trotter_final) >= min_fidelity


def test_trotter_fidelity_converges_monotonically():
    """A real bug in the angle signs would NOT produce monotonic convergence —
    it would plateau well short of 1, or not approach 1 at all. This is the
    test that would have caught a sign error during development."""
    num_spins, J, h, total_time = 3, 1.0, 0.5, 1.0
    exact_final = _exact_evolution(num_spins, J, h, total_time)

    fidelities = []
    for steps in [1, 2, 5, 20, 100]:
        circuit = trotter_circuit(num_spins, J, h, total_time, steps)
        trotter_final = Statevector(circuit).data
        fidelities.append(_fidelity(exact_final, trotter_final))

    assert all(b >= a - 1e-9 for a, b in zip(fidelities, fidelities[1:])), (
        f"fidelity should increase monotonically (within tolerance) as steps increase: {fidelities}"
    )
    assert fidelities[-1] >= 0.9999
    assert fidelities[0] < fidelities[-1]


def test_zero_time_evolution_is_identity():
    """t=0 should leave the initial state unchanged regardless of step count —
    a cheap exact edge case that doesn't depend on Trotter error at all."""
    num_spins = 3
    circuit = trotter_circuit(num_spins, J=1.0, h=0.5, total_time=0.0, steps=10)
    sv = Statevector(circuit)
    probs = sv.probabilities_dict()
    assert probs["000"] == pytest.approx(1.0, abs=1e-9)


@pytest.mark.slow
def test_measurement_smoke_test_with_seeded_simulator():
    from qiskit_aer import AerSimulator

    circuit = trotter_circuit(3, J=1.0, h=0.5, total_time=1.0, steps=20)
    circuit.measure_all()
    sim = AerSimulator(seed_simulator=11)
    result = sim.run(circuit, shots=1000, seed_simulator=11).result()
    counts = result.get_counts()
    assert sum(counts.values()) == 1000
