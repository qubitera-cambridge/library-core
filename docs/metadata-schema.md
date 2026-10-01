# Algorithm metadata schema

Every algorithm directory under `algorithms/**/<algorithm-slug>/` carries a `metadata.yaml`
alongside its `PROVENANCE.md`. This is the structured layer an AI traverses first to shortlist
candidates for a problem, before reading any actual code. JSON Schema for validation lives at
`schema/algorithm.schema.json`.

## Fields

| Field | Type | Notes |
|---|---|---|
| `id` | string | Unique slug, matches directory name |
| `name` | string | Canonical name, e.g. "Shor's Algorithm" |
| `aliases` | list[string] | Other names it's known by |
| `category` | string | Matches top-level `algorithms/` taxonomy directory |
| `problem_class` | string | One-sentence description of the problem it solves |
| `problem_tags` | list[string] | Free tags for search/filtering, e.g. `factoring`, `search`, `optimization`, `linear-algebra`, `simulation`, `cryptanalysis`, `graph` |
| `classical_complexity` | string | Best known classical complexity for the same problem |
| `quantum_complexity` | string | This algorithm's complexity |
| `speedup` | enum | `exponential` \| `superpolynomial` \| `polynomial` \| `quadratic` \| `heuristic` \| `none-proven` |
| `qubits_required` | string | Formula or fixed count, note logical vs. physical qubits |
| `circuit_depth` | string | Rough asymptotic or typical depth |
| `requires_fault_tolerance` | boolean | Whether it needs error-corrected hardware to be useful at scale |
| `hardware_assumptions` | string | e.g. "NISQ-viable", "requires logical qubits ~10^6 physical", "simulator only" |
| `maturity` | enum | `textbook` \| `demonstrated` (run on real hardware) \| `research` \| `experimental` |
| `implementations` | list[object] | `{language, framework, path, status}` — one entry per implementation variant in this repo |
| `source` | object | `{repo, url, commit, license}` — provenance of the original code this was copied from |
| `known_limitations` | list[string] | Known weaknesses, failure modes, or caveats |
| `improvement_opportunities` | list[string] | Open ideas for optimization — this is the field an "improve this algorithm" agent reads/writes to |
| `benchmarks` | list[object] | Optional: `{metric, value, hardware, date}` |
| `references` | list[string] | Paper links / DOIs |
| `last_reviewed` | date | When metadata was last verified against the code |

`improvement_opportunities` and `known_limitations` are deliberately freeform lists rather than
rigid sub-schemas — they're meant to accumulate notes from both humans and an AI reviewer over
time without needing a schema migration every time someone finds a new angle.

## Example

See `docs/examples/metadata.example.yaml`.
