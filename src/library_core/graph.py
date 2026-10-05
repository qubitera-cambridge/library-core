"""Dependency graph over library_core's algorithm catalogue.

Reads every catalogue entry's `algorithm_dependencies` field (see
schema/algorithm.schema.json and tests/test_repo_structure.py's referential-
integrity check) via `list_algorithms()` and turns it into a small real graph
object, for consumers that want to show "what does this build on" / "what
depends on this" (e.g. a hadamard-test docs page listing df-vqls-solver and
quantum-krylov-solver as dependents) or render the whole thing as a diagram.

Graph library choice
---------------------
As of this writing the catalogue has 6 nodes and 2 edges (both
linear-algebra solvers depending on hadamard-test; see the metadata.yaml
files under src/library_core/algorithms/). Taking on networkx — a real
install footprint and its own dependency surface — for a structure this
small isn't justified: a plain dict-of-lists adjacency list is a couple
dozen lines, has zero third-party dependencies, and every operation this
module needs (list nodes, list edges, forward lookup, reverse lookup,
flowchart rendering) is O(V+E) at worst on it directly — no actual graph
algorithms (shortest path, topological sort, cycle detection) are required
yet. test_repo_structure.py's referential-integrity test already prevents
dangling edges; nothing here currently needs more than that.

If the catalogue grows much larger and denser, or a consumer needs a real
graph algorithm (topological sort for build/doc ordering, cycle detection,
path queries) rather than just the four lookups below, networkx becomes the
right call and this module should delegate to it instead of growing its own
graph algorithms by hand.
"""

from __future__ import annotations

from dataclasses import dataclass

from .catalogue import list_algorithms


@dataclass(frozen=True)
class AlgorithmNode:
    """One catalogue entry as a graph node."""

    id: str
    name: str
    category: str
    problem_class: str


@dataclass(frozen=True)
class DependencyEdge:
    """A directed edge: `algo_id` depends on `depends_on` (i.e. `algo_id`'s
    metadata.yaml lists `depends_on` under `algorithm_dependencies`)."""

    algo_id: str
    depends_on: str


class DependencyGraph:
    """Directed graph of algorithm_dependencies relationships across
    library_core's algorithm catalogue.

    An edge (u -> v) means "u depends on v". Construct via
    `build_dependency_graph()`, not directly.
    """

    def __init__(self, nodes: dict[str, AlgorithmNode], forward: dict[str, list[str]]):
        self._nodes = nodes
        # algo_id -> [ids it directly depends on], in catalogue order.
        self._forward = forward
        # algo_id -> [ids that directly depend on it] (reverse of _forward).
        self._reverse: dict[str, list[str]] = {algo_id: [] for algo_id in nodes}
        for algo_id in sorted(forward):
            for dep_id in forward[algo_id]:
                self._reverse[dep_id].append(algo_id)

    def nodes(self) -> list[AlgorithmNode]:
        """Every algorithm in the catalogue as a node, sorted by id for a
        deterministic order."""
        return [self._nodes[algo_id] for algo_id in sorted(self._nodes)]

    def edges(self) -> list[DependencyEdge]:
        """Every (algo_id, depends_on) pair, sorted by (algo_id, depends_on)
        for a deterministic order."""
        return [
            DependencyEdge(algo_id, dep_id)
            for algo_id in sorted(self._forward)
            for dep_id in self._forward[algo_id]
        ]

    def _check_known(self, algo_id: str) -> None:
        if algo_id not in self._nodes:
            raise ValueError(f"Unknown algorithm id: {algo_id}")

    def dependencies_of(self, algo_id: str) -> list[str]:
        """Direct dependencies `algo_id` declares (its own
        `algorithm_dependencies` list). Raises ValueError if algo_id is not
        in the catalogue."""
        self._check_known(algo_id)
        return list(self._forward.get(algo_id, []))

    def dependents_of(self, algo_id: str) -> list[str]:
        """Reverse lookup: ids of algorithms that directly declare a
        dependency on `algo_id`. E.g. `dependents_of("hadamard-test")` ->
        `["df-vqls-solver", "quantum-krylov-solver"]`. Raises ValueError if
        algo_id is not in the catalogue."""
        self._check_known(algo_id)
        return list(self._reverse.get(algo_id, []))

    def to_mermaid(self) -> str:
        """Render the whole graph as a Mermaid flowchart definition string
        (a `flowchart LR` diagram, one labeled node declaration per
        algorithm followed by one arrow line per dependency edge), suitable
        for embedding directly in a docs page."""
        lines = ["flowchart LR"]
        for node in self.nodes():
            label = node.name.replace('"', "'")
            lines.append(f'    {node.id}["{label}"]')
        edges = self.edges()
        if edges:
            lines.append("")
        for edge in edges:
            lines.append(f"    {edge.algo_id} --> {edge.depends_on}")
        return "\n".join(lines) + "\n"


def build_dependency_graph() -> DependencyGraph:
    """Build the algorithm dependency graph by calling `list_algorithms()`
    and reading each entry's `algorithm_dependencies` field (treated as `[]`
    when absent, since the field is optional in the schema)."""
    nodes: dict[str, AlgorithmNode] = {}
    forward: dict[str, list[str]] = {}
    for meta in list_algorithms():
        algo_id = meta["id"]
        nodes[algo_id] = AlgorithmNode(
            id=algo_id,
            name=meta["name"],
            category=meta["category"],
            problem_class=meta["problem_class"],
        )
        forward[algo_id] = list(meta.get("algorithm_dependencies", []))
    return DependencyGraph(nodes=nodes, forward=forward)
