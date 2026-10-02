# Testing architecture

## Principles

- **Tests live with their algorithm.** Each `algorithms/<category>/<algo>/` directory owns its
  own `test_*.py` alongside its implementation — no central test tree duplicating that structure.
  This keeps an algorithm's correctness self-contained and makes it obvious when one is untested.
- **Prefer exact statevector assertions over sampled ones.** Quantum circuits are probabilistic
  at measurement, but their statevector (pre-measurement) is deterministic. Asserting on
  `Statevector` probabilities catches correctness bugs with zero flakiness and no seeds to manage.
  Reserve sampled, shot-based tests for the one thing statevector tests can't cover: the actual
  measurement/backend path — and seed the simulator (`seed_simulator=...`) when you do.
- **A repo-wide structural suite catches drift.** `tests/test_repo_structure.py` validates every
  `metadata.yaml` against `schema/algorithm.schema.json`, checks `id`/`category` match the
  directory layout, confirms `PROVENANCE.md` exists, and confirms every path under
  `implementations` in metadata actually exists on disk. This is cheap (pure parsing, no
  simulation) so it always runs, regardless of what changed.

## Avoiding collisions at scale

Once there are hundreds of algorithms, many will share file basenames — most Qiskit-based
algorithms will have a `qiskit_impl.py` and a `test_qiskit_impl.py`. Two things prevent this from
breaking test collection:

1. `pyproject.toml` sets `addopts = "--import-mode=importlib"`, so pytest can collect multiple
   `test_qiskit_impl.py` files from different directories without the classic "import file
   mismatch" error that plain rootdir-based imports hit when there's no `__init__.py`.
2. Each test file loads its sibling implementation via `importlib.util.spec_from_file_location`
   with a unique module name (e.g. `"grovers_algorithm.qiskit_impl"`), rather than a plain
   `from qiskit_impl import ...`, which would otherwise collide through `sys.modules` once more
   than one same-named module is imported in the same pytest session. Copy this pattern (see
   `algorithms/oracular/grovers-algorithm/test_qiskit_impl.py`) for every new algorithm's tests.

## Running tests

```bash
# Everything
python3 -m pytest

# Just the structural/schema checks (fast, always worth running)
python3 -m pytest tests/test_repo_structure.py

# Just one algorithm
python3 -m pytest algorithms/oracular/grovers-algorithm/
```

## Pre-commit hook

`.pre-commit-config.yaml` wires up `scripts/run_changed_algorithm_tests.sh`, which:

1. Always runs `tests/test_repo_structure.py` (cheap, catches metadata drift).
2. Inspects the staged files to find which algorithm directories actually changed
   (`scripts/changed_algorithm_dirs.py`) and runs pytest scoped to just those — not the full
   simulator-backed suite — so commits stay fast as the collection grows into the hundreds or
   thousands of algorithms.

Setup:

```bash
pip install -r requirements-dev.txt
pre-commit install
```

If you'd rather not take the `pre-commit` framework dependency, `scripts/run_changed_algorithm_tests.sh`
is a plain script — you can call it directly from `.git/hooks/pre-commit` with the staged file list:

```bash
#!/usr/bin/env bash
exec scripts/run_changed_algorithm_tests.sh $(git diff --cached --name-only --diff-filter=ACM)
```
