#!/usr/bin/env python3
"""Pre-commit hook entrypoint.

Always runs the cheap repo structure/schema check, then routes per-algorithm
tests to the tox environment matching each changed algorithm's framework(s)
(metadata.yaml's implementations[].framework) — so no contributor or CI job
ever needs every quantum SDK installed in one shared environment, and a
missing framework in one algorithm can't block a commit touching another.

Rewritten from a bash script into Python after an adversarial review found
three separate bash-specific bugs here (unquoted word-splitting, set -e
mishandling pytest's "no tests collected" exit code, pure-deletion commits
not reaching the script at all) — see docs/testing.md and git history.
"""

import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from changed_algorithm_dirs import changed_algorithm_dirs  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent


def frameworks_for(algo_dir):
    metadata_path = algo_dir / "metadata.yaml"
    if not metadata_path.exists():
        return set()
    try:
        with open(metadata_path) as f:
            data = yaml.safe_load(f) or {}
    except yaml.YAMLError:
        return set()
    return {
        impl.get("framework")
        for impl in data.get("implementations", [])
        if impl.get("framework")
    }


def main(argv):
    structural = subprocess.run(
        ["python3", "-m", "pytest", "tests/test_repo_structure.py", "-q"],
        cwd=REPO_ROOT,
    )
    if structural.returncode != 0:
        return structural.returncode

    dirs = changed_algorithm_dirs(argv)
    if not dirs:
        print("No algorithm directories changed; skipping per-algorithm tests.", flush=True)
        return 0

    dirs_by_framework = defaultdict(list)
    unresolved = []
    for d in dirs:
        fws = frameworks_for(d)
        if not fws:
            unresolved.append(d)
            continue
        for fw in fws:
            dirs_by_framework[fw].append(str(d.relative_to(REPO_ROOT)))

    if unresolved:
        # The structural check above already validates metadata.yaml exists and
        # lists at least one implementation with a framework — if it passed,
        # this shouldn't happen. Warn rather than silently skip either way.
        print(
            "warning: could not resolve a tox environment for (check metadata.yaml's implementations[].framework):",
            flush=True,
        )
        for d in unresolved:
            print(f"  {d.relative_to(REPO_ROOT)}", flush=True)

    overall_rc = 0
    for framework, rel_dirs in sorted(dirs_by_framework.items()):
        print(f"Running '{framework}' tests for: {', '.join(rel_dirs)}", flush=True)
        result = subprocess.run(
            ["tox", "-e", framework, "--", *rel_dirs, "-q"], cwd=REPO_ROOT
        )
        rc = result.returncode
        if rc == 5:
            # "no tests collected" — expected when metadata/impl are staged
            # before the test file exists yet (e.g. a new algorithm landing
            # across a couple of commits). Don't hard-block the commit for it.
            print(f"warning: no tests found yet for the changed '{framework}' director(y/ies) above")
            rc = 0
        overall_rc = overall_rc or rc

    return overall_rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
