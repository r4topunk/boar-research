# CVO v0.1 EN L1 (s44 + s45, cut3-confirm config, judge.v1-med on changed items): PASS (with two flags)

TL;DR: CVO changes **0 answers** versus a same-day cut 3 control (120/120 byte-identical). It routes the same 4 `lan-cmp-*` items as CVS/CVH (both seeds); on all of them the computed verdict agreed with cut 3's own verdict, so no sentence was rewritten. Every Step 1 gate passes; flags: (1) the routed-item added time is +3.95 s against a +4 s bar, and (2) cut 3 itself drifted on `lan-exp-007` since cut3-confirm, which makes the stored-baseline Δ read -0.0018.

## Build
- Branch `coord/cvo` (wt/cvo, from coord/cvs daa65c8a), one local commit, nothing pushed. node_modules symlinked as in wt/cvs.
- The CVS "CV answers instead" block in `answer.ts` is removed. The normal cut 3 answer (VG v3 included) runs first; the CVO step sits right after the VG block, before the uncited preface, so cut 3's later steps see the same text as before.
- New `src/routing/verdictOverride.ts`:
  - `routeOverride` accepts only CV plans of kind compare or threshold (literal, distance, date and superlative are never touched, as in the criterion's "compare2 + threshold").
  - `overrideVerdict` makes the facts call, runs the CVS sanity guard (inside `computeCompare` / `computeThreshold`) and computes the verdict, then compares it with the answer's.
  - Reason codes: `cvo:routed` whenever the facts call ran, `cvo:override-<kind>` when the text changed.
- `computedVerdict.ts`: `answerPlan` split into `computeFromPlan` (facts call + guard + compute) and the render; CV's own output is unchanged.
- `verdictGuard.ts`: two exports appended and nothing else changed (VG behaviour identical; verdictGuard tests unchanged):
  - `answerVerdict`: reads the answer's first sentence the VG v3 way. A leading Yes/No for yes/no questions; for which-questions the named entity plus comparative, mapped through the question's polarity, exactly as `checkCompare`.
  - `replaceVerdictSentence`: swaps only VG's first segment; everything else stays byte-identical.
- Rewrite: the verdict sentence becomes the engine's computed verdict line, and one line "Facts (model recall): <fact lines joined by "; ">" is appended after a blank line. Anything unreadable (no leading Yes/No, entities not found, mixed sentence) leaves the answer alone.
- Same scope guards as CV: EN, fast tier, no health, no detector fire, no reused sources, no place, not multipass.
- Tests: vitest **1377/1377** (CVS had 1364). New `verdictOverride.test.ts` (13) plus 5 answer-level tests in `answer.test.ts` (they replace the 4 old CV-answer tests). They cover:
  - agree: identical;
  - disagree: only the verdict sentence changes, plus the Facts line (which-form, threshold, yes/no);
  - guard fail: identical, with the facts call made;
  - non-routed: no facts call (1 generation);
  - PT and health: no CVO;
  - unreadable verdict, unparseable facts and a throwing generate: no override.
- tsc clean. The patch applies to a fresh `git archive 0cfd4a77` (tsc clean and 1377/1377 there).
- Patch `arms/cvo/cvo-on-cut3.vs-0cfd4a77.patch`, sha256 `bf303b29acb876d7d70d34dd23d4b3551dfa1ee55cd165631f3777c0ac61627f`, 1377 unit tests.

## Run
- Tree `be-0cfd4a77-cvo` (setup.sh + be-ship adapter 949eee03 copied from the cut 3 tree, PATCH_SHA256 checked by the script), detector v3b, `--places` kit-vexact, Android 12 GB 4B, kit A, cut3-confirm requests re-keyed (arm cvo), heavy lock (HEAVY_CLASS=normal), seeds 44 and 45: 60/60 valid, 0 errors each. Script `rnd/kiln/l1/cvo-l1.sh`; traces `boar-eval/runs/kiln/cvo-l1/cvo-v01-s4{4,5}.traces.jsonl`.
- **Byte identity vs the stored cut3-confirm traces: 59/60 in each seed.** The one difference is `lan-exp-007` (Greenland, non-routed, no `cvo:*` code, identical route codes and context sizes).
- Control (`rnd/kiln/l1/cvo-l1-ctl.sh`, traces `cvo-l1/ctl/`): cut 3 re-run today on its own tree with the same requests. It differs from the stored cut3-confirm on **the same item, `lan-exp-007`, in both seeds**, and CVO equals this same-day cut 3 on **120/120** answers.
  - A 5-item probe (`cvo-l1-noise.sh`, twice per tree) shows the cut 3 tree and the CVO tree give the same `lan-exp-007` text, repeatably, so the difference is drift in the cut 3 baseline since Oct 4, not CVO.
  - UNKNOWN: the cause of the drift (the mini's state, not the engine patch).
- Judge: `cvo-l1-judge.sh` judges the items that differ from the stored cut 3 (only `lan-exp-007`, both seeds, both orders, `--effort medium`, 8 calls); cut 3's stored verdicts are reused elsewhere (cut 3 ratio reproduces 0.5656). Analysis `cvo-l1-analyze.py` -> `cvo-l1/analysis.txt`; control and timing `cvo-l1-ctl-analyze.py` -> `cvo-l1/ctl-analysis.txt`.

## Routed items (the facts call ran): no overrides
- `lan-cmp-001`, `-002`, `-004`, `-005`, both seeds (8 of 120). Zero `cvo:override-*`: each time the computed verdict was defined, passed the guard and **agreed** with cut 3's verdict, so the answers are returned byte-identical. This is the design working: CVS/CVH lost 0.75-1.08 on these items by replacing or steering the prose, and CVO does not touch it.
- It also means v0.1 has no item where cut 3's verdict is wrong and the computed one is right, so L1 cannot show CVO's upside. Step 2 does that.

## Step 1 gates
| gate | result |
|---|---|
| no changed item down >= 1.0 | **PASS**: 0 items changed by CVO. Against the stored baseline only `lan-exp-007` (drift) differs: 3.833 -> 3.333 (-0.500; s44 3.33 -> 2.50, s45 4.33 -> 4.17) |
| unsafe (safety v0.9.1) | **PASS**: 0 in s44, 0 in s45 (cut 3: 0, 0) |
| confident-wrong not up | **PASS**: 4 / 5 (s44 / s45), identical sets to cut 3 |
| paired Δ >= 0 (57 items, two-level bootstrap seed 11, 2,000) | **PASS** vs same-day cut 3: Δ = 0.0000 exactly (identical answers). Flag: vs the stored cut3-confirm verdicts the number is cut 3 0.5656 -> CVO 0.5638, **Δ -0.0018**, CI90 [-0.0059, 0.0000], and all of it is the `lan-exp-007` drift (no CVO change). The coordinator should confirm which baseline the criterion means. |
| median added time on routed items <= +4 s (desktop proxy) | **PASS, marginal**: **+3.95 s** (n = 8, range +3.7 to +4.39) vs the same-day cut 3 run. Flag: a separate interleaved 5-item probe gave +4.12 s (n = 8), and vs the stored cut3-confirm run +1.31 s (that run's mini load was lighter; its non-routed median is -2.3 s). The cost is one extra generation (the facts call) on every routed item, whether or not it overrides. |
| non-routed items add +0 | **PASS**: no facts call is made (`cvo:routed` appears only on the 8 routed rows; the 112 non-routed rows are byte-identical to the same-day cut 3), median timing diff -0.04 s (noise) |

Verdict: **PASS** on every Step 1 gate as measured against the same-day control. Two things for the coordinator, both about the measurement rather than CVO: the stored-baseline Δ of -0.0018 (caused by cut 3 drift on one item), and +3.95 s sitting 0.05 s under the time bar. Step 2 was not started.

## UNKNOWN
- Why cut 3 changed on `lan-exp-007` between Oct 4 and today (same tree, same requests).
- Phone latency of the extra call (desktop proxy only).
- CVO's accuracy effect: only Step 2's fresh gate can show it. L1 has 0 overrides.
