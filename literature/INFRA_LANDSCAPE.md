# Infrastructure for Managing Agent Swarms: Landscape & Opportunity

*2026-09-27. Companion to `LIT_REVIEW.md`. This file covers the systems and software-engineering side: spawning, supervising and observing agents and their subagents.
All 13 new papers below passed the arXiv verification check. Records are in `.aris/verify-papers/verified_infra.json`.*

## 1. What already exists (four layers, mostly not connected to each other)

| Layer | Representative work | What it covers | What it does *not* cover |
|---|---|---|---|
| **Session wranglers** (100+ tools, [awesome-agent-orchestrators](https://github.com/andyrewlee/awesome-agent-orchestrators)) | claude-squad, gastown, ClawTeam, hcom, openswarm, Vigil | Run N Claude Code/Codex sessions in tmux panes plus git worktrees, with a dashboard | Most are flat: **no subagent tree**, no budgets, no supervision semantics, and observation is just scraping the terminal |
| **Agent frameworks** | LangGraph, CrewAI, OpenAI Agents SDK, Claude Agent SDK, Google ADK, MS Agent Framework | Graph/role/handoff abstractions *inside* one process | Lifecycle across processes and machines; each implements only fragments of the actor model |
| **Durable execution** | Temporal, Restate, DBOS, Inngest, Cloudflare Workflows, Bedrock AgentCore | Crash recovery, retries, checkpoint and replay | Knows nothing agent-specific: tokens, context, a spawning hierarchy, semantic failure |
| **Observability** | Langfuse, Phoenix/OpenInference, AgentOps (2411.05285), Datadog; [OTel GenAI semconv](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md) | Span per LLM call, tool call and `invoke_agent` | The OTel agent spans are still in *Development* status and **do not define parent/child relations between agents, subagent spawning, or handoff**. Tracing is also passive: it observes but cannot act (GAAT 2604.05119) |
| **Agent OS (research)** | AIOS (2403.16971) | Kernel-style scheduling and context and memory management for LLM calls | Focus is resource scheduling of LLM calls, not supervision trees or observability of spawned agent hierarchies |

## 2. Relevant research threads

- **Runtime patterns.** The SDB paper (2605.20173) treats the *stochastic–deterministic boundary* (proposer → verifier → commit/reject) as the core primitive of an agent runtime. It catalogs six patterns, including hierarchical delegation, scatter-gather + saga, and supervisor + gate.
- **Delegation and authority.** Bounded Agents / APC (2608.15888) addresses the problem that subagents inherit authority without limits. It carries delegated *scope and budget* down the principal chain and checks each request against accumulated session state.
- **Governance in the loop.** GAAT (2604.05119) extends OTel with governance attributes and a policy engine that reacts in under 200 ms, turning an observe-only system into one that can enforce.
- **Evidence and replay.** NovaFabric (2609.12582) records tamper-evident, replayable "Run Capsules" of agent runs.
- **Failure attribution.** Who&When (2505.00212) finds that even the best method identifies the responsible agent 53.5% of the time and the failing step only 14.2% of the time. Adaptive Influence Graphs (2608.24361) show that **structured trace representations markedly improve attribution**. MP-Bench (2603.25001) argues that failures often have several plausible causes. MAST (2503.13657) catalogs 14 failure modes.
- **Orchestration policy.** ProgRouter (2608.25992) routes each step of a workflow to a model based on progress, under cost and quality budgets. BOT-Orch (2605.27073) treats delegation as a bandit problem that accounts for agent reliability.
- **Benchmarking the manager.** ClawArena-Team (2606.31174) measures how well a lead LLM can *manage* a subagent pool.
- **Warning on claimed gains.** "Science of Collective AI" (2602.05289) proposes the collaboration-gain metric Γ, which separates real collaboration from simply spending more budget.

## 3. The gap

> **⚠ Correction (2026-09-28):** Paperclip already ships a hierarchy (org chart), budgets with hard stops, OTel traces and an immutable audit log. The gap as written below is therefore partly filled. See `POSITIONING.md` for the revised gap: *dynamic, self-organized structure* plus *causal lineage*.

> Everyone either **runs** agents (session wranglers, frameworks) or **watches** them (tracing),
> but no runtime treats a swarm as a **supervised, budgeted, observable process tree**
> in which every spawn records its lineage, inherits a bounded budget and permissions,
> emits structured events, and can be paused, killed, restarted or replayed.

This is the "Erlang/OTP + cgroups + OpenTelemetry for LLM agents" slot. Practitioner write-ups keep calling for it (the Zylos notes on supervision trees and the actor model), but it does not exist as a coherent, measured system.

## 4. Sketch: what the infrastructure could be

**Core abstraction: the agent as a process.**
```
AgentProcess {
  aid, parent_aid, lineage[]          # process tree (like a PID tree)
  spec: {harness, model, prompt, tools, workdir/worktree, sandbox}
  budget: {tokens, $, wall_time, max_children, max_depth}   # inherited, must be ≤ parent's remaining budget
  caps:   {fs paths, network, tools, may_spawn}              # attenuated on delegation (APC-style)
  state:  PENDING|RUNNING|WAITING(human|child|tool)|DONE|FAILED|KILLED
  mailbox, outputs(artifacts), checkpoint_ref
}
```

**Components**
1. **Spawner/adapters.** A uniform `spawn()` over Claude Agent SDK, Claude Code headless, Codex, OpenHands, and raw API loops. Each agent runs isolated in its own git worktree, container, or both.
2. **Supervisor tree.** OTP-style restart strategies (one_for_one, one_for_all, escalate), plus agent-specific policies: stop on loops, restart with fresh context, escalate to the parent or a human.
3. **Budget and capability ledger.** Budgets and permissions are split hierarchically when a child is spawned. When a subtree runs out of budget, the parent is notified. This is the cgroups analogue.
4. **Event bus and trace model.** Emits OTel GenAI spans **extended with `agent.parent_id`, spawn/handoff links, and budget and state events**, which fills the gap in the semantic conventions. Events are stored append-only so runs can be replayed.
5. **Control plane (API + CLI + UI).** Tree view of the live swarm with per-node cost, status and diffs, plus pause, kill, inject-message, fork-from-checkpoint and "attach" to any agent.
6. **Policy hooks.** Gates at the stochastic–deterministic boundary, such as a verifier before merge or commit, and a human approval inbox.

## 5. Research questions (what would make this a paper, not just a tool)

| RQ | Measurement | Related work |
|---|---|---|
| RQ1. What is the overhead of full supervision and tracing as N grows (10 → 1000 agents)? | Latency, throughput, storage per agent-hour | AIOS |
| RQ2. Do lineage-aware structured traces improve **automated failure attribution**? | Accuracy on Who&When, MP-Bench, and your own swarm traces vs. flat logs | Who&When, AIG |
| RQ3. Do hierarchical budgets and supervision reduce **cost blow-ups** and runaway failures (loops, fan-out explosions) at equal task success? | $ per solved task and failure-mode counts (MAST) on SWE-bench-style tasks | ProgRouter, MAST |
| RQ4. Which delegation topology and supervision policy maximizes **collaboration gain Γ** under a fixed budget? | Γ across tree, flat and swarm topologies | Science of Collective AI, ClawArena-Team |
| RQ5. Can the runtime serve as a **substrate for swarm self-improvement** (DGM/GEA-style), where the evaluator is outside what agents can edit and every edit is recorded? | Tamper detection, reproducibility | Links back to `LIT_REVIEW.md`: harness tampering, GEA |

## 6. Suggested MVP path
1. **Week 1–2.** Single-machine runtime in Python (or Go/Rust for the daemon). Agent-as-process abstraction, `spawn` over Claude Agent SDK and Claude Code headless, one worktree per agent, SQLite event log, CLI tree view.
2. **Week 3–4.** Budget and capability inheritance, supervisor restart policies, OTel export with the parent/child extensions, kill/pause/inject.
3. **Week 5–6.** Web UI showing the live tree. Replay from the event log. Run RQ1 and RQ3 experiments.
4. **Later.** Multi-node deployment (a Temporal/Restate backend or your own), failure-attribution experiments (RQ2), and the self-improvement substrate (RQ5).

## Sources
[awesome-agent-orchestrators](https://github.com/andyrewlee/awesome-agent-orchestrators) ·
[OTel GenAI agent spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md) ·
[OTel GenAI observability blog (2026)](https://opentelemetry.io/blog/2026/genai-observability/) ·
[O'Reilly: open source agent toolkit 2026](https://www.oreilly.com/radar/the-open-source-agent-toolkit-in-2026/) ·
[Arize: agent observability tools 2026](https://arize.com/blog/best-ai-observability-tools-for-autonomous-agents-in-2026/) ·
[Zylos: supervisor trees for AI agents](https://zylos.ai/research/2026-03-16-supervisor-trees-fault-tolerance-ai-agent-systems/) ·
[Zylos: actor model for MAS](https://zylos.ai/research/2026-03-10-actor-model-communicating-agent-patterns/) ·
[Zylos: durable execution for agent runtimes](https://zylos.ai/research/2026-04-24-durable-execution-agent-runtimes/) ·
[Durable AI agents 2026 (Temporal/Inngest/DBOS/Restate)](https://www.reactify-solutions.com/articles/durable-ai-agents-2026) ·
[InfoQ: Cloudflare ADLC](https://www.infoq.com/news/2026/09/cloudflare-adlc-agents/)
