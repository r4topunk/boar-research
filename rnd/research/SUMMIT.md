# Summit: the high-level researcher (Fable), and when to call it

TL;DR: Summit runs on Fable, the most expensive tier, and stays idle until the coordinator (ai research) sends a brief. It never loops. It gets **few, big questions**: strategy, architecture, and decisions that are expensive to reverse. Each brief arrives as a self-contained dossier, so Summit spends its tokens on judgment and not on reading the repo.

## Call Summit only when ALL of these hold

1. **The question is high-level and consequential.** Its answer changes the plan for days, e.g.:
   - which architecture can reach > 0.50 of frontier+web under 12 GB offline by 2026-10-31;
   - which of several promising lines to drop;
   - how to frame the bounty claim;
   - how to adjudicate conflicting evidence between researchers.
2. **The evidence exists.** Measured numbers from boar-eval, not ideas. Summit synthesizes and decides; it doesn't do first-pass research. The Sonar, Anvil and Compass loops do that cheaply.
3. **Opus can't settle it.** Either the coordinator and the researchers disagree, or two serious Opus attempts left it open.
4. **A dossier is ready.** It has the question, the constraints, the measured numbers with file paths, the options with their evidence, and what would change the decision. It should be readable in about 10 minutes.

**Don't call it for:** routine triage, single-arm results, bug hunts, writing code, or anything a researcher card or a Kiln arm can answer.

**Budget:** ≤ 1 brief per day by default. A second brief needs a stated reason in the queue (`rnd/research/QUEUE.md`, Summit section).

## What Summit returns (one memo per brief, in `rnd/research/summit/`)

```
# <question>
TL;DR: <the decision, one sentence>
Decision · Confidence (low/med/high) · What would change my mind (kill criteria, measurable in boar-eval)
Ranked options with expected effect on the 7 axes and the bounty bar (> 0.50), cost, risk
The 1–3 experiments that would most reduce uncertainty, each with a frozen success criterion
UNKNOWN
```

## Rules

- Research and reasoning only. No edits outside `rnd/research/summit/`, no runs on the Mac mini, no iPhone, no GitHub writes.
- It reads the files the dossier cites, and nothing else unless it asks.
- English in files. Sources linked, with dates, when it uses outside evidence.

## Planned first call

After the night of 2026-10-01 → 02, once boar-eval has the shared-engine baselines (iPhone 1.5B, Android Qwen3-4B vs Gemma 4 E4B, judge scores) and the first arm results (#3 comparison split, #5 Wikivoyage lead gate, Decision 1 A/C, danger detector A1).

**Question:** given the measured gap to 0.50 and the three radars, what is the highest-expected-value path to the bounty bar by 2026-10-31, and what should we stop doing?
