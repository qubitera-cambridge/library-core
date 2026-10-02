"""Public API for consumers of library_core (library-ui's docs site build,
Delphi's service layer) to discover and run algorithms without needing to
know the on-disk layout directly.

This exists specifically so neither consumer needs to re-implement metadata
parsing or the importlib-by-path loading trick tests already use — one
implementation of "how do I find and run an algorithm," shared.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import yaml

PACKAGE_ROOT = Path(__file__).resolve().parent
ALGORITHMS_DIR = PACKAGE_ROOT / "algorithms"


def list_algorithms() -> list[dict]:
    """Every algorithm's metadata dict, each with an added `_dir` (absolute
    Path to that algorithm's directory, for callers that need e.g.
    EXPLANATION.md or PROVENANCE.md directly)."""
    results = []
    for metadata_path in sorted(ALGORITHMS_DIR.glob("*/*/metadata.yaml")):
        with open(metadata_path) as f:
            meta = yaml.safe_load(f)
        meta["_dir"] = metadata_path.parent
        results.append(meta)
    return results


def get_algorithm(algo_id: str) -> dict | None:
    for meta in list_algorithms():
        if meta["id"] == algo_id:
            return meta
    return None


def get_explanation(algo_id: str) -> str | None:
    meta = get_algorithm(algo_id)
    if meta is None:
        raise ValueError(f"Unknown algorithm id: {algo_id}")
    explanation_path = meta["_dir"] / "EXPLANATION.md"
    return explanation_path.read_text() if explanation_path.exists() else None


def get_provenance(algo_id: str) -> str | None:
    meta = get_algorithm(algo_id)
    if meta is None:
        raise ValueError(f"Unknown algorithm id: {algo_id}")
    provenance_path = meta["_dir"] / "PROVENANCE.md"
    return provenance_path.read_text() if provenance_path.exists() else None


def load_implementation(algo_id: str, framework: str) -> ModuleType:
    """Dynamically import and return the implementation module for one
    algorithm's given framework (e.g. "qiskit"). Uses a unique module name per
    call via `importlib.util.module_from_spec` (never registered into
    `sys.modules`), the same collision-avoidance pattern this repo's own tests
    use — see docs/testing.md — so loading many algorithms with the same
    implementation-file basename (e.g. every Qiskit algorithm's
    `qiskit_impl.py`) in one process is safe.
    """
    meta = get_algorithm(algo_id)
    if meta is None:
        raise ValueError(f"Unknown algorithm id: {algo_id}")

    impl_entries = [
        impl for impl in meta.get("implementations", [])
        if impl.get("framework") == framework
    ]
    if not impl_entries:
        raise ValueError(f"No '{framework}' implementation registered for '{algo_id}'")

    impl_path = meta["_dir"] / Path(impl_entries[0]["path"]).name
    spec = importlib.util.spec_from_file_location(f"{algo_id}.{framework}_impl", impl_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_demo(algo_id: str, framework: str) -> dict:
    """Load the given algorithm's implementation and call its `demo()`
    function. Raises AttributeError if that implementation has none."""
    module = load_implementation(algo_id, framework)
    return module.demo()
