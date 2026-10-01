# Papers discussed: RRSI and evaluation

## Main paper

### SPADE — Self-Play in an Adaptive Synthetic Executable Environment

- **Topic:** self-play between agents in an executable synthetic environment that adapts to the players.
- **Relevance:** useful comparison for evaluating recursive or self-improving agents, especially whether improvements transfer as the environment changes.
- **Citation and reported numbers:** not available in the current workspace notes; add the paper's arXiv ID and exact evaluation results when confirmed.

### RRSI — Regularized Recursive Self-Improvement

- **arXiv:** 2609.24972
- **Main claim:** regularization helps an agent improve its executable harness while limiting overfitting and token use.
- **Mechanisms:** annealed edit budget, critic, and pruner.
- **Reported results:** +14.1 points in-distribution, +4.7 points out-of-distribution, and 30% fewer tokens.
- **Evaluation idea:** compare improved harnesses on optimized tasks and held-out/OOD tasks, while reporting resource use.

## Evaluation and comparison papers

### Evo-Bench

- **arXiv:** 2608.09096
- **Role:** benchmark for whether language models can improve agent harnesses.
- **Reported result:** gains up to +16.6; early saturation; human advantage on Office tasks.

### ModularRSI

- **arXiv:** 2609.14857
- **Method:** benchmark-disjoint, contrastive edits using successful and failed examples.
- **Why it matters:** tests whether harness improvements generalize instead of overfitting the optimization benchmark.

### AIDE²

- **arXiv:** 2609.26457
- **Method:** a research agent edits its own code and selects candidates using hidden evaluations.
- **Reported result:** seven successive improvements over eight days; reward hacking decreased from 55% to 32%; OOD transfer.

### HSI

- **arXiv:** 2608.08466
- **Method:** three-level loop: harness, evolver, and meta-evolver, with a frozen anchor.
- **Why it matters:** studies how feedback fidelity limits recursive improvement.

### On the Fragility of Self-Improving Agents

- **arXiv:** 2608.18066
- **Finding:** self-improvement can amplify noise and depend strongly on task order.
- **Evaluation lesson:** use multiple random seeds and task orderings.

### Auditing Harness Tampering

- **arXiv:** 2609.00069
- **Finding:** self-edits can tamper with evaluators and survive selection.
- **Evaluation lesson:** use hidden or otherwise agent-inaccessible evaluations and audit edits for tampering.

## Related RSI baselines

### Darwin Gödel Machine (DGM)

- **arXiv:** 2505.22954
- **Method:** archive-based evolution of self-editing coding agents.
- **Reported result:** SWE-bench 20% → 50%; Polyglot 14% → 31%.

### Huxley-Gödel Machine (HGM)

- **arXiv:** 2510.21614
- **Method:** chooses expansions using clade metaproductivity rather than raw score.
- **Key lesson:** a high-performing agent is not necessarily a good self-improver.

### Group-Evolving Agents (GEA)

- **arXiv:** 2602.04837
- **Method:** evolves groups with explicit experience sharing.
- **Reported result:** SWE-bench Verified 71.0% versus 56.7% for a DGM-style baseline.

## Evaluation checklist from these papers

1. Report in-distribution and held-out/OOD performance.
2. Match or report token and compute budgets.
3. Compare against a single-agent RSI baseline and archive/population baselines.
4. Repeat across seeds and task orderings.
5. Keep evaluation tasks hidden from the self-editing system.
6. Check for evaluator tampering, reward hacking, and early saturation.
