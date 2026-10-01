"""Policy-development agent: revises policy code from replay feedback.

The paper uses an LLM agent that rewrites exploration-policy source. Here the
`Developer` protocol is the seam; `LocalSearchDeveloper` is a deterministic
stand-in that mutates ParamPolicy knobs using per-world replay scores.
An LLM-backed developer can implement the same `revise` signature.
"""
from __future__ import annotations

import random
from typing import Protocol

from .policy import ParamPolicy
from .replay import Coeffs


class Developer(Protocol):
    def revise(self, policy: ParamPolicy, v: float, per_world: list[float],
               feedback_log: list[tuple[dict, float]]) -> ParamPolicy: ...


class LocalSearchDeveloper:
    def __init__(self, seed: int = 0) -> None:
        self.rng = random.Random(seed)

    def revise(self, policy, v, per_world, feedback_log):
        # start from the best version seen so far (uses earlier-revision feedback)
        base = policy
        if feedback_log:
            best_params, best_v = max(feedback_log, key=lambda x: x[1])
            if best_v > v:
                base = ParamPolicy(type(policy.p)(**best_params), policy.seed)
        r, p = self.rng, base.p
        kw = {}
        for name, lo, hi, step in [
            ("n_branches", 1, 32, 3), ("max_depth", 1, 30, 3), ("patience", 1, 10, 1),
            ("window", 1, 10, 1),
        ]:
            if r.random() < 0.5:
                kw[name] = min(hi, max(lo, getattr(p, name) + r.randint(-step, step)))
        if r.random() < 0.5:
            kw["top_frac"] = min(1.0, max(0.1, p.top_frac + r.uniform(-0.3, 0.3)))
        if r.random() < 0.3:
            kw["stop_gain"] = max(0.0, p.stop_gain + r.uniform(-0.005, 0.01))
        return base.with_params(**kw) if kw else base
