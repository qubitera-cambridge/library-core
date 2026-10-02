Grover's algorithm solves a simple-sounding problem: you have N possible items, one (or a few)
of them are "marked" by some test you can run, and you want to find which one. Classically, with
no structure to exploit, you're stuck checking items one at a time — on average N/2 checks,
worst case N. Grover's does it in roughly sqrt(N) checks instead.

## The intuition: amplitude amplification

Grover's works by repeating two steps that, together, nudge the "marked" answers higher in
probability each time:

1. **The oracle** flips the sign (phase) of exactly the marked states, leaving everything else
   untouched. This doesn't change any probabilities by itself — squaring a negative amplitude
   gives the same probability as squaring a positive one — but it sets up the next step.
2. **The diffusion operator** reflects every amplitude about the *average* amplitude across all
   states. Because the oracle just made the marked states' amplitudes stick out from the average
   (now negative, while everything else is still positive), this reflection pushes the marked
   states' amplitudes further from zero — amplifying them — while shrinking the rest.

Repeat this pair of steps roughly `(pi/4) * sqrt(N/M)` times (for `M` marked states out of `N`),
and the marked states end up carrying almost all the probability. Measure, and you'll read out one
of them with high probability.

The one subtlety that actually matters in practice: there's an optimal number of iterations, and
**overshooting it doesn't help** — like swinging a pendulum past the top, more iterations past the
optimum actually *decreases* your success probability. This repo's implementation computes that
optimal count exactly (see `qiskit_impl.py`'s `optimal_iterations`) rather than using the common
small-angle approximation, which was found during development to overshoot for anything but a
very small ratio of marked to total items.

## Why no ancilla qubit?

Many introductions to Grover's draw the oracle with an extra "ancilla" qubit prepared in the
`|->` state, using phase kickback to flip the sign of marked states. This implementation skips
that: it uses a direct multi-controlled-Z gate instead, which achieves the same phase flip
symmetrically across all qubits with no extra qubit needed. Fewer qubits, same result — just a
different (and arguably simpler) way to write the same oracle.

## Worked example

The demo below searches an 8-item space (3 qubits) for 2 marked items. With `N=8` and `M=2`, the
optimal iteration count works out to exactly 1 — notably *not* 2, which is what the common
approximation formula would suggest (and which this repo's test suite specifically catches, see
`PROVENANCE.md`). One iteration is enough to concentrate essentially all the probability on the
two marked states.
