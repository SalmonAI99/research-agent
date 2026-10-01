"""Replay evaluation (paper Eq. 1) and the rollout driver shared with online runs."""
from __future__ import annotations

from dataclasses import dataclass

from .env import Env, ReplayEnv
from .policy import Policy
from .tree import DiscoveryTree


@dataclass(frozen=True)
class Coeffs:
    beta1: float = 0.01  # execution-cost penalty per generation request
    beta2: float = 0.0   # parallelism bonus (avg attempts per round)


def run(policy: Policy, env: Env, max_rounds: int) -> Env:
    """Drive a policy for at most K rounds; stops on an empty batch."""
    policy.reset()
    for _ in range(max_rounds):
        batch = policy.select(env)
        if not batch:
            break
        if not env.step(batch):  # nothing left to reveal/produce
            break
    return env


def replay_score(env: Env, c: Coeffs = Coeffs()) -> float:
    """V = max score - beta1 * N + beta2 * N / max(1, k*)."""
    n, k = env.requests, env.rounds
    best = env.observed.best() if n else 0.0
    return best - c.beta1 * n + c.beta2 * n / max(1, k)


def evaluate_policy(
    policy: Policy, history: list[DiscoveryTree], workers: int, max_rounds: int,
    c: Coeffs = Coeffs(),
) -> tuple[float, list[float], list[ReplayEnv]]:
    """Average replay score over all historical trees (worlds) -> (V, per-tree V_i, envs)."""
    envs, scores = [], []
    for tree in history:
        env = ReplayEnv(tree, workers)
        run(policy, env, max_rounds)
        envs.append(env)
        scores.append(replay_score(env, c))
    return sum(scores) / len(scores), scores, envs
