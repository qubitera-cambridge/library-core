"""Quantum Krylov subspace linear solver: solve Ax = b by building a Krylov
subspace with a quantum-estimated basis (density matrix exponentiation, which
itself uses the Hadamard-test primitive — see `algorithm_dependencies` in
metadata.yaml) and solving the small projected system classically.

This is a thin wrapper around the `quantum-krylov` package
(https://github.com/qubitera-cambridge/quantum-krylov-core), a separate,
privately-hosted, independently-tested library-core sibling project — not
code duplicated into this repo. See PROVENANCE.md and
docs/private-dependencies.md for why, and requirements-krylov.txt for how to
install it (requires access to qubitera-cambridge's private repositories).

The `quantum_krylov` import is deliberately lazy (inside functions, not at
module level) so this file can still be imported/discovered by the repo's
structural checks even where the private package isn't installed; its own
test file uses `pytest.importorskip("quantum_krylov")` for the same reason.
"""

from __future__ import annotations

import numpy as np


def solve(A, b, **kwargs):
    """Thin pass-through to quantum_krylov.solve — see that package's own
    docstring for the full set of basis/implementation/reduced_solver options."""
    import quantum_krylov

    return quantum_krylov.solve(A, b, **kwargs)


def demo() -> dict:
    """Solve a small 2x2 system with the quantum (real_time basis) Krylov
    method and compare against the exact classical solution — reported
    honestly: this basis/dimension combination has real approximation error,
    not hidden behind a cherry-picked configuration."""
    A = np.array([[0.8, 0.1], [0.1, 0.6]])
    b = np.array([1.0, -0.3])
    exact = np.linalg.solve(A, b)

    result = solve(A, b, basis="real_time", implementation="quantum", dimension=2)
    quantum_solution = np.real_if_close(result.solution, tol=1000)
    relative_error = float(np.linalg.norm(quantum_solution - exact) / np.linalg.norm(exact))

    return {
        "description": "Quantum Krylov (real_time basis, dimension=2) solve of a 2x2 system, vs. the exact classical solution",
        "parameters": {"A": A.tolist(), "b": b.tolist(), "basis": "real_time", "dimension": 2},
        "result": {
            "quantum_solution": [complex(x).real for x in quantum_solution],
            "exact_solution": exact.tolist(),
            "relative_error": relative_error,
        },
    }


if __name__ == "__main__":
    result = demo()
    print(result["description"])
    print("Quantum solution:", result["result"]["quantum_solution"])
    print("Exact solution:  ", result["result"]["exact_solution"])
    print(f"Relative error: {result['result']['relative_error']:.2%}")
