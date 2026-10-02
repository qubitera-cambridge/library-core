"""Repo-wide structural checks, independent of any single algorithm's test suite.

Validates that every algorithm directory conforms to the repo's conventions:
metadata.yaml exists and matches the schema, PROVENANCE.md exists, and every
path listed under `implementations` actually exists on disk. This is what
catches drift between metadata and reality as the collection grows into the
hundreds/thousands — it's cheap (pure YAML/JSON parsing, no quantum
simulation) so it should always run, unlike the per-algorithm numerical tests
which only need to run for directories that changed.
"""

import json
from pathlib import Path

import jsonschema
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "schema" / "algorithm.schema.json"
ALGORITHMS_DIR = REPO_ROOT / "algorithms"


def _algorithm_dirs():
    if not ALGORITHMS_DIR.exists():
        return []
    return sorted(
        p.parent for p in ALGORITHMS_DIR.glob("*/*/metadata.yaml")
    )


@pytest.fixture(scope="module")
def schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


ALGO_DIRS = _algorithm_dirs()


@pytest.mark.parametrize("algo_dir", ALGO_DIRS, ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_metadata_matches_schema(algo_dir, schema):
    with open(algo_dir / "metadata.yaml") as f:
        data = yaml.safe_load(f)
    jsonschema.validate(instance=data, schema=schema)


@pytest.mark.parametrize("algo_dir", ALGO_DIRS, ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_metadata_id_matches_directory_name(algo_dir):
    with open(algo_dir / "metadata.yaml") as f:
        data = yaml.safe_load(f)
    assert data["id"] == algo_dir.name


@pytest.mark.parametrize("algo_dir", ALGO_DIRS, ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_metadata_category_matches_parent_directory(algo_dir):
    with open(algo_dir / "metadata.yaml") as f:
        data = yaml.safe_load(f)
    assert data["category"] == algo_dir.parent.name


@pytest.mark.parametrize("algo_dir", ALGO_DIRS, ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_provenance_file_exists(algo_dir):
    assert (algo_dir / "PROVENANCE.md").exists(), f"Missing PROVENANCE.md in {algo_dir}"


@pytest.mark.parametrize("algo_dir", ALGO_DIRS, ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_implementation_paths_exist(algo_dir):
    with open(algo_dir / "metadata.yaml") as f:
        data = yaml.safe_load(f)
    for impl in data.get("implementations", []):
        impl_path = REPO_ROOT / impl["path"]
        assert impl_path.exists(), f"metadata.yaml references missing file: {impl['path']}"


def test_at_least_one_algorithm_is_registered():
    assert len(ALGO_DIRS) >= 1, "Expected at least one algorithm under algorithms/**/metadata.yaml"
