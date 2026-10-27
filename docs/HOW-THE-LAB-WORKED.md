# How the lab worked

TL;DR: one coordinator session owned the plan and the queue; a handful of agent **lanes** each owned one kind of work; every experiment (an **arm**) had a pass/fail rule written and hashed before any run that could decide something; a cheap judge triaged, an expensive judge confirmed; held-out data stayed behind scripts; independent reviewers read the claims and the wording before anything went out; negative results were registered, not buried. The author, r4to, set the direction and made every irreversible call.

## Roles

| name | what it was |
|---|---|
| **Coordinator** ("ai research") | the session that read the queue, froze criteria, ran or delegated arms, wrote the reports and the handoffs between sessions. It owned `rnd/research/QUEUE.md` and `rnd/research/coordinator/`. |
| **Sonar, Anvil, Compass** | the three continuous researchers (`rnd/research/MANDATE.md`): Sonar = retrieval and health content; Anvil = models, quantisation, latency; Compass = evaluation, safety and the fast loop. Each turned findings into a technique card the runner could A/B. |
| **Forge** | native performance, the benchmark phone app and the deep tier (a 35B mixture-of-experts model on a 12 GB-class phone). |
| **Kiln** | the runner: it executed arms through the harness on the mini (an Apple-silicon Mac mini) and wrote run logs. Researchers proposed, Kiln ran. |
| **Summit** | the high-level strategist, called only with a dossier and a decision that was expensive to reverse (`rnd/research/SUMMIT.md`). It never looped. |
| **Lantern, Plumb, Veil** | the September lanes: Lantern built bench v0 and the landscape notes; Plumb drove the physical iPhone; Veil kept the blind sets and the legal checks (its material is not in this record). |
| **Independent reviewers** | fresh agent sessions with no stake in the draft, used for claim text, wording, content decisions and audits (`CLAIM-REVIEW-*.md`, `PIPELINE-AUDIT-*.md`, `LEDGER-AUDIT-*.md`, `CRITIQUE-*.md`). |
| **Maestri** | the canvas tool that hosted the lanes as agents. |

## The loop

1. **Propose.** A lane writes a card: hypothesis, the arm to run, the criterion, the cost.
2. **Freeze.** The coordinator copies the criterion into `<ARM>-criterion.md`, takes its sha256, and only then runs (template: `rnd/research/coordinator/arms/_lib/CRITERION-TEMPLATE.md`; examples: the arm folders). A criterion is never edited after verdicts exist; a change is a dated addendum.
3. **Gate, then slice, then full.** Deterministic gates first (replayed retrieval, no model call), then a 20-item slice judged by the cheap judge (L1), then the full set judged by the strong judge (L2, both A/B orders, two seeds, bootstrap CIs). L1 and L2 numbers are never mixed in one cell (`L1-PROTOCOL.md`).
4. **Verdict and log.** The result is appended to `QUEUE.md` with the numbers and the verdict against the frozen rule. A negative result becomes a row in `CLOSED.md` with its minimum detectable effect and what would reopen it.
5. **Loop.** From 2026-10-11 an unattended loop (`LOOP-PROGRAM-2026-10-11.md`, `LOOP-V2-2026-10-14.md`) picked the next proposed arm from `BACKLOG.md` within spend caps; the 10-14 retrospective (`retro-2026-10-14/`) turned its lessons into the v2 rules.

## Discipline that the record lets you check

- **Held-out data.** Held-out and burnt sets are touched only through scripts that print aggregates; every exposure is a row in `EXPOSURES.md`; a set that has been seen is dev data from then on. The final number needs a set written outside the Claude family (bench v0.3 / v0.4).
- **Judge limits.** The judge is closed, paid and not bit-reproducible. The first references and the judge are the same model family, so a cross-family judge (OpenAI gpt-5.6-sol via the Codex CLI) re-scored existing traces: the Claude judge is the stricter family by about 0.10 on both sets, the ranking is unchanged, and the win rate does not move. Every ratio is reported with its judge family.
- **Seed noise.** A one-seed deep-tier delta below about 0.05 on the bounty-style set is treated as seed noise (rule raised after `CRITIQUE-2026-10-16.md`).
- **Three scales, always together** (raw, floor-adjusted, win/tie/loss), because the raw ratio is flattered by the rubric floor.
- **Autonomy and spend.** Free local compute by default; paid APIs only when no free equivalent existed, capped and logged. Usage and spend lines are not part of this release.
- **Reviews.** Claim drafts went through independent reviewers (`CLAIM-REVIEW-*.md`, verdicts "accept with edits" and the edits applied); pipeline audits re-checked the ledgers.

## Where things are

`rnd/research/coordinator/arms/` has one folder per arm; `rnd/research/QUEUE.md` is the chronological index; `docs/TIMELINE.md` is a dated one-line-per-entry view of it; `data/` has facts, decisions and experiments as structured rows.
