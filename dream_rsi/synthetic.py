"""Synthetic stand-in for the discovery agent + evaluator (no LLM needed).

Each root attempt draws a latent 'direction quality'; refining a node improves
the score with diminishing returns plus noise, and attempts occasionally fail
(score 0 = broken implementation). This gives trees with realistic structure:
good/bad directions, plateaus, and repairable failures.
"""
from __future__ import annotations

import random

from .tree import ROOT, DiscoveryTree


class SyntheticAgent:
    def __init__(self, seed: int = 0, fail_rate: float = 0.12) -> None:
        self.rng = random.Random(seed)
        self.fail_rate = fail_rate
        self.quality: dict[int, float] = {}  # branch root id -> latent potential

    def __call__(self, tree: DiscoveryTree, parent: int) -> tuple[float, dict]:
        r = self.rng
        if parent == ROOT:
            q = r.betavariate(2, 3)  # potential of a fresh direction
            score = max(0.0, q * 0.4 + r.gauss(0, 0.03))
            meta = {"q": q}
            if r.random() < self.fail_rate:
                score = 0.0
            return score, meta
        branch = tree.branch_of(parent)
        q = tree.nodes[branch].meta["q"]
        prev = max(tree.nodes[parent].score, 0.0)
        ceiling = 0.35 + 0.65 * q
        gain = (ceiling - prev) * r.uniform(0.0, 0.35) + r.gauss(0, 0.015)
        score = prev + gain
        if r.random() < self.fail_rate:
            score = 0.0  # failed attempt; parent's score is unchanged
        return max(score, 0.0), {"q": q}
