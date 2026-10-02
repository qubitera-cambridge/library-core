"""Trotterized time evolution of the Transverse-Field Ising Model (TFIM):
H = -J * sum_i Z_i Z_{i+1} - h * sum_i X_i

Approximates exp(-i*H*t) via first-order Trotter-Suzuki decomposition:
exp(-i*H*t) ~= [exp(-i*H_zz*dt) * exp(-i*H_x*dt)]^steps, dt = t/steps.

This is an approximate algorithm by construction — correctness here means
"converges to the exact evolution as steps increases," verified against an
exact matrix-exponential reference computed classically (tractable only
because the demo uses a handful of spins; that's the whole point of needing a
quantum computer for larger systems).

Adapted from the standard Trotter-Suzuki simulation pattern described in
Qiskit's own tutorials (Apache-2.0). See PROVENANCE.md.
"""

from __future__ import annotations

from qiskit import QuantumCircuit


def trotter_circuit(num_spins: int, J: float, h: float, total_time: float, steps: int) -> QuantumCircuit:
    """ZZ interaction term via CX-RZ-CX; X field term via RX. Angle signs are
    derived from Rz(theta) = exp(-i*theta/2*Z) and Rx(theta) = exp(-i*theta/2*X):
    to apply exp(+i*J*dt*Z_iZ_{i+1}) (from -(-J) in the Hamiltonian) we need
    theta = -2*J*dt, and likewise theta = -2*h*dt for the X term.
    """
    dt = total_time / steps
    qc = QuantumCircuit(num_spins)
    for _ in range(steps):
        for i in range(num_spins - 1):
            qc.cx(i, i + 1)
            qc.rz(-2 * J * dt, i + 1)
            qc.cx(i, i + 1)
        for i in range(num_spins):
            qc.rx(-2 * h * dt, i)
    return qc


def exact_tfim_hamiltonian(num_spins: int, J: float, h: float):
    """Dense matrix form of H, for classical reference comparison only —
    exponential in num_spins, so this is strictly a small-system test/reference
    tool, not part of the quantum algorithm itself."""
    import numpy as np

    identity = np.eye(2)
    pauli_x = np.array([[0, 1], [1, 0]])
    pauli_z = np.array([[1, 0], [0, -1]])

    def kron_chain(ops):
        result = np.array([[1.0]])
        for op in ops:
            result = np.kron(result, op)
        return result

    dim = 2**num_spins
    hamiltonian = np.zeros((dim, dim), dtype=complex)
    for i in range(num_spins - 1):
        ops = [identity] * num_spins
        ops[i] = pauli_z
        ops[i + 1] = pauli_z
        hamiltonian += -J * kron_chain(ops)
    for i in range(num_spins):
        ops = [identity] * num_spins
        ops[i] = pauli_x
        hamiltonian += -h * kron_chain(ops)
    return hamiltonian


if __name__ == "__main__":
    import numpy as np
    from qiskit.quantum_info import Statevector
    from scipy.linalg import expm

    num_spins, J, h, total_time = 3, 1.0, 0.5, 1.0
    hamiltonian = exact_tfim_hamiltonian(num_spins, J, h)
    initial_state = np.zeros(2**num_spins, dtype=complex)
    initial_state[0] = 1.0  # |000>
    exact_final_state = expm(-1j * hamiltonian * total_time) @ initial_state

    print(f"TFIM chain: {num_spins} spins, J={J}, h={h}, t={total_time}")
    for steps in [1, 2, 5, 20, 100]:
        circuit = trotter_circuit(num_spins, J, h, total_time, steps)
        trotter_state = Statevector(circuit).data
        fidelity = abs(np.vdot(exact_final_state, trotter_state)) ** 2
        print(f"  steps={steps:4d}  fidelity={fidelity:.6f}")
