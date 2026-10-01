"""Discovery tree: root = initial workspace; each node = one generate+evaluate attempt."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

ROOT = 0


@dataclass
class Node:
    id: int
    parent: int | None
    score: float | None  # None for the root
    seq: int = 0  # creation order
    meta: dict[str, Any] = field(default_factory=dict)  # artifact, diagnostics, ...


class DiscoveryTree:
    def __init__(self) -> None:
        self.nodes: dict[int, Node] = {ROOT: Node(ROOT, None, None)}
        self.children: dict[int, list[int]] = {ROOT: []}

    def add(self, parent: int, score: float, **meta: Any) -> Node:
        nid = len(self.nodes)
        node = Node(nid, parent, score, seq=nid, meta=meta)
        self.nodes[nid] = node
        self.children[nid] = []
        self.children[parent].append(nid)
        return node

    def leaves(self) -> list[int]:
        return [i for i, c in self.children.items() if i != ROOT and not c]

    def eligible(self) -> list[int]:
        """A(T) = {root} U leaves."""
        return [ROOT] + self.leaves()

    def branch_of(self, nid: int) -> int:
        """Id of the depth-1 ancestor (the branch this node belongs to)."""
        while self.nodes[nid].parent not in (ROOT, None):
            nid = self.nodes[nid].parent  # type: ignore[assignment]
        return nid

    def best(self) -> float:
        scores = [n.score for n in self.nodes.values() if n.score is not None]
        return max(scores) if scores else float("-inf")

    def __len__(self) -> int:
        return len(self.nodes) - 1  # non-root nodes
