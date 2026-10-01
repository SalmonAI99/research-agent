"""Exploration policies. A policy is executable code over the Env interface."""
from __future__ import annotations

import random
from dataclasses import dataclass, asdict, replace
from typing import Protocol

from .env import Env
from .tree import ROOT


class Policy(Protocol):
    def reset(self) -> None: ...
    def select(self, env: Env) -> list[int]: ...


class ParallelRefinePolicy:
    """Paper's initial policy: W independent workspaces, each repeatedly refined."""

    def __init__(self, depth: int = 11) -> None:
        self.depth = depth

    def reset(self) -> None:
        pass

    def select(self, env: Env) -> list[int]:
        t = env.observed
        if not t.leaves():
            return [ROOT] * env.workers  # open W independent workspaces
        live = [v for v in t.leaves() if _depth(t, v) < self.depth]
        return live[: env.workers]


def _depth(t, v: int) -> int:
    d = 0
    while t.nodes[v].parent is not None:
        v = t.nodes[v].parent
        d += 1
    return d


@dataclass(frozen=True)
class PolicyParams:
    """Tunable knobs of ParamPolicy (the stand-in for 'policy code')."""
    n_branches: int = 8        # branches opened before refining
    max_depth: int = 11        # stop refining a branch beyond this depth
    patience: int = 3          # close a branch after this many non-improving steps
    top_frac: float = 1.0      # only refine the top fraction of live branches
    reopen: float = 0.0        # prob. of opening a new root when slots are free
    stop_gain: float = 0.0     # stop all if best gain over last `window` rounds <= this
    window: int = 4


class ParamPolicy:
    def __init__(self, params: PolicyParams | None = None, seed: int = 0) -> None:
        self.p = params or PolicyParams()
        self.seed = seed
        self.reset()

    def reset(self) -> None:
        self.rng = random.Random(self.seed)
        self.best_hist: list[float] = []

    def with_params(self, **kw) -> "ParamPolicy":
        return ParamPolicy(replace(self.p, **kw), self.seed)

    def describe(self) -> dict:
        return asdict(self.p)

    def select(self, env: Env) -> list[int]:
        t, p, W = env.observed, self.p, env.workers
        best = t.best()
        self.best_hist.append(best)
        if len(self.best_hist) > p.window and p.stop_gain > 0:
            gain = self.best_hist[-1] - self.best_hist[-1 - p.window]
            if gain <= p.stop_gain:
                return []
        # live leaves: not too deep and not stalled
        live = []
        for v in t.leaves():
            if _depth(t, v) >= p.max_depth:
                continue
            if self._stalled(t, v) >= p.patience:
                continue
            live.append(v)
        live.sort(key=lambda v: -t.nodes[v].score)
        live = live[: max(1, int(round(len(live) * p.top_frac)))] if live else []
        n_open = len(t.children[ROOT])
        batch = live[:W]
        free = W - len(batch)
        while free > 0 and n_open < p.n_branches:
            batch.append(ROOT)
            n_open += 1
            free -= 1
        if free > 0 and p.reopen > 0 and self.rng.random() < p.reopen:
            batch.append(ROOT)
        return batch

    @staticmethod
    def _stalled(t, v: int) -> int:
        """Consecutive non-improving steps at the tip of this branch."""
        n, cur = 0, v
        while t.nodes[cur].parent not in (None, ROOT):
            par = t.nodes[cur].parent
            if t.nodes[cur].score > t.nodes[par].score:
                break
            n += 1
            cur = par
        return n
