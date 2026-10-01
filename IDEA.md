# Research ideas

## Memory-guided self-play by checkpoint forking

### Core idea

Let an agent inspect its own execution history and decide where an alternative continuation would be useful. The runtime checkpoints the agent's state at that point, forks the run, and lets the branch produce a different result. A human can approve the result or behavior. The approved outcome becomes feedback for improving the policy that chooses **when**, **where**, and possibly **how** to fork.

This is inspired by the replay-simulator idea associated with Dream-RSI: past execution traces are treated as a space in which the agent can simulate alternative decisions before changing future behavior.

### Proposed loop

1. Record an append-only trajectory: observations, messages, tool calls, memory reads/writes, intermediate artifacts, decisions, and outcomes.
2. At selected checkpoints, have a fork policy estimate the value of branching. A useful trigger might be uncertainty, a detected failure pattern, a high-impact decision, or a disagreement between critics.
3. Restore the checkpoint and run one or more counterfactual continuations with controlled randomness and a specified intervention.
4. Score branches with task success, verifier checks, cost, safety constraints, and human approval.
5. Store the approved branch and the rejected alternatives as training data for the fork policy and, separately, for the task agent's memory.
6. Periodically update the fork policy, with a held-out evaluation set to prevent it from learning to optimize approval artifacts.

### What could be learned

- **Fork timing:** which execution stages are worth branching from.
- **Fork trigger:** uncertainty, error likelihood, novelty, or expected value of information.
- **Branch allocation:** how many branches to spend under a fixed budget.
- **Intervention choice:** which message, plan, tool call, memory item, or delegation to change.
- **Selection policy:** how to combine automated verification with human approval.

### Important design distinction

The system should separate the **task policy** from the **fork policy**. The fork policy decides when and how to explore alternatives; it should not be allowed to edit the evaluator or treat approval as the only objective. Human approval is a valuable label, but it is sparse, subjective, and vulnerable to reward hacking.

### Feasibility requirements

- Deterministic or recorded tool effects where possible.
- Checkpoints that include model-visible context, memory state, tool state, filesystem/worktree state, and random seeds.
- An event lineage connecting each branch to its parent checkpoint.
- Isolation for side effects such as network calls, files, commits, and external APIs.
- A merge rule that imports approved knowledge without blindly copying branch-specific observations.

### Main research claim to test

> A learned fork policy can use execution history to spend a fixed replay budget on high-value counterfactuals, improving final task success and reducing repeated failures compared with fixed fork schedules, no replay, and a single-agent longer-context baseline.

### Evaluation

Compare:

- no forking;
- fixed checkpoints (for example, every k steps);
- uncertainty-only or failure-triggered forking;
- learned fork timing and intervention selection.

Match total model calls, tokens, tool cost, and wall-clock budget. Report task success, counterfactual branch value, approval rate, repeated-failure rate, and calibration of the fork policy. Use multiple seeds and task orderings. Keep a hidden evaluator and audit branches for evaluator tampering.

The strongest initial experiment is a controlled environment with replayable tools, followed by a real coding-agent environment where filesystem and tool side effects make replay imperfect. A useful ablation removes memory, removes human approval, or prevents the fork policy from seeing the full trajectory.

### Risks and open questions

- Replay may not be faithful when external tools or nondeterministic APIs have changed.
- The agent may fork after every difficult step, wasting the budget.
- Approved branches may overfit to one user's preferences or one benchmark.
- Memory can preserve misleading counterfactuals unless provenance records the branch, intervention, and approval context.
- It is unclear whether human approval should train fork timing, branch selection, or both.

