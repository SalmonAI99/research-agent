# Positioning: How to Stand Out

*2026-09-28. Supersedes the "gap" section of INFRA_LANDSCAPE.md. Paperclip already covers budgets, a hierarchy, OTel traces and audit.*

## 1. What the competition actually does

| | **google/ax** | **Paperclip** (90k★) | **OpenHands SDK** |
|---|---|---|---|
| Metaphor | Kubernetes for agent tasks | A company: org chart, tickets, employees | A library: a main agent calls a delegate tool |
| Unit | Sandboxed Task + Workspace + Model | Long-lived agent "employee" with a role | In-process sub-agent conversation |
| Hierarchy | **None** (flat tasks) | **Static org chart designed by a human**; delegation via tickets | Dynamic, but inside one framework and one process |
| Budgets | None | **Yes**: per-agent/project/goal, hard stop | Not a runtime concept |
| Supervision | suspend/resume; no restart policy | Heartbeat wake queue; pause on overspend | Up to the caller |
| Observability | `ax watch`, `ax ssh` | **OTel traces, immutable audit log, cost events** | Event stream per conversation |
| Strength | Scale (billions of tasks), isolation | Governance and management UX | Developer ergonomics |

## 2. What you should not compete on
- **Management UX, dashboards, adapters.** Paperclip has 90k stars and a head start.
- **Scale and isolation.** Google plus Kubernetes.
- **"Yet another orchestrator".** There are 100+ on awesome-agent-orchestrators.

A system paper whose contribution is "we built an orchestrator with features X, Y, Z" will be read as engineering, not research.

## 3. What none of them do (the real openings)

All three share one assumption: **the structure of the swarm is fixed or human-designed, and observation means logging.**

- In Paperclip the org chart is drawn by a human. In AX there is no structure. In OpenHands the structure is whatever the calling code hard-wires.
- Their traces record *what happened*. None of them can answer *why the outcome happened*, meaning which agent, which delegation and which piece of context caused it. The research says this is unsolved: Who&When finds the failing step only 14.2% of the time.

That leaves two openings:

**Opening A: causal observability.** The runtime records *lineage*: who spawned whom, which message or artifact flowed where, and which context each decision consumed. Blame and credit then become queries over that record, not a matter of an LLM reading logs.

**Opening B: self-organizing structure.** Agents themselves spawn, merge, prune and re-route, so the tree grows and shrinks on its own (this is literally the agentlang README). The runtime enforces the invariants (budget conservation, bounded depth and fan-out, capabilities that can only narrow on delegation), so self-restructuring is *safe*.

These two openings depend on each other. B needs A to be debuggable and learnable, and A is only interesting when the structure is dynamic. A static org chart is easy to read by eye.

## 4. Candidate thesis statements (pick one)

**T1 (systems, most tractable):**
> "A runtime that records causal lineage for spawns, messages and artifacts makes multi-agent failures attributable: it reaches X% agent-level and Y% step-level attribution vs. Z% with flat traces, at under W% runtime overhead."

- Falsified if lineage doesn't beat flat OTel traces on Who&When / MP-Bench-style tasks.
- Evaluation: Who&When, MP-Bench, plus failures you inject into your own swarm runs.

**T2 (the ambitious claim):**
> "Swarms that restructure themselves under runtime-enforced invariants achieve higher collaboration gain Γ than fixed hierarchies at equal cost."

- Falsified if a fixed org (Paperclip-style) or a single agent with the same budget matches it.
- Evaluation: SWE-bench-style or research tasks, comparing Γ against flat, fixed-tree and single-agent baselines at matched $.

**T3 (bridges to self-improvement):**
> "Lineage is the credit-assignment signal that makes swarm-structure self-improvement work."

This ties to DGM/HGM's clade metaproductivity, applied to the swarm's structure instead of agent code.

## 5. Recommendation
- **Paper 1 = T1.** Scoped for a systems venue, falsifiable in about 3 months, and it builds the substrate.
- **Paper 2 = T2 on top of it.** This is where the "brain that grows and shrinks" vision pays off.
- **Build:** a small runtime with lineage-first events, 1–2 adapters (Claude Code headless + a raw API loop), and invariant enforcement.
- **Do not build:** a web dashboard, k8s support, ticket systems, or many adapters.
- **One-sentence pitch:** *"Paperclip gives agents an org chart; we let the swarm draw its own org chart, and we can tell you exactly why it worked or failed."*
