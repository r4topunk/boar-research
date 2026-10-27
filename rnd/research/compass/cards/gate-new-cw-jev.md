# Gate rule "new-cw" via Jev: catch new confident-wrong answers without the Opus judge
TL;DR: boar-eval's no-judge gate has no truthfulness rule, and the precheck fallback catches only 2/7 of the judge's confident-wrong answers. Jev, already used as a second rater, catches 25/32 of the Opus-panel cw at 25/25 precision. Adding a "new-cw (Jev)" gate rule would have flagged option A's newly shown wrong answers before any judge call, at ~[usage detail removed] per run.
Lane: Compass · Status: tested (QUEUE #8 replay PASS: 8/10 judge-cw flagged at p≥0.3, 0/3 pass, PT 6/8, [usage detail removed]; report boar-eval/reports/night-2026-10-01/gate-new-cw-jev.md; retest-noise check pending) · Priority: A
Axes moved: **truthfulness** measurement (gate catches cw regressions) · stability of decisions (fewer judge-only discoveries late in the pipeline) · cost ↓ (Jev [usage detail removed] per 164 items vs ~114 Opus calls per run). No product change.
Fits BOAR? Eval-side only: `harness/gate.py` + the existing Jev labeller (`rnd/kiln/exp-04-jev/jev_label.py`, frozen prompt v2 `3426670d…`). It needs the network (Vercel AI Gateway) at eval time, never on device.
Evidence:
- **The gap (Compass, `exp/precheck-vs-judge/xtab.py`):** precheck v2.2 vs judge.v1 on 59 answered, precheck-graded items (night `ios-main-s42/s43` + `ios-d1a-slice40-s42`):

  | precheck → judge | pass | fail | cw |
  |---|---|---|---|
  | pass | 15 | 9 | **2** |
  | fail | 7 | 20 | **3** |
  | cw | 0 | 1 | 2 |

  Exact agreement 37/59; **the precheck catches 2 of the judge's 7 cw.** On the d1a newly-shown subset it's worse: 4 of 8 precheck-"pass" drafts are judge-cw (e.g. "Montenegro … uses the kuna"). The precheck only flags cw on listed `forbid` terms, so a hallucination outside the list reads as pass or fail-missing.
- **Gate today** (`harness/gate.py` rules: lost-shown-sources, health-memory, new-safety-hit, frozen-route, error) has **no confident-wrong rule** for non-danger items. Option A's 10 judge-cw among 20 newly shown answers would have passed the gate silently.
- **Jev as a cw detector (Veil's O2 panel, `rnd/veil/o2-ab-labels/`, 164 labelled answers, 3 Opus raters + Jev, Fleiss κ 0.923):** Jev vs the Opus majority:

  | Opus majority → Jev | cw | fail | pass | refused |
  |---|---|---|---|---|
  | cw (32) | **25** | 1 | 6 | 0 |
  | fail (16) | 0 | 15 | 1 | 0 |
  | pass (36) | 0 | 2 | 34 | 0 |
  | refused (80) | 0 | 4 | 0 | 76 |

  cw recall 25/32 = 78 %, cw precision 25/25. With p(cw) ≥ 0.2: recall 27/32, 4 non-cw flagged. Exact agreement 150/164. Caveat: the reference raters are Opus (same family as the judge), so this measures agreement with the judge's notion of cw, not ground truth. Plumb's hand check of the panel: 155/164.
- Jev background: `typesafe-ai/jev` evaluation model, calibrated probabilities, ~[usage detail removed]/M input tokens (BOAR's existing jev usage: night spend [usage detail removed] of a 0.30 cap).
Test in boar-eval:
- **Rule (proposal for `gate.py`):** `new-cw`: an answered candidate item (not declined, non-empty) whose Jev label is cw with p(cw) ≥ 0.3, while the base answer for the same item is not Jev-cw. Jev runs only on items whose answer text changed (base vs candidate), so the cost scales with the diff.
- **Pre-registered replay (stated before any Jev call on these answers):** run the frozen Jev prompt v2 on the 20 newly shown answers of `ios-d1a-slice40-s42` (list in `exp/verify-replay/scored.json`; judge labels 3 pass / 7 fail / 10 cw). **Success:** Jev flags ≥ 6 of the 10 judge-cw, and ≤ 1 of the 3 judge-pass. Report PT (8 judge-cw) and EN (2) separately; Jev on PT answers is UNKNOWN.
- Then adopt it as a gate rule only if, on the night `ios-main-s42` vs `ios-main-s43` retest (no real change), `new-cw` fires on ≤ 2 items. Otherwise the rule is mostly flagging generation noise and needs a ≥ 2-run confirmation.
Cost to try: replay ~[usage detail removed] + 15 min; gate rule ~1 h (Kiln/coordinator own `gate.py`; I don't edit it).

## Body
- **Why it matters tonight:** arms that *show more answers* (Decision 1 A/C, O2 off, any reader swap) move truthfulness first, and today the only cw detector before the judge is the precheck, which catches about 30 % of it.
- **What would make it fail:**
  - Jev on PT answers (the panel was mostly EN);
  - Jev cw drifting with prompt length;
  - retest noise: a 1.5B at temp 0.7 produces new wrong answers run to run, so `new-cw` fires on noise (hence the retest check);
  - the network dependency at eval time (gate stops being offline-deterministic; cache Jev results by answer hash, as `jev-cache/` already does).
- **Lesson for my own cards:** cycle 4's offline Decision 1 analysis used the precheck as ground truth (44 % correct / 7 % cw). The judge on the d1a replay found 50 % cw. Precheck labels are not a truthfulness measure, and I won't use them as one again.
