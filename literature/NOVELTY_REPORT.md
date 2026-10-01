# Novelty Check Report

*2026-09-28. Sources: arXiv API and WebSearch. All 30 prior-work papers passed arXiv verification (`.aris/verify-papers/verified_novelty.json`).*

> ⚠ **Phase C (cross-model review) was not run.** No Codex MCP reviewer is available in this session, so these verdicts are single-model (Claude) judgments. A second opinion via `/research-review` or an external reviewer is recommended before committing.

## Proposed Method
A multi-agent runtime that (T1) records causal lineage natively at execution time (spawn edges, message and artifact provenance, the exact context each LLM call consumed) to make failures attributable, and (T2) lets swarms restructure themselves (spawn/merge/prune) under runtime-enforced invariants, beating fixed hierarchies on collaboration gain Γ at equal cost.

## Core Claims

1. **Structured and causal traces improve attribution over flat logs.** *Closest:* CHIEF "From Flat Logs to Causal Graphs" (2602.23701), GraphTracer (2510.10581), AgentTrace (2603.14688), DCFA (2609.04749), FALAT (2606.00765), AIG (2608.24361), TraceElephant (2604.22708): full traces give up to +76%.
   **Status: TAKEN as a general claim.** At least 8 papers already show it.

2. **Dependencies recorded at runtime (ground truth) beat dependencies inferred after the fact.** *Closest:* GRADE (2606.22741) grades each dependency edge as observed, declared or inferred, then tests the observed edges against a counterfeit. **It finds that dependency attachment adds ~no failure-prediction signal** (mean diff −0.0003). ASCon (2608.10646) finds LLM-inferred graphs give no consistent gain over plain graphs.
   **Status: OPEN but CONTESTED.** GRADE is a *negative* result for *prediction*, using a linear probe. Nobody has tested whether ground-truth lineage improves attribution (who and which step) in dynamically spawned agent trees.

3. **Lineage-enabled interventional attribution (fork from a checkpoint and re-run).** *Closest:* Causal Agent Replay (2606.08275; SCM + do-operator + Shapley), AgenTracer (2509.03312; counterfactual replay to build labels), CausalFlow (2605.25338).
   **Status: The method is known.** Every one of these assumes replay is possible, which is cheap in toy multi-agent systems and hard with real tools, worktrees and spawned processes. *Delta:* a runtime that makes replay cheap and faithful for real swarms is a systems contribution these papers don't make.

4. **Runtime restructuring under safety invariants.** *Closest:* ATM "Autonomous Topology Mutation" (2607.20488): factorizes an overloaded agent into sub-agents, gated by capability monotonicity, state-routing completeness and shadow validation. Also: Progressive Risk Vesting (2609.01035; risk-budget escrow for recursive agent trees, with a harm bound), When Child Inherits (2605.08460; invariants at spawn time), Recursive Agent Harnesses (2606.13643; depth-bounded recursive spawning), Puppeteer (2505.19591; orchestration learned with RL), DeLM (2606.10662).
   **Status: MECHANISM TAKEN.** ATM + PRV together already cover "self-restructure under invariants".

5. **Self-restructuring beats fixed hierarchies on Γ at matched cost.** *Closest:* ATM compares against its own overloaded starting configuration (3.3%→61.7%) and reports **no cost matching and no fixed-org or single-agent baseline**. "Science of Collective AI" (2602.05289) defines Γ but doesn't test self-restructuring.
   **Status: OPEN as a finding.** This is empirical, not a method, and it could come out negative.

## Closest Prior Work

