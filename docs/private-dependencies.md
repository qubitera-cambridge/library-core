# Private sibling dependencies

A few library-core algorithms (`quantum-krylov-solver`, `df-vqls-solver`) are thin wrappers
around separate, privately-hosted `qubitera-cambridge` repositories
([`quantum-krylov-core`](https://github.com/qubitera-cambridge/quantum-krylov-core),
[`df-vqls-core`](https://github.com/qubitera-cambridge/df-vqls-core)) rather than code copied into
this repo — see each algorithm's `PROVENANCE.md` for why.

These are **not** third-party sources in the `docs/SOURCES.md` sense — they're sibling projects
under the same org, already independently tested. They're documented here specifically because
they're private, which has real consequences for how this repo's tests and CI work:

## What this means in practice

- `requirements-krylov.txt` / `requirements-dfvqls.txt` pin these packages via
  `git+ssh://git@github.com/qubitera-cambridge/...@<commit>` URLs, which only resolve for someone
  with SSH (or an authenticated HTTPS credential helper) access to those private repos.
- `tox.ini` defines `krylov` and `dfvqls` environments for them, **deliberately excluded from
  `envlist`** — so a plain `tox` run, and the default public CI matrix in
  `.github/workflows/ci.yml`, never try to install them and never fail for lack of access. Run
  them explicitly (`tox -e krylov`, `tox -e dfvqls`) if you have access.
- Each wrapper's `qiskit_impl.py` imports the private package lazily (inside functions, not at
  module level), and its `test_qiskit_impl.py` calls `pytest.importorskip("quantum_krylov")` /
  `pytest.importorskip("df_vqls")` — the same pattern already used for optional SDKs (see
  `docs/testing.md`), just applied to "not installed because no access" instead of "not installed
  because it's a different framework." Either way, the default `qiskit`/`cirq` test runs report
  these as cleanly skipped, not a collection error.
- `tests/test_repo_structure.py`'s structural checks (schema validation, path existence,
  `algorithm_dependencies` references) still run and pass for these algorithms without needing the
  private packages installed — only the actual numerical correctness tests need access.

## Deliberately not done

No cross-repo CI credential (a deploy key or PAT granting library-core's public CI access to
these private repos) has been set up. That's a real security/access decision — who gets a secret
that can read private org repos — that shouldn't be made unilaterally; it's a reasonable next step
if these wrappers are worth testing centrally rather than relying on whoever has access to run
`tox -e krylov`/`tox -e dfvqls` locally before merging a change to them.
