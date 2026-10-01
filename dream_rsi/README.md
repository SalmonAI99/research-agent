# dream_rsi — clone of the Dream-RSI core loop

Reimplements Section 3 of *Dream-RSI* (Zheng et al., 2026; paper in
`zhengkid/Dream-RSI`, code not yet released) from the paper alone.

| Paper | Module |
|---|---|
| Discovery tree, eligible set A(T) = root ∪ leaves | `tree.py` |
| Shared online/offline decision interface, batch ≤ W | `env.py` (`OnlineEnv`, `ReplayEnv`) |
| Replay: recorded child returned deterministically, root opens earliest unrevealed branch | `ReplayEnv` |
| Replay score V = max s − β1·N + β2·N/max(1,k*) (Eq. 1) | `replay.py` |
| Exploration policy = executable code | `policy.py` |
| Policy-development agent (LLM in the paper) | `developer.py` (`LocalSearchDeveloper` stand-in) |
| Outer loop, π_{t+1} = argmax_m V^m (so V* ≥ V^0) | `loop.py` |
| Discovery agent + evaluator | `synthetic.py` (stand-in) |

Run: `python3 -m unittest tests.test_dream_rsi` and `python3 run_demo.py`.

Not reproduced: the real discovery agent/evaluator (Gemini CLI, KernelBench, Lasso),
and the LLM policy developer. Swap `make_agent` and `developer` to plug them in.
