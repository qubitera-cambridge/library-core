#!/usr/bin/env python3
"""Stage 1 of the documentation site build: run each algorithm's `demo()`
function (if it has one) and cache the result as JSON.

This must run inside the tox environment matching the algorithms' framework
(e.g. `tox -e qiskit-docs`) — it imports and executes real algorithm code, so
it needs that framework's SDK installed. It deliberately does NOT build the
site itself: that's scripts/render_docs.py, which only needs the cached JSON
this script produces, not any quantum SDK. Keeping these separate means the
site-rendering step never needs every framework's SDK installed at once,
mirroring the same per-framework isolation tox.ini already gives tests.

See docs/site-generation.md.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
ALGORITHMS_DIR = REPO_ROOT / "algorithms"
DEMO_CACHE_DIR = REPO_ROOT / "website" / "demo_cache"


def _algorithm_dirs():
    return sorted(p.parent for p in ALGORITHMS_DIR.glob("*/*/metadata.yaml"))


def _frameworks(metadata: dict) -> set:
    return {
        impl.get("framework")
        for impl in metadata.get("implementations", [])
        if impl.get("framework")
    }


def _load_impl_module(impl_path: Path, unique_name: str):
    spec = importlib.util.spec_from_file_location(unique_name, impl_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def generate_for_framework(framework: str, only_dirs: list[Path] | None = None) -> int:
    """`only_dirs`, if given, scopes generation to just those algorithm
    directories — e.g. the ones a commit actually touched — leaving cached
    JSON for every other algorithm of this framework untouched rather than
    regenerating it. `website/demo_cache/` is gitignored but persists on disk
    across commits/tox runs, so this is the whole caching mechanism: nothing
    fancy, just "don't recompute what nothing asked you to recompute."
    `only_dirs=None` (the default, used for a full/CI build) regenerates
    everything, since there's no prior cache to trust on a fresh checkout.
    """
    DEMO_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    generated, skipped = 0, 0

    only_dirs_resolved = {d.resolve() for d in only_dirs} if only_dirs is not None else None

    for algo_dir in _algorithm_dirs():
        if only_dirs_resolved is not None and algo_dir.resolve() not in only_dirs_resolved:
            continue

        with open(algo_dir / "metadata.yaml") as f:
            metadata = yaml.safe_load(f)

        if framework not in _frameworks(metadata):
            continue

        algo_id = metadata["id"]
        impl_entries = [
            impl for impl in metadata.get("implementations", [])
            if impl.get("framework") == framework
        ]
        if not impl_entries:
            continue
        impl_path = REPO_ROOT / impl_entries[0]["path"]

        module = _load_impl_module(impl_path, f"{algo_id}.{framework}_impl")
        if not hasattr(module, "demo"):
            print(f"skip (no demo()): {algo_id}")
            skipped += 1
            continue

        result = module.demo()
        out_path = DEMO_CACHE_DIR / f"{algo_id}.json"
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"generated: {algo_id} -> {out_path.relative_to(REPO_ROOT)}")
        generated += 1

    print(f"\n{generated} demo(s) generated, {skipped} algorithm(s) skipped (no demo() yet)")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--framework", required=True)
    parser.add_argument(
        "dirs", nargs="*", help="Scope to these algorithm directories only (default: all)"
    )
    args = parser.parse_args()
    only_dirs = [REPO_ROOT / d for d in args.dirs] if args.dirs else None
    sys.exit(generate_for_framework(args.framework, only_dirs))
