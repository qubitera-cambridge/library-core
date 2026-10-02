#!/usr/bin/env python3
"""Print the set of algorithm directories touched by the given file paths
(typically staged files passed in by a pre-commit hook).

Used so the pre-commit test hook only runs the (potentially expensive,
simulator-backed) tests for algorithms that actually changed, rather than
the full suite on every commit — necessary once this repo holds hundreds or
thousands of algorithms.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ALGORITHMS_DIR = REPO_ROOT / "algorithms"


def changed_algorithm_dirs(changed_paths):
    dirs = set()
    for raw_path in changed_paths:
        path = (REPO_ROOT / raw_path).resolve()
        try:
            rel = path.relative_to(ALGORITHMS_DIR)
        except ValueError:
            continue
        if len(rel.parts) >= 2:
            algo_dir = ALGORITHMS_DIR / rel.parts[0] / rel.parts[1]
            if algo_dir.is_dir():
                dirs.add(algo_dir)
    return sorted(dirs)


if __name__ == "__main__":
    for d in changed_algorithm_dirs(sys.argv[1:]):
        print(d.relative_to(REPO_ROOT))
