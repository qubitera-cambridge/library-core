# Source ledger

Tracks upstream repos considered for QuAlgLib, their license, and whether/what we've pulled in.
Nothing gets copied in without a license check landing here first.

| Source | URL | License | Notes | Status |
|---|---|---|---|---|
| Qiskit | https://github.com/Qiskit/qiskit | Apache-2.0 | Core SDK; algorithm textbook/tutorials live in separate repos (qiskit-community-tutorials, etc.) | Grover's algorithm vendored (pattern-level, see `algorithms/oracular/grovers-algorithm/PROVENANCE.md`) |
| Classiq Library | https://github.com/Classiq/classiq-library | Apache-2.0 (notebooks) | Many notebooks require the proprietary `classiq` SDK/backend to actually synthesize circuits — check portability per-notebook before vendoring | Not yet vendored |
| DeltaKit | https://github.com/Deltakit | Apache-2.0 (verify per-repo) | QEC / decoder tooling, not really "algorithms" in the Shor/Grover sense — scope fit questionable | Under review |
| Quantum Algorithm Zoo | https://quantumalgorithmzoo.org/ | N/A (curated list, not code) | Use only as a taxonomy/index of algorithms + paper citations, not a code source | Reference only |

## Process for adding a source

1. Confirm the upstream license (check `LICENSE`/`COPYING` file, not just README claims).
2. If permissive (MIT/BSD/Apache-2.0): copy the specific algorithm file(s), preserve original
   copyright header, add an entry to `NOTICE` and a `PROVENANCE.md` in the target algorithm
   directory.
3. If copyleft (GPL/AGPL/LGPL): confirm the file can be isolated as its own subdirectory/module
   without forcing relicensing of unrelated code; document the obligation clearly; consider
   whether it's worth including at all.
4. If source-available/proprietary-backend (e.g. Classiq notebooks needing their cloud backend):
   flag as "requires external service" rather than a self-contained implementation.
