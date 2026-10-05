"""Tests for library_core.graph: the dependency graph built from every
catalogue entry's algorithm_dependencies field.

These are deliberately real — built from the actual catalogue on disk, not a
fixture/mock — so they catch drift the same way test_repo_structure.py does:
if a metadata.yaml's algorithm_dependencies changes, these tests reflect the
new reality rather than silently passing against stale expectations.
"""

import re

import pytest

from library_core import build_dependency_graph, list_algorithms

# The two real edges in the catalogue today (see metadata.yaml under
# df-vqls-solver and quantum-krylov-solver). If the catalogue's
# algorithm_dependencies entries change, update this alongside them.
KNOWN_REAL_EDGES = {
    ("df-vqls-solver", "hadamard-test"),
    ("quantum-krylov-solver", "hadamard-test"),
}


@pytest.fixture(scope="module")
def graph():
    return build_dependency_graph()


@pytest.fixture(scope="module")
def real_algo_ids():
    return {meta["id"] for meta in list_algorithms()}


def test_graph_contains_all_real_catalogue_algorithms_as_nodes(graph, real_algo_ids):
    node_ids = {node.id for node in graph.nodes()}
    assert node_ids == real_algo_ids


def test_nodes_carry_real_category_and_problem_class(graph):
    real_meta = {meta["id"]: meta for meta in list_algorithms()}
    for node in graph.nodes():
        meta = real_meta[node.id]
        assert node.category == meta["category"]
        assert node.problem_class == meta["problem_class"]
        assert node.name == meta["name"]


def test_known_real_edges_exist(graph):
    edge_pairs = {(e.algo_id, e.depends_on) for e in graph.edges()}
    assert KNOWN_REAL_EDGES <= edge_pairs


def test_edges_contain_no_unexpected_entries(graph, real_algo_ids):
    """Cross-check against the real metadata.yaml files directly (not just
    the hardcoded KNOWN_REAL_EDGES set above), so a newly added
    algorithm_dependencies entry is caught by this suite too."""
    expected = set()
    for meta in list_algorithms():
        for dep_id in meta.get("algorithm_dependencies", []):
            expected.add((meta["id"], dep_id))
    edge_pairs = {(e.algo_id, e.depends_on) for e in graph.edges()}
    assert edge_pairs == expected
    assert KNOWN_REAL_EDGES <= expected  # sanity: the hardcoded set is still accurate


def test_dependents_of_hadamard_test_returns_both_linear_algebra_solvers(graph):
    assert set(graph.dependents_of("hadamard-test")) == {
        "df-vqls-solver",
        "quantum-krylov-solver",
    }


def test_dependencies_of_hadamard_test_is_empty(graph):
    """hadamard-test declares algorithm_dependencies: [] explicitly."""
    assert graph.dependencies_of("hadamard-test") == []


def test_dependencies_of_df_vqls_solver_is_hadamard_test(graph):
    assert graph.dependencies_of("df-vqls-solver") == ["hadamard-test"]


def test_dependents_of_algorithm_with_no_dependents_is_empty(graph):
    # df-vqls-solver is a leaf: nothing in the catalogue depends on it.
    assert graph.dependents_of("df-vqls-solver") == []


def test_algorithm_missing_the_field_entirely_has_no_dependencies(graph):
    """grovers-algorithm's metadata.yaml has no algorithm_dependencies key at
    all (the field is optional) — must behave like an empty list, not
    raise."""
    assert graph.dependencies_of("grovers-algorithm") == []
    assert graph.dependents_of("grovers-algorithm") == []


def test_dependencies_of_unknown_id_raises(graph):
    with pytest.raises(ValueError):
        graph.dependencies_of("not-a-real-algorithm")


def test_dependents_of_unknown_id_raises(graph):
    with pytest.raises(ValueError):
        graph.dependents_of("not-a-real-algorithm")


def test_to_mermaid_starts_with_valid_diagram_declaration(graph):
    mermaid = graph.to_mermaid()
    first_line = mermaid.strip().splitlines()[0]
    assert re.match(r"^(flowchart|graph)\s+(LR|RL|TD|TB|BT)$", first_line)


def test_to_mermaid_contains_every_real_edge_as_an_arrow_line(graph):
    mermaid = graph.to_mermaid()
    for algo_id, dep_id in KNOWN_REAL_EDGES:
        # Recognizable Mermaid arrow syntax: "<source> --> <target>".
        pattern = rf"^\s*{re.escape(algo_id)}\s*-->\s*{re.escape(dep_id)}\s*$"
        assert re.search(pattern, mermaid, re.MULTILINE), (
            f"Expected an arrow line for {algo_id} --> {dep_id} in:\n{mermaid}"
        )


def test_to_mermaid_declares_every_node(graph):
    mermaid = graph.to_mermaid()
    for node in graph.nodes():
        assert re.search(rf"^\s*{re.escape(node.id)}\[", mermaid, re.MULTILINE), (
            f"Expected a node declaration for {node.id} in:\n{mermaid}"
        )


def test_to_mermaid_has_no_stray_arrow_lines(graph):
    """Every arrow line in the diagram corresponds to a real edge — guards
    against accidental duplicate/phantom edges creeping into rendering."""
    mermaid = graph.to_mermaid()
    arrow_lines = [line for line in mermaid.splitlines() if "-->" in line]
    assert len(arrow_lines) == len(KNOWN_REAL_EDGES)
