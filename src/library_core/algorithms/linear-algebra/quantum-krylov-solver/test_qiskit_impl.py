"""Correctness tests for the quantum Krylov solver wrapper.

Requires the private `quantum-krylov` package (see requirements-krylov.txt) —
reports as cleanly skipped, not a collection error, when it isn't installed
(e.g. in the default public CI matrix, which doesn't have access to
qubitera-cambridge's private repositories). See docs/private-dependencies.md.
"""

import importlib.util
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("quantum_krylov")

_impl_path = Path(__file__).parent / "qiskit_impl.py"
_spec = importlib.util.spec_from_file_location("quantum_krylov_solver.qiskit_impl", _impl_path)
_qiskit_impl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_qiskit_impl)

solve = _qiskit_impl.solve
demo = _qiskit_impl.demo


def test_classical_implementation_matches_numpy_exactly():
    """The package's own classical (non-quantum) implementation should
    reproduce numpy's solve exactly, for any basis — this is this package's
    own correctness guarantee, not something library-core re-derives; this
    test exists so a future quantum-krylov-core upgrade that broke it would
    be caught here too, not just in that package's own suite."""
    A = np.array([[0.8, 0.1], [0.1, 0.6]])
    b = np.array([1.0, -0.3])
    result = solve(A, b, basis="real_time", implementation="classical", dimension=2)
    np.testing.assert_allclose(result.solution, np.linalg.solve(A, b), atol=1e-10)


def test_demo_returns_expected_shape_and_bounded_error():
    result = demo()
    assert isinstance(result["description"], str) and result["description"]
    r = result["result"]
    assert len(r["quantum_solution"]) == 2
    assert len(r["exact_solution"]) == 2
    # Real_time/dimension=2 on this system has known, non-negligible
    # approximation error (confirmed during development: ~7%) - bound it
    # loosely rather than asserting near-exactness, which would be false.
    assert 0 <= r["relative_error"] < 0.25


def test_demo_is_deterministic():
    first = demo()
    second = demo()
    assert first["result"]["quantum_solution"] == second["result"]["quantum_solution"]
