"""Clone of the Dream-RSI core loop (Zheng et al., 2026, arXiv:2609.14858).

History as replay simulator: a completed discovery tree is replayed by
alternative exploration policies at zero execution cost.
"""
from .tree import DiscoveryTree, Node
from .env import Env, OnlineEnv, ReplayEnv
from .policy import Policy, ParallelRefinePolicy, ParamPolicy
from .replay import replay_score, evaluate_policy
from .loop import dream_rsi, DreamResult

__all__ = [
    "DiscoveryTree", "Node", "Env", "OnlineEnv", "ReplayEnv", "Policy",
    "ParallelRefinePolicy", "ParamPolicy", "replay_score", "evaluate_policy",
    "dream_rsi", "DreamResult",
]
