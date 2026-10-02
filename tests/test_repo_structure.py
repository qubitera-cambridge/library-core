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
from datetime import date, timedelta
from pathlib import Path

import jsonschema
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "schema" / "algorithm.schema.json"
ALGORITHMS_DIR = REPO_ROOT / "src" / "library_core" / "algorithms"
STALE_AFTER_DAYS = 365


def _algorithm_dirs():
    if not ALGORITHMS_DIR.exists():
        return []
    return sorted(
        p.parent for p in ALGORITHMS_DIR.glob("*/*/metadata.yaml")
    )


def _all_leaf_directories():
    """Every algorithms/<category>/<algo>/ directory that exists on disk, found
    by walking the filesystem rather than by globbing for metadata.yaml. Used to
    catch a directory whose metadata.yaml was deleted (e.g. by a pure-deletion
    commit) — such a directory is invisible to _algorithm_dirs() above and would
    otherwise silently drop out of every structural check."""
    if not ALGORITHMS_DIR.exists():
        return []
    return sorted(p for p in ALGORITHMS_DIR.glob("*/*") if p.is_dir())


@pytest.fixture(scope="module")
def schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


ALGO_DIRS = _algorithm_dirs()
ALL_LEAF_DIRS = _all_leaf_directories()


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
def test_algorithm_dependencies_reference_real_catalogue_entries(algo_dir):
    """The 'checker' for algorithm_dependencies: a declared dependency on
    another library-core algorithm must actually exist in the catalogue, not
    just be a typo or a stale reference to something renamed/removed."""
    with open(algo_dir / "metadata.yaml") as f:
        data = yaml.safe_load(f)
    known_ids = {d.name for d in ALGO_DIRS}
    for dep_id in data.get("algorithm_dependencies", []):
        assert dep_id in known_ids, (
            f"{algo_dir}: algorithm_dependencies references unknown id '{dep_id}' "
            f"(known ids: {sorted(known_ids)})"
        )


@pytest.mark.parametrize("algo_dir", ALGO_DIRS, ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_provenance_file_exists(algo_dir):
    assert (algo_dir / "PROVENANCE.md").exists(), f"Missing PROVENANCE.md in {algo_dir}"


@pytest.mark.parametrize("algo_dir", ALGO_DIRS, ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_implementation_paths_exist(algo_dir):
    """`path` is relative to the algorithm's own directory (algo_dir), not
    repo-root — see docs/metadata-schema.md."""
    with open(algo_dir / "metadata.yaml") as f:
        data = yaml.safe_load(f)
    for impl in data.get("implementations", []):
        impl_path = algo_dir / impl["path"]
        assert impl_path.exists(), f"metadata.yaml references missing file: {impl['path']}"


@pytest.mark.parametrize("algo_dir", ALGO_DIRS, ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_last_reviewed_not_stale(algo_dir):
    with open(algo_dir / "metadata.yaml") as f:
        data = yaml.safe_load(f)
    reviewed = data["last_reviewed"]
    if not isinstance(reviewed, date):
        reviewed = date.fromisoformat(str(reviewed))
    age = date.today() - reviewed
    assert age <= timedelta(days=STALE_AFTER_DAYS), (
        f"{algo_dir}: last_reviewed is {age.days} days old (> {STALE_AFTER_DAYS}); "
        "re-verify the implementation/benchmarks and bump last_reviewed"
    )


@pytest.mark.parametrize("leaf_dir", ALL_LEAF_DIRS, ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_every_algorithm_directory_has_metadata(leaf_dir):
    assert (leaf_dir / "metadata.yaml").exists(), (
        f"{leaf_dir} has no metadata.yaml — orphaned algorithm directory "
        "(did a metadata.yaml get deleted without removing the directory?)"
    )


def test_at_least_one_algorithm_is_registered():
    assert len(ALGO_DIRS) >= 1, "Expected at least one algorithm under algorithms/**/metadata.yaml"
