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


## Assessment of directions from `literature/LIT_REVIEW.md` (2026-10-01)

### How I ranked the six gaps

Criteria: (1) is the claim testable with a small budget, (2) is the result publishable whichever way it comes out, (3) how likely is it to already be scooped, (4) does it connect to the checkpoint-forking idea above.

| Rank | Gap | Why |
|---|---|---|
| 1 | **Gap 1: compute-matched swarm RSI** | The review says almost no swarm-RSI paper reports an equal-budget single-agent baseline, and "Science of Collective AI" (Γ) gives a ready metric. Either outcome is informative. Best treated as the *evaluation protocol* for every other idea, not a standalone project. |
| 2 | **Gap 5: fragility of population methods** | Cheap and evaluation-only: reuse the fragility paper's seeds and task-order protocol. Hypothesis "populations reduce single-agent variance" is clean. Needs a working RSI loop first. |
| 3 | **Gap 3: auditor role** | Strongest safety angle. The tampering paper (2609.00069) supplies a taxonomy, and "tampering survives selection" is a concrete failure to beat. Risk: needs a tamper benchmark, which may need to be built. |
| 4 | **Gap 2: metaproductivity of sharing structure** | Most novel intellectually (HGM's CMP lifted from lineages to communication structure) but hardest to measure and easy to make vague. |
| 5 | **Gap 6: empirical R_AI** | Nearly free if the loops above log their gains; a good secondary result. Weak alone because RRSI and Evo-Bench already report early saturation. |
| 6 | **Gap 4: where improvement lives** | Most expensive (needs four implementations on the same budget) and confounded by implementation quality. Skip unless it falls out of another study. |

### Link to the checkpoint-forking idea

HGM's finding is that a good agent is not the same as a good self-improver, and it selects expansion nodes by clade metaproductivity. The fork policy asks the same question one level down: *which point in a trajectory is worth branching from?* Learning fork value from the outcomes of counterfactual branches is a trajectory-level analogue of CMP. GEA's explicit experience sharing also suggests branch results could be shared across a group instead of kept by one agent.

### Suggested combined thesis

> Use counterfactual forking as the self-improvement mechanism. Evaluate it with the Gap 1 equal-budget protocol and the Gap 5 seed/order protocol. Use an auditor (Gap 3) to guard against reward hacking of human approval.

This keeps one mechanism, one baseline discipline, and one safeguard, instead of six loosely related studies.

### What to look into first

1. **Novelty check on forking.** Dream-RSI is not in the literature review, and neither is prior work on branching, rewinding or counterfactual replay of agent trajectories. Search for it before investing more.
2. **Read in full:** HGM (2510.21614) for CMP, GEA (2602.04837) for experience sharing, fragility (2608.18066) for the protocol, tampering (2609.00069) for the threat model, and Γ (2602.05289) for the compute-matched metric.
3. **Benchmark choice:** Evo-Bench (2608.09096) for harness improvement versus SWE-bench for coding. Replayable tools are needed for a clean first experiment.
4. **Baselines to implement:** no forking, fixed-interval forking, failure-triggered forking, and a single agent with a longer context at matched cost.

### Open questions for the author

- Compute and API budget, which decides whether DGM-scale runs are possible.
- Paper-oriented or prototype-oriented.
- Whether human approval is a required part of the design or an optional ablation.

## Scope and plan for paper + prototype on one month of Claude Max 20x (2026-10-01)

### Budget implications

A Max 20x plan is a usage allowance (rolling windows plus weekly caps), not a pool of API dollars. Treat it as roughly a few hundred million tokens of mixed-model use per month at best, shared with interactive development. Consequences:

- DGM/GEA-scale runs (hundreds of SWE-bench episodes per generation) are out of reach. Do not target SWE-bench Verified as the main benchmark.
- Use a **cheap task agent** (the smallest capable model) and reserve larger models for the fork policy, critics and auditor, where few calls are needed.
- Primary environment: a **small, fully replayable, deterministic tool environment** (e.g. a synthetic multi-step coding/data task suite with recorded tool effects), 30 to 60 tasks. This makes checkpoint restore exact and keeps seeds cheap.
- Cache every model call keyed on (prompt, seed). Replays and repeated baselines then cost nothing.
- Hold back about 20% of the allowance for reruns and for the final multi-seed evaluation.

### Claims the paper can support at this scale

1. Under matched calls and tokens, a learned fork policy beats fixed and failure-triggered forking on a replayable suite.
2. The advantage holds across seeds and task orderings (the fragility protocol).
3. An auditor reduces approval-hacking compared with no auditor.

A real-repo coding-agent run (a small slice of SWE-bench Lite, about 20 to 30 tasks) is a stretch goal and can be framed as a limitations or "transfer" result.

### Four-week schedule

| Week | Deliverable |
|---|---|
| 1 | Novelty search; read the five key papers; build the replayable environment, trajectory log and checkpoint/restore; call cache. |
| 2 | Baselines (no fork, fixed-k, failure-triggered, longer-context single agent) at matched budget; first results and cost accounting. |
| 3 | Learned fork policy (start with a simple value model over trajectory features before any fine-tuning); auditor; hidden evaluator. |
| 4 | Multi-seed and task-order evaluation, ablations (no memory, no human approval), optional SWE-bench Lite slice; write the paper draft. |

### Cut list if the allowance runs short

Drop the SWE-bench slice first, then the auditor ablation, then the learned policy in favor of a heuristic one. Never drop the matched-budget baselines, since they are the paper's credibility.

### Prototype deliverable

A small Python package in this repo: trajectory recorder, checkpoint/restore, fork-policy interface, budget accountant, cached model client, and an experiment runner that emits seed-by-order result tables.

## Novelty check for checkpoint forking (2026-10-01)

**Method and limits.** Web searches only. `arxiv.org` and several mirrors are blocked in this sandbox, so I could not read any full text. The findings below come from search snippets and abstracts, and the arXiv IDs have **not** been run through `verify_papers.py`. Treat every overlap claim as "needs a full read".

### Verdict

The core claim, "a learned policy decides when and where to fork an agent's execution," is **substantially occupied**. The parts that still look open are human-approval-driven fork learning, an auditor guarding that approval signal, provenance-tracked memory write-back, and a budget-matched, seed/order-robust evaluation.

### Closest prior work

| Work | ID | What it does | Overlap with this idea |
|---|---|---|---|
| Dream-RSI | 2609.14858 | Logs a discovery tree with filesystem snapshots and scores, builds a replay simulator, improves the exploration policy by "dreaming" over it. Up to 162x fewer agent calls. | Source of the replay idea. Operates over a search tree (which node to expand), not live forks inside one run. No human approval or auditor seen in snippets. |
| Counterfactual Rollout Replay (CRR) | 2609.33875 | Picks decision points, restores state, samples alternative actions, uses return differences as step-level advantages. | Same fork-and-compare mechanism. Used as an RL training signal for the task policy. How decision points are chosen is unverified. |
| Branching Policy Optimization (BPO) | 2607.14171 | Branch points chosen by per-step entropy, sandbox restore, K sibling forks, tree-structured advantage. +3.6 to 6.1 on SWE-bench Verified at matched compute. | Matched-compute fork baseline on a real benchmark. Heuristic branch selection and training-time only, not a learned fork policy. |
| AgentRewind | 2608.14380 | Agent rewinds to an earlier checkpoint when stuck, restores context and environment, keeps a summary of the failed attempt as rewind memory. | Very close to "memory-guided" forking. Whether checkpoint choice is trained or prompted is unverified. |
| DIAL | 2605.06908 | Sparse gate trained from counterfactual exploration to learn when extra rollouts help. | **Closest to a learned fork trigger.** Key finding: the same uncertainty signal predicts benefit in one environment and harm in another. |
| Learning When to Plan | 2509.03581 | Learns when to spend test-time compute on planning. | Same "learn when to spend compute" framing. |
| StateFork / Waypoint | 2609.38648 | Open-source branchable environment state for agents. | Infrastructure. **Could replace our own checkpoint/restore code.** |
| Others | n/a | SWE-Search, Tree Search for LM Agents (inference-time MCTS), AgentHER, pivotal-aware self-feedback retry (reuse prefix, restart at the error). | Background and baselines. |

### What still looks open

1. **Human approval as the label for fork learning,** with an auditor role and a hidden evaluator to catch approval-hacking. None of the above mention it.
2. **Provenance-tracked memory write-back:** storing approved and rejected branches with the fork point, intervention and approval context. AgentRewind keeps a summary, but I did not see provenance.
3. **Matched-budget comparison across fork-timing, intervention-choice and branch-count policies,** with multi-seed, multi-order evaluation. BPO is matched-compute but not about learned fork policy.
4. **Transfer of a learned fork policy across environments and backbones.** DIAL suggests signal direction flips, so a result either way is publishable.

### Recommendations

- **Reframe the thesis.** Drop "learned fork timing beats fixed forking" as the headline. Use something like: "Approval-guided fork learning with an auditor, evaluated under matched budget and across seeds, orders and backbones."
- **Reuse infrastructure.** Evaluate StateFork or Waypoint for the checkpoint layer to save week-1 effort.
- **Baselines to add:** BPO-style entropy-triggered forking, a DIAL-style gate, and an AgentRewind-style stuck-then-rewind policy.
- **Before committing:** read CRR, AgentRewind, DIAL and BPO in full from a machine with arXiv access and run `verify_papers.py` on them. If CRR or AgentRewind already learns the fork point, open item 1 becomes the only differentiator.

## Reframe: memory as the state, no computer-use environment (2026-10-01)

This supersedes the filesystem/tool-state parts of the earlier feasibility notes, the StateFork recommendation, and the SWE-bench Lite stretch goal. The task agent is a **frozen model**. The only thing that changes, and therefore the only thing that is checkpointed and forked, is its **memory**.

### What the state is

`S_t = (M_t, retrieval/consolidation config)`, where `M_t` is the memory store (notes, lessons, skills, or a small knowledge base). A checkpoint is a copy of `S_t`. A fork is a **memory branch**; a counterfactual is a different memory edit applied at the same point in the task stream.

### Why this is a better fit for the budget and the thesis

- Checkpoint and restore are exact and nearly free (copy a file or a version), so the replay-fidelity risk in the old Risks section disappears.
- Task episodes can be text-only with cached model calls, so counterfactual branches are cheap to re-run.
- It lands directly on the setting of the fragility paper (2608.18066): memory-based self-improvement amplifies noise and depends on task order. A fork policy then has a concrete job, which is making memory updates robust.
- Memory diffs are human-readable, so human approval becomes cheap and natural (reviewing an edit, not a world state).

### Proposed loop

1. The agent runs a task stream and proposes memory edits (add, revise, delete, merge, change what is retrieved).
2. Instead of committing an edit directly, the system **forks** the memory: branch A has the edit, branch B does not (and optionally B' has an alternative edit).
3. Both branches are scored by **replaying** recent and held-out past tasks under each memory, using cached outcomes where possible. This is the Dream-RSI replay idea applied to memory.
4. A commit rule accepts the edit only if the branch beats the control by a margin, passes the auditor, and, optionally, passes human approval of the diff. Rejected edits are kept with provenance as negative examples.
5. A learned fork policy decides **which edits are worth the replay cost**, since scoring every proposed edit is expensive.

One-line pitch: **git for agent memory. Speculative memory updates are validated on replay branches before they are committed.**

### What the fork policy learns

- Which proposed edits deserve a replay (value of information versus replay cost).
- Which replay tasks to score on (the most informative subset, since full replay is costly).
- How to allocate the budget between exploring new tasks and validating memory.
- Per-entry credit: which stored items actually help, estimated by leave-one-out branches.

### Baselines

No memory; append-only memory (Reflexion-style); LLM-curated memory without validation; commit-all-edits with periodic pruning; random or fixed-schedule validation; validate-everything (upper bound on quality, lower bound on efficiency). All matched on total model calls.

### Evaluation

Continual task streams with multiple **orderings and seeds**, reporting final accuracy, area under the learning curve, variance across orderings (the robustness claim), validation cost, and the fraction of harmful edits blocked. Use disjoint tuning, replay and test splits, because the memory can store benchmark answers.

### Main claims to test

1. Validated memory commits reduce order-sensitivity and noise amplification compared with unvalidated memory updates.
2. A learned fork/validation policy recovers most of the benefit of validate-everything at a fraction of the replay cost.
3. An auditor plus held-out replay blocks leakage and approval-hacking edits.

### Risks and open questions

- **Novelty is unchecked for this framing.** The earlier search covered environment forking. Memory curation, validated writes, and RL for memory operations need their own search.
- Memory effects are small relative to noise, so replay sets must be large enough to detect an edit's value, which raises cost.
- Replay on past tasks can overfit to those tasks, so held-out tasks are required.
- Memory may encode answers or evaluator hints, which makes the auditor and split design central.
- The meaning of "approval" changes: approving memory edits is easy, but it is unclear whether approval should be a training label or only a gate.

## Novelty check for memory-as-state validation, coding domain (2026-10-01)

**Method and limits.** Web searches only, same as the earlier check. Full texts were not readable (arXiv is blocked in this sandbox), so overlaps come from snippets and abstracts. IDs are **not** yet run through `verify_papers.py`. Free-text memory, coding tasks.

### Verdict

The "validate a memory edit by counterfactual replay before committing it" framing is **heavily occupied**, and "git for agent memory" is already a crowded name. What looks open is narrower: (a) a *learned policy for allocating a limited replay budget across candidate edits*, and (b) a test of whether validated commits actually fix the order-sensitivity and variance that the fragility paper documents, in a coding setting, with an auditor.

### Closest prior work

| Work | ID / link | What it does | Overlap |
|---|---|---|---|
| AGMR | 2607.17621 | Does not commit a candidate memory update directly; validates it by re-executing the task with the refined memory. | **Near-identical commit rule.** |
| HiMPO | 2606.16285 | Defines the local counterfactual utility of a memory write by comparing updated vs. previous memory under the same pre-write state; trains a memory policy with it. | Same counterfactual comparison; used for RL credit, not for budgeted validation. |
| Hindsight Memory-PRM | 2608.29605 | Operation-conditioned memory-utility critic, entry-level credit. | Per-entry credit assignment. |
| MeClear | 2609.09115 | Counterfactual screening plus Shapley attribution to clear harmful memories. | Leave-one-out / attribution for pruning. |
| Learning What to Remember | 2609.37930 | Long-horizon counterfactual memory optimization. | Counterfactual memory objective. |
| When to Forget | 2604.12007 | Memory governance primitive. | Forgetting policy. |
| DreamBench-SWE | 2608.20664 | Multi-session memory-hygiene benchmark for software agents; lessons are typed, provenance-linked, lifecycle-managed and checked against executable traps. | **Coding-domain memory benchmark with provenance.** Candidate evaluation. |
| SWE-MeM | 2606.28434 | Learns adaptive memory management for long-horizon coding agents. | Learned memory ops in coding. |
| Memory-R1 | 2508.19828 | RL-trained ADD/UPDATE/DELETE/NOOP memory manager. | Learned edit policy (no replay validation). |
| MemGovern, CodeSkill, SWE-Bench-CL | 2601.06789, 2605.25430, 2507.00014 | Curated experience memory, self-evolving skills, continual-learning benchmark for coding agents. | Coding memory and continual benchmark. |
| Git-style memory | Memoir, Memoria, GCC (2508.00031), GitOfThoughts (2606.14470) | Branch, commit, merge, rollback of agent memory or context. | The versioning mechanism is not novel. |
| Fragility paper | 2608.18066 | Memory-based SI amplifies variance (up in 71% of cases, up to 10-point best-to-worst gap); shuffled task order turns +1.5% into -4.5%. | Our motivating problem. Appears diagnostic. I did not see a proposed remedy. |

### What still looks open

1. **Budgeted validation policy.** Validation by replay is costly. A learned or value-of-information policy that decides which edits to validate, and on which replay tasks, under a fixed budget, is not visible in the above. Baselines would be validate-all (AGMR-like), validate-none, and random.
2. **Does validation fix fragility?** A direct test, with the fragility paper's multi-run and shuffled-order protocol, of whether validated commits reduce variance and order-dependence in a coding stream. This reads as an empirical contribution that could stand on its own.
3. **Auditor plus leakage controls for coding memory.** Free-text lessons can encode test answers. DreamBench-SWE has hygiene traps, but an auditor role specifically blocking answer-leakage and evaluator-gaming edits was not seen.
4. **Human approval of memory diffs** as gate or label. Not seen in these results.

### Recommendations

- **Drop "git for agent memory" as the pitch.** It is taken. Pitch the budget allocation and the robustness result instead.
- **Reframed thesis:** *Under a fixed replay budget, which memory edits should an agent validate, and does validation make memory-based self-improvement robust to seeds and task order in coding?*
- **Baselines to implement:** AGMR-style validate-everything, HiMPO-style counterfactual utility, Memory-R1-style unvalidated edits, append-only (Reflexion-like), no memory.
- **Benchmarks to evaluate:** DreamBench-SWE and SWE-Bench-CL are the closest, but both may be heavy. A cheaper option is a stream of function-level coding tasks with unit tests, where execution only scores the answer. Choose after reading both.
- **Before committing:** read AGMR, HiMPO, Hindsight Memory-PRM and the fragility paper in full from a machine with arXiv access, then run `verify_papers.py`. If AGMR or HiMPO already budget their validation, item 1 is gone and the paper rests on item 2.
