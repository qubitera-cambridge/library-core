"""Decomposition-Free Variational Quantum Linear Solver (DF-VQLS): solve
Ax = b variationally, without decomposing A into a linear combination of
unitaries, using overlap-estimation circuits (building on the Hadamard-test
primitive — see `algorithm_dependencies` in metadata.yaml) and a classical
optimizer loop.

This is a thin wrapper around the `df-vqls` package
(https://github.com/qubitera-cambridge/df-vqls-core), a separate, privately-
hosted, independently-tested library-core sibling project — not code
duplicated into this repo. See PROVENANCE.md and
docs/private-dependencies.md for why, and requirements-dfvqls.txt for how to
install it (requires access to qubitera-cambridge's private repositories).

The `df_vqls` import is deliberately lazy (inside functions, not at module
level) so this file can still be imported/discovered by the repo's
structural checks even where the private package isn't installed; its own
test file uses `pytest.importorskip("df_vqls")` for the same reason.
"""

from __future__ import annotations

import numpy as np


def solve(A, b, **kwargs):
    """Thin pass-through to df_vqls.DF_VQLS — see that package's own
    docstring for the full set of ansatz/optimizer/cost-function options."""
    import df_vqls

    return df_vqls.DF_VQLS(A, b, **kwargs)


def demo() -> dict:
    """Solve a small diagonal 2x2 system variationally and report convergence
    (function evaluations, whether the residual target was met), not just the
    final solution — a variational method's convergence behavior is part of
    its correctness story, the same way Trotter step count is for
    trotterized-tfim."""
    A = np.diag([0.8, 0.6])
    expected_direction = np.array([1.0, -0.3])
    b = A @ expected_direction

    x, result = solve(
        A, b, max_iter=30, cost_estimator="joint_conditional", residual_tolerance=1e-3
    )
    optimizer = result["Variational_optimizer"]

    # DF-VQLS recovers the solution direction up to normalization; compare
    # normalized vectors rather than assuming a specific scale/sign.
    x_normalized = x / np.linalg.norm(x)
    expected_normalized = expected_direction / np.linalg.norm(expected_direction)
    cosine_similarity = float(np.dot(x_normalized, expected_normalized))

    return {
        "description": "DF-VQLS variational solve of a 2x2 diagonal system",
        "parameters": {
            "A": A.tolist(),
            "b": b.tolist(),
            "max_iter": 30,
            "cost_estimator": "joint_conditional",
            "residual_tolerance": 1e-3,
        },
        "result": {
            "solution": x.tolist(),
            "expected_direction": expected_direction.tolist(),
            "cosine_similarity": cosine_similarity,
            "function_evaluations": optimizer["function_evaluations"],
            "target_met": bool(optimizer["target_met"]),
        },
    }


if __name__ == "__main__":
    result = demo()
    print(result["description"])
    r = result["result"]
    print("Solution:", r["solution"])
    print("Expected direction:", r["expected_direction"])
    print(f"Cosine similarity: {r['cosine_similarity']:.4f}")
    print(f"Function evaluations: {r['function_evaluations']}, target met: {r['target_met']}")
