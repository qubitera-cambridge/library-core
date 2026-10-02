#!/usr/bin/env bash
# Pre-commit hook entrypoint: runs the always-cheap repo structure/schema
# checks, then pytest scoped only to algorithm directories touched by the
# files passed in (staged files, from pre-commit). Falls back to nothing
# extra if no algorithm files changed.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

python3 -m pytest tests/test_repo_structure.py -q

CHANGED_DIRS=$(python3 scripts/changed_algorithm_dirs.py "$@")

if [ -n "$CHANGED_DIRS" ]; then
    echo "Running tests for changed algorithm(s):"
    echo "$CHANGED_DIRS"
    # shellcheck disable=SC2086
    python3 -m pytest $CHANGED_DIRS -q
else
    echo "No algorithm directories changed; skipping per-algorithm tests."
fi
