#!/usr/bin/env bash
# Pre-commit hook entrypoint: runs the always-cheap repo structure/schema
# checks, then pytest scoped only to algorithm directories touched by the
# files passed in (staged files, from pre-commit). Falls back to nothing
# extra if no algorithm files changed.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

python3 -m pytest tests/test_repo_structure.py -q

# Read as a real array, not an unquoted string — a category/algorithm directory
# name containing a space would otherwise get word-split into bogus separate
# pytest path arguments.
mapfile -t CHANGED_DIRS < <(python3 scripts/changed_algorithm_dirs.py "$@")

if [ "${#CHANGED_DIRS[@]}" -gt 0 ]; then
    echo "Running tests for changed algorithm(s):"
    printf '%s\n' "${CHANGED_DIRS[@]}"
    set +e
    python3 -m pytest "${CHANGED_DIRS[@]}" -q
    rc=$?
    set -e
    if [ "$rc" -eq 5 ]; then
        # Exit 5 = "no tests collected" — expected when metadata/impl files are
        # staged before their test file exists yet (e.g. a new algorithm landing
        # across a couple of commits). Don't hard-block the commit for that.
        echo "warning: no tests found yet for the changed algorithm director(y/ies) above"
        rc=0
    fi
    exit "$rc"
else
    echo "No algorithm directories changed; skipping per-algorithm tests."
fi
