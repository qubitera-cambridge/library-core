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
2. Each test file loads its sibling implementation via `importlib.util.spec_from_file_location` +
   `module_from_spec`/`exec_module`, rather than a plain `from qiskit_impl import ...`. This is
   what actually prevents collisions: `module_from_spec`/`exec_module` never registers into
   `sys.modules` at all, so two different `qiskit_impl.py` files load as fully independent objects
   regardless of what string name you give the spec — the name itself (e.g.
   `"grovers_algorithm.qiskit_impl"`) is just a label, not what's doing the work. (A plain
   `import qiskit_impl`, by contrast, genuinely would collide through `sys.modules` once more than
   one same-named module is imported in the same session — that's the failure mode this pattern
   avoids.) Copy this pattern (see `algorithms/oracular/grovers-algorithm/test_qiskit_impl.py`)
   for every new algorithm's tests.
3. A missing optional SDK must not take down the whole suite. `pyproject.toml` sets
   `--continue-on-collection-errors` so one algorithm's test file failing to import (e.g. a Cirq
   algorithm's test when Cirq isn't installed) doesn't abort every other test in the same `pytest`
   invocation — but the failing file still reports as a collection *error*, not a clean skip. For
   any test file whose imports depend on an SDK that isn't a hard requirement of the whole repo,
   add `pytest.importorskip("cirq")` (or whichever package) at the top of the file so it reports
   as skipped instead.

## Running tests

```bash
# Everything
python3 -m pytest

# Fast subset only — skips sampled/simulator-backed tests marked @pytest.mark.slow
python3 -m pytest -m "not slow"

# Just the structural/schema checks (fast, always worth running)
python3 -m pytest tests/test_repo_structure.py

# Just one algorithm
python3 -m pytest algorithms/oracular/grovers-algorithm/
```

Mark any sampled/simulator-backed test (not exact-statevector) with `@pytest.mark.slow` — see
`test_measurement_smoke_test_with_seeded_simulator` in Grover's test file. This costs nothing
while every test runs in under a second, but establishes the convention before an algorithm with a
genuinely slow simulator run (larger qubit counts, a classical-optimizer loop) lands.

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
exec scripts/run_changed_algorithm_tests.sh $(git diff --cached --name-only --diff-filter=ACMR)
```

Use `ACMR` (Added/Copied/Modified/**Renamed**), not `ACM` — dropping `R` silently excludes renamed
files from the staged-file list, which means renaming a test or implementation file would commit
with zero verification under this fallback.

## CI

`.github/workflows/ci.yml` runs the full suite (`python3 -m pytest`) on every push and pull
request. **The local pre-commit hook is a fast first line of defense, not the enforcement
mechanism** — it's opt-in per clone (nothing runs it until someone runs `pre-commit install`),
and `git commit --no-verify` bypasses it trivially. CI is what actually guarantees a merged change
was checked. Once this repo has a remote with multiple contributors, turn on branch protection
requiring the CI job to pass before merging.

## Known gaps — not yet handled

This architecture was designed and verified against exactly one algorithm (Grover's, Qiskit,
reversible circuit with a single final measurement). It does not yet have an answer for:

- **Non-deterministic / statistical correctness** (VQE, QAOA, anything judged by an approximation
  ratio or convergence within tolerance rather than an exact target state). The
  exact-statevector-first principle above assumes there *is* one deterministic target — these
  algorithms don't have that, and what the shot-based test pattern should look like for them
  (sizing shots/tolerance, picking a known-answer small instance to validate against) hasn't been
  worked out.
- **Mid-circuit measurement with classical feedback** (teleportation, iterative phase estimation,
  quantum error correction). `Statevector(circuit).evolve(...)` only works for unitary-only
  circuits — there's no established pattern here yet for testing a circuit whose later gates
  depend on an earlier measurement outcome.
- **Non-Qiskit SDKs.** Everything above is written in Qiskit-specific terms (`Statevector` is a
  Qiskit class). Cirq's equivalent (`cirq.final_state_vector`) has its own conventions that
  haven't been mapped to this doc yet.
- **Qubit counts beyond exact-simulation tractability.** Exact statevector simulation is
  `O(2^n)` memory — this breaks down well before 30 qubits. No ceiling is documented, and nothing
  stops a future algorithm's test from trying to allocate more memory than CI has.
- **Multi-SDK dependency isolation.** All dependencies currently live in one flat
  `requirements-dev.txt`. This is a known, deliberately deferred architecture decision — see the
  comment in `requirements-dev.txt` — to be resolved before the first non-Qiskit algorithm lands,
  not after.
- **Benchmark claims aren't automatically re-verified.** `metadata.yaml`'s `benchmarks` field now
  requires a numeric `value` (not prose) specifically so this is possible later, but nothing yet
  recomputes a benchmark from a test run and flags drift from what's recorded.

Don't write speculative guidance for these until a real algorithm needing one actually lands —
but don't assume the principles above silently cover them either.
