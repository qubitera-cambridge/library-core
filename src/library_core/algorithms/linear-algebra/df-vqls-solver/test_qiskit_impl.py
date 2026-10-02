"""Correctness tests for the DF-VQLS solver wrapper.

Requires the private `df-vqls` package (see requirements-dfvqls.txt) —
reports as cleanly skipped, not a collection error, when it isn't installed
(e.g. in the default public CI matrix, which doesn't have access to
qubitera-cambridge's private repositories). See docs/private-dependencies.md.
"""

import importlib.util
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("df_vqls")

_impl_path = Path(__file__).parent / "qiskit_impl.py"
_spec = importlib.util.spec_from_file_location("df_vqls_solver.qiskit_impl", _impl_path)
_qiskit_impl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_qiskit_impl)

demo = _qiskit_impl.demo


@pytest.mark.slow
def test_demo_converges_to_the_correct_solution_direction():
    result = demo()
    r = result["result"]
    assert r["target_met"] is True
    # DF-VQLS recovers direction, not an absolute scale/sign - cosine
    # similarity close to 1 is the right correctness check, not exact
    # solution equality.
    assert r["cosine_similarity"] == pytest.approx(1.0, abs=1e-3)
    assert r["function_evaluations"] < 30


@pytest.mark.slow
def test_demo_returns_expected_shape():
    result = demo()
    assert isinstance(result["description"], str) and result["description"]
    r = result["result"]
    assert len(r["solution"]) == 2
    assert isinstance(r["function_evaluations"], int)
