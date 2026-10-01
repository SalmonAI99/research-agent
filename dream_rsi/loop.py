"""Outer Dream-RSI loop: online explore -> build simulator pool -> dream -> redeploy."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .developer import Developer, LocalSearchDeveloper
from .env import OnlineEnv
from .policy import ParamPolicy, PolicyParams
from .replay import Coeffs, evaluate_policy, run
from .synthetic import SyntheticAgent
from .tree import DiscoveryTree


@dataclass
class RoundLog:
    t: int
    policy: dict
    online_best: float
    online_requests: int
    replay_v_before: float
    replay_v_after: float


@dataclass
class DreamResult:
    history: list[DiscoveryTree]
    policy: ParamPolicy
    logs: list[RoundLog] = field(default_factory=list)


def dream_rsi(
    *,
    rounds: int = 4,               # outer iterations T
    workers: int = 10,             # W
    k1: int = 11,                  # online decision rounds K1
    k2: int = 11,                  # replay decision rounds K2
    m_versions: int = 8,           # policy versions M per offline phase
    coeffs: Coeffs = Coeffs(),
    make_agent: Callable[[int], Callable] = lambda t: SyntheticAgent(seed=t),
    developer: Developer | None = None,
    initial: ParamPolicy | None = None,
    adapt: bool = True,            # False => Recursive Fixed Exploration baseline
) -> DreamResult:
    developer = developer or LocalSearchDeveloper()
    policy = initial or ParamPolicy(PolicyParams(n_branches=workers, max_depth=k1))
    history: list[DiscoveryTree] = []
    out = DreamResult(history, policy)
    for t in range(1, rounds + 1):
        # 1. Online exploration with the current policy (fresh tree; history is context only)
        env = OnlineEnv(workers, make_agent(t))
        run(policy, env, k1)
        history.append(env.observed)
        # 2-3. Offline dreaming over every recorded world
        v0, _, _ = evaluate_policy(policy, history, workers, k2, coeffs)
        best, best_v = policy, v0
        if adapt:
            cur, cur_v, per_world, log = policy, v0, evaluate_policy(policy, history, workers, k2, coeffs)[1], []
            for _ in range(m_versions - 1):
                log.append((cur.describe(), cur_v))
                cur = developer.revise(cur, cur_v, per_world, log)
                cur_v, per_world, _ = evaluate_policy(cur, history, workers, k2, coeffs)
                if cur_v > best_v:  # argmax over versions; pi_0 included, so V* >= V0
                    best, best_v = cur, cur_v
        out.logs.append(RoundLog(t, best.describe(), env.observed.best(), env.requests, v0, best_v))
        policy = best
    out.policy = policy
    return out
