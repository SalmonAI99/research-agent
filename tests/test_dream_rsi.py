import unittest

from dream_rsi import (DiscoveryTree, OnlineEnv, ParallelRefinePolicy, ParamPolicy,
                       ReplayEnv, dream_rsi, evaluate_policy)
from dream_rsi.replay import Coeffs, replay_score, run
from dream_rsi.synthetic import SyntheticAgent
from dream_rsi.tree import ROOT


def small_tree() -> DiscoveryTree:
    t = DiscoveryTree()
    a = t.add(ROOT, 0.2); b = t.add(ROOT, 0.1)
    t.add(a.id, 0.5); t.add(b.id, 0.9)
    return t


class ReplayTests(unittest.TestCase):
    def test_replay_is_deterministic_and_reads_only_records(self):
        t = small_tree()
        e1, e2 = ReplayEnv(t, 2), ReplayEnv(t, 2)
        pol = ParallelRefinePolicy(depth=5)
        run(pol, e1, 5); run(pol, e2, 5)
        self.assertEqual(e1.observed.best(), e2.observed.best())
        self.assertEqual(e1.observed.best(), 0.9)
        self.assertEqual(e1.requests, 4)

    def test_root_opens_earliest_unrevealed_child_in_order(self):
        env = ReplayEnv(small_tree(), 2)
        env.step([ROOT])
        self.assertEqual(env.observed.nodes[1].score, 0.2)
        env.step([ROOT])
        self.assertEqual(env.observed.nodes[2].score, 0.1)

    def test_policy_cannot_exceed_workers_or_pick_internal_node(self):
        env = ReplayEnv(small_tree(), 1)
        with self.assertRaises(ValueError): env.step([ROOT, ROOT])
        env.step([ROOT]); env.step([1])
        with self.assertRaises(ValueError): env.step([1])  # 1 is now internal

    def test_replay_score_formula(self):
        env = ReplayEnv(small_tree(), 2)
        run(ParallelRefinePolicy(5), env, 5)
        # best .9 - .01*4 + .5*4/2 rounds
        self.assertAlmostEqual(replay_score(env, Coeffs(0.01, 0.5)), 0.9 - 0.04 + 0.5 * 4 / env.rounds)

    def test_empty_policy_scores_zero_cost(self):
        env = ReplayEnv(small_tree(), 2)
        self.assertEqual(replay_score(env), 0.0)


class LoopTests(unittest.TestCase):
    def test_selected_policy_never_worse_than_current_on_history(self):
        res = dream_rsi(rounds=3, workers=6, k1=8, k2=8, m_versions=6)
        for log in res.logs:
            self.assertGreaterEqual(log.replay_v_after, log.replay_v_before)
        self.assertEqual(len(res.history), 3)

    def test_fixed_baseline_keeps_policy(self):
        res = dream_rsi(rounds=3, workers=6, k1=8, k2=8, adapt=False)
        self.assertEqual({tuple(l.policy.items()) for l in res.logs}.__len__(), 1)

    def test_online_env_grows_tree(self):
        env = OnlineEnv(4, SyntheticAgent(1))
        run(ParallelRefinePolicy(3), env, 3)
        self.assertEqual(len(env.observed), 12)


if __name__ == "__main__":
    unittest.main()