| Paper | arXiv | Date | Overlap | Key difference from you |
|---|---|---|---|---|
| **GRADE** | 2606.22741 | 2026-06 | Asks the same question: what does recording "what each step relied on" add? | Failure *prediction* with a probe; mostly a negative result; no runtime; no dynamic spawning |
| **CHIEF** | 2602.23701 | 2026-02 | "Flat logs → causal graphs" for multi-agent attribution | Graph built *after the fact* from Who&When logs |
| **GraphTracer** | 2510.10581 | 2025-10 | Information-dependency graphs for attribution | Inferred dependencies; fixed MAS |
| **AgentTrace** | 2603.14688 | 2026-03 | Causal graph tracing with no LLM inference, sub-second | Reconstructed from logs; synthetic scenarios |
| **TraceElephant** | 2604.22708 | 2026-04 | Full observability improves attribution by up to 76% | A benchmark, not a runtime; fixed MAS |
| **Causal Agent Replay** | 2606.08275 | 2026-06 | Interventional attribution with Shapley credit | Assumes re-execution; single agent; synthetic SCMs |
| **AgenTracer** | 2509.03312 | 2025-09 | Counterfactual replay + fault injection | Offline labeling; fixed MAS |
| **PROV-AGENT** | 2508.02866 | 2025-08 | Runtime provenance capture (W3C PROV + MCP) | Scientific workflows; no attribution evaluation |
| **ATM** | 2607.20488 | 2026-06 | Runtime restructuring + safety invariants | Triggered by overload, one level deep, no cost matching, no Γ |
| **PRV** | 2609.01035 | 2026-09 | Risk budget for recursive agent trees | Theory + stylized models; risk, not cost/Γ |
| **RL via orchestration traces** | 2605.02801 | 2026-05 | Spawn/delegate/stop as trace events for credit | Survey; notes *counterfactual message-level credit is sparse* and *no RL for stopping* (supports you) |

Also in the crowd: VerifyMAS, DCFA, FALAT, ASCon, AgentTether, AIG, MP-Bench, NeuroTaint, Agent-BOM, Matrix (provenance integrity), RAH, When Child Inherits, SOAN, DeLM.

## Overall Novelty Assessment

- **T1 (lineage → attribution): 5/10. PROCEED WITH CAUTION.** "Graphs beat flat logs" is taken, and GRADE has a *negative* result on the core hypothesis. Specifically, the delta is thin because every graph method already beats flat logs.
  - **What would make it carry:** (a) ground-truth context-consumption lineage in **dynamically spawned trees with real tools**, which no benchmark has (Who&When and TraceElephant are fixed teams); (b) evaluation on **attribution**, not prediction, including a direct test of GRADE's counterfeit-edge control; (c) **cheap checkpoint-fork interventional attribution** as a runtime capability.
- **T2 (self-restructuring + invariants): 4/10 as a method, 6/10 as a finding. PROCEED WITH CAUTION.** Don't claim the mechanism (ATM and PRV have it). The *finding*, cost-matched Γ of self-restructuring vs. a fixed org vs. a single agent, is open.
- **Combined idea: 6/10. PROCEED.** No single paper contains *"a runtime whose native lineage and fork/replay make interventional attribution and structural credit assignment cheap for dynamically spawning swarms."* The field has attribution methods that assume data and replay it doesn't have, and runtimes that don't produce either.
- **Risks a reviewer would raise:** "GRADE showed dependency edges don't help"; "CAR/AgenTracer already do counterfactual attribution"; "ATM already does safe restructuring"; "Paperclip already has traces".

## Suggested Positioning

> **Existing failure attribution methods infer causal structure after the fact from fixed-team logs and assume replay is possible. We build the runtime that makes both real: ground-truth lineage and cheap checkpoint-fork replay for dynamically spawning agent swarms. We use it to show (i) when recorded dependencies do and don't help attribution, which resolves GRADE's negative result, and (ii) how to assign credit to structural decisions (spawn, delegate, stop).**

A reviewer could check the delta: *no prior paper evaluates attribution on dynamically spawned agent trees with ground-truth runtime lineage and interventional replay.*

### Concrete first pilot (cheap, decisive)
1. Run ~200 real tasks with dynamic spawning (Claude Code headless with subagents) through a thin lineage-recording wrapper.
2. Inject faults (AgenTracer-style) at known agents and steps, which gives ground-truth labels.
3. Compare attribution accuracy using four inputs: flat trace, post-hoc inferred graph (GraphTracer/CHIEF-style), runtime lineage, and runtime lineage + fork-replay.
4. **Go/no-go:** if runtime lineage doesn't beat the inferred graph by a clear margin, T1 as a headline claim is dead. Pivot to the substrate/replay contribution.
