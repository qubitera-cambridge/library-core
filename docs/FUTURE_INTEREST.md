# Future interest

Repos, libraries, and ideas worth revisiting for QuAlgLib, but not yet ready for the license-check
/ vendoring pipeline in `docs/SOURCES.md` — usually because an open design question needs settling
first, or because no one's done even a first-pass license/fit check yet. Low-friction by design:
an entry here is a pointer and a reason, not a commitment.

Once an entry's blocking question is resolved and it's worth seriously evaluating, promote it to
`docs/SOURCES.md` and run it through the process documented there.

## Entries

- **[lambeq](https://github.com/quantinuum/lambeq)** (Quantinuum) — QNLP framework (DisCoCat-based
  circuit construction + training), Apache-2.0. Not a named algorithm with a proven
  complexity-theoretic speedup, so it doesn't fit the current `src/library_core/algorithms/` taxonomy or the
  exact-statevector testing pattern in `docs/testing.md` (which assumes deterministic, reversible
  circuits). Blocked on: deciding whether QuAlgLib's scope extends to heuristic/variational
  frameworks, and if so, what category (e.g. `quantum-nlp`) and testing approach
  (e.g. accuracy-within-tolerance rather than exact state checks) they'd use.
