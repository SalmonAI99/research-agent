# Replay, counterfactual forking, and adaptive self-improvement

Research date: 2026-09-30

## Closest match

### Dream-RSI — Recursive Self-Improvement through Evolving Worlds

- **Paper:** [arXiv:2609.14858](https://arxiv.org/abs/2609.14858)
- **Artifact:** [zhengkid/Dream-RSI](https://github.com/zhengkid/Dream-RSI)
- **Core idea:** accumulated discovery trees become a replay simulator. A candidate exploration policy can traverse recorded branches in different orders, with different stopping and parallelization decisions, without rerunning the underlying agent or evaluator.
- **Relation to our idea:** extremely close at the strategy layer. Your proposed extension is to let the agent choose *where to fork in an individual trajectory*, then learn that fork policy from approved outcomes.
- **Limitation:** Dream-RSI primarily replays recorded search-tree outcomes for exploration-policy improvement; it is not mainly a general-purpose runtime for arbitrary tool side effects or human-approved agent memory.

### SPADE — Self-Play in Adaptive Synthetic Executable Environments

- **Paper:** [arXiv:2608.19197](https://arxiv.org/abs/2608.19197)
- **Artifact:** [spade-rl/spade](https://github.com/spade-rl/spade)
- **Core idea:** one language model acts both as an environment designer, writing executable Python environments, and as a reasoning agent. Hint-based regret trains the designer to produce environments near the agent's capability frontier.
- **Relation:** relevant to the adaptive-environment and self-play side of the proposal, but SPADE creates new environments rather than replaying and forking an agent's own history.
- **Available assets:** code, checkpoints, grounding corpora, and generated environments are linked from the repository and Hugging Face.

## Directly relevant counterfactual replay papers

### Causal Agent Replay (CAR)

- **Paper:** [arXiv:2606.08275](https://arxiv.org/abs/2606.08275)
- **Artifact:** [jaineet17/causal-agent-replay](https://github.com/jaineet17/causal-agent-replay)
- **Core idea:** record a trajectory, intervene at a step, replay forward, and measure the distributional change in outcomes. Supports resampling an action, forcing an action, replacing an observation, editing context, or swapping the policy.
- **Relation:** the strongest existing implementation substrate for your fork primitive. It already treats a checkpoint plus a downstream re-run as an intervention.
- **Useful design:** confidence intervals, stochastic forward replay, and Monte-Carlo Shapley attribution.

### CausalFlow — Causal Attribution and Counterfactual Repair for LLM Agent Failures

- **Paper:** [arXiv:2605.25338](https://arxiv.org/abs/2605.25338)
- **Artifact:** [devangb3/CausalFlow](https://github.com/devangb3/CausalFlow)
- **Core idea:** identify high-responsibility steps by counterfactual intervention, then generate minimal edits and validate them by replay. The repository includes trace logging, causal graphs, repairs, ablations, and DPO sketches.
- **Reported repository headline:** aggregate effective success 61.6% to 78.1% (+16.5 points), with run details in `RESULTS.md`.
- **Relation:** supports learning from approved repaired branches. Your novelty would be learning *when to branch* proactively rather than only repairing detected failures.

### AgenTracer — Who Is Inducing Failure in the LLM Agentic Systems?

- **Paper:** [arXiv:2509.03312](https://arxiv.org/abs/2509.03312)
- **Artifact status:** no official GitHub repository was located in this search.
- **Core idea:** counterfactual replay and programmed fault injection produce the TracerTraj dataset; a lightweight tracer learns multi-granular failure attribution.
- **Relation:** useful for generating labels for which checkpoint or decision should have been forked, even if it is not itself a fork-policy learner.

## Evidence and replay-quality work

### GRADE — Graph Representation of LLM Agent Dependency and Execution

- **Paper:** [arXiv:2606.22741](https://arxiv.org/abs/2606.22741)
- **Core idea:** compare execution traces with dependency edges that are observed, declared, or inferred, including counterfeit-edge controls.
- **Relation:** a warning for your design: storing history is not enough. You need to record the exact context, memory reads, tool outputs, and branch provenance consumed at each decision.

### Reflexion — Language Agents with Verbal Reinforcement Learning

- **Paper:** [arXiv:2303.11366](https://arxiv.org/abs/2303.11366)
- **Artifact:** [noahshinn/reflexion](https://github.com/noahshinn/reflexion)
- **Core idea:** agents write verbal reflections into memory and use them on later attempts.
- **Relation:** foundational precedent for turning approved outcomes and failures into persistent memory. It does not replay a prior trajectory or learn branch timing.

### Voyager — An Open-Ended Embodied Agent with Large Language Models

- **Paper:** [arXiv:2305.16291](https://arxiv.org/abs/2305.16291)
- **Artifact:** [MineDojo/Voyager](https://github.com/MineDojo/Voyager)
- **Core idea:** an embodied agent maintains an ever-growing skill library and uses execution feedback to improve future behavior.
- **Relation:** relevant to branch knowledge retention and selective memory, but not checkpoint-level counterfactual replay.

## Useful implementation artifacts (not necessarily papers)

| Artifact | Repository | What it provides |
|---|---|---|
| Agent Time Machine | [dev2solid/agent-time-machine](https://github.com/dev2solid/agent-time-machine) | Framework-independent SQLite event store; rewind, fork at a checkpoint, change one decision, and compare evidence. |
| Agent checkpoint replay | [jrajath94/agent-checkpoint-replay](https://github.com/jrajath94/agent-checkpoint-replay) | Small standard-library demo of durable checkpoint, restore, and deterministic replay for tool-calling runs. |
| AgentKernel | [hugyu/AgentKernel](https://github.com/hugyu/AgentKernel) | Observable/replayable harness with event sourcing, state hashes, checkpoints, and trajectory diffs. |
| Agent Harness | [nderman/agent-harness](https://github.com/nderman/agent-harness) | Deterministic cassettes, replayable traces, and evaluation reports for a tool-using agent. |
| LangGraph | [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | Production-oriented graph runtime with persistence/checkpoint concepts that can serve as a base for branchable execution. |
| Dream-RSI SDK (unofficial) | [TheAstrayDev/dream-rsi-sdk](https://github.com/TheAstrayDev/dream-rsi-sdk) | Alpha, model-agnostic recorded-tree replay and exploration-policy search inspired by Dream-RSI; treat as an independent implementation, not the paper's official artifact. |

## Synthesis for our proposal

The literature separates into three layers:

1. **Replay as a simulator:** Dream-RSI reuses realized search trees to train exploration policies cheaply.
2. **Replay as intervention:** CAR and CausalFlow fork a trajectory to identify causal steps or repair failures.
3. **Memory as improvement signal:** Reflexion and Voyager retain reflections or skills for later attempts; SPADE adapts the environment itself.

The clearest open combination is a **learned proactive fork policy**: use a CAR-style checkpoint and intervention substrate, Dream-RSI-style replay data, and approval or verifier outcomes to learn when and where to branch. This differs from simply replaying all checkpoints or only branching after a failure.

## Recommended first prototype

1. Implement event-sourced checkpoints for model context, memory reads/writes, tool outputs, random seed, and filesystem snapshot.
2. Add two interventions: resample the next model action and edit one memory item.
3. Start with a deterministic synthetic tool environment; use CAR's confidence-interval evaluation pattern.
4. Compare no replay, fixed-interval replay, failure-triggered replay, and a learned fork policy under equal model-call budget.
5. Use human approval only as an additional label; retain an independent hidden verifier to prevent approval optimization.

