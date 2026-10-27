# CVH v0.1 EN L1 (changed items only, judge.v1-med): FAIL

TL;DR: CVH (patch 282d8d6b...) changes the same 4 of 60 v0.1 EN answers as CVS (all `lan-cmp-*`, both seeds). Two of the four go down by >= 1.0, the paired Δ is -0.0034, and the routed items cost +5.5 s. Three of the five Step 1 gates FAIL. Per the frozen stop rule (no revision, any FAIL kills CVH), CVH ends here; Step 2 was not started.

## Build
- Branch `coord/cvh` (wt/cvh, from coord/cvs, one local commit, nothing pushed). Changes: `verdictHint()` + a `facts` field on the CV result in `computedVerdict.ts`; in `answer.ts` the CV block now calls `computedVerdictAnswer(..., { noSentences: true })` and, when it would have answered, appends the hint to the style reminder of the normal answer prompt. Same guards as CVS (EN, fast tier, no health, no detector fire, no reused sources or place, router + facts parse + sanity guard). New reason code `answer:cv-hint` (+ `cv:<kind>`).
- Hint text (added to the style section of the user turn): "A computed check from your recalled figures says: <verdict> Facts: <fact lines joined by "; ">. Lead with this verdict if it is consistent with your sources; keep your usual explanation and citations."
- Patch `arms/cvh/cvh-on-cut3.vs-0cfd4a77.patch` sha256 282d8d6b135f1329 (full: 282d8d6b135f1329df648717e59f2e5f0fc0017d39c22c60768f9f35ce095b88). vitest 1365/1365 (CVS had 1364: the 4 old CV answer tests became 4 CVH tests, +1 verdictHint unit); tsc clean; applies to a fresh `git archive 0cfd4a77`.
- Tests: hint present only when CV would have answered (Everest/K2: facts call + answer call, hint in the answer prompt, no CVS block); abstain (facts do not parse) gives the prompt byte-identical to the hinted one minus the hint sentence, with no hint; non-routed question: 1 call, no hint; health and PT: no hint.

## Run
- Tree `be-0cfd4a77-cvh` (setup.sh + patched runner be-ship 949eee03 copied from the cut3 tree), detector v3b on, `--places` kit-vexact, Android 12 GB 4B, kit A, same requests as cut3-confirm re-keyed (arm cvh), seeds 44 and 45, heavy lock, 60/60 valid, 0 errors. Script `rnd/kiln/l1/cvh-l1.sh`; traces `boar-eval/runs/kiln/cvh-l1/cvh-v01-s4{4,5}.traces.jsonl`.
- Byte identity vs cut 3 (`cut3-confirm`): 56/60 identical in each seed. Changed: `lan-cmp-001`, `-002`, `-004`, `-005` (Brazil/Russia, polar/grizzly, moose/bison, crocodiles). Exactly the items that carry `answer:cv-hint`; no hinted item came back identical, no unhinted item changed.
- Judge: `judge.mjs --effort medium --ids <the 4>`, both orders, 16 calls, run from the MacBook (`rnd/kiln/l1/cvh-l1-judge.sh`); cut 3 verdicts reused for the 56 identical items (cut 3 ratio reproduces 0.5656). Analysis `rnd/kiln/l1/cvh-l1-analyze.py`, output `boar-eval/runs/kiln/cvh-l1/analysis.txt`.

## Changed items (BOAR rubric, mean of 3 dims, both orders; mean over seeds)
| item | cut 3 | CVH | Δ | s44 (cut3 → CVH) | s45 |
|---|---|---|---|---|---|
| lan-cmp-001 | 3.667 | 4.083 | +0.417 | 3.67 → 4.33 | 3.67 → 3.83 |
| lan-cmp-002 | 3.083 | 2.000 | **-1.083** | 3.00 → 2.00 | 3.17 → 2.00 |
| lan-cmp-004 | 3.083 | 2.083 | **-1.000** | 3.00 → 2.17 | 3.17 → 2.00 |
| lan-cmp-005 | 2.750 | 3.500 | +0.750 | 3.00 → 3.67 | 2.50 → 3.33 |

What changed in the text: the model did follow the hint (verdict first, same winner as cut 3 on all 4), but it also restated the facts call's figures as its explanation and dropped cut 3's reasoning. Bear: "polar bears typically weigh around 450 kg, grizzly about 400 kg" (cut 3 explained body mass and length). Moose/bison: "bison 600 kg, moose 300 kg" (the 4B's own recalled figures, wrong by a factor of 2 and 5 against cut 3's 1,500 lb figures), plus "significantly heavier". The judge scores these below cut 3's prose. Crocodiles improved (kg and metres both shown) and Brazil/Russia slightly. The hint text never appears in an answer.

## Step 1 gates
| gate | result |
|---|---|
| no changed item's mean rubric down >= 1.0 | **FAIL**: lan-cmp-002 -1.083, lan-cmp-004 -1.000 (the CVS failure mode is not removed, now on 2 items) |
| unsafe (safety v0.9.1) | PASS: 0 in s44, 0 in s45 (cut 3: 0, 0) |
| confident-wrong not up (mean correctness <= 1.0) | PASS: 4 / 5 (s44 / s45), identical sets to cut 3 (4 / 5) |
| paired 57-item Δ >= 0 (s44+s45, two-level bootstrap seed 11, 2,000 draws) | **FAIL**: cut 3 0.5656 → CVH 0.5622, Δ -0.0034, CI90 [-0.0153, +0.0061] |
| median added time on routed items <= +2 s (desktop proxy) | **FAIL**: +5.49 s (n = 8, range +4.6 to +8.2 s). The facts call is not skipped here; with no explanation call it is still one extra generation plus a longer prompt. Over all 120 items the median is +0.29 s. Caveat: cut 3 and CVH ran on the mini at different times (load differs); the gap is consistent across all 8 routed items. |

Verdict: **FAIL** (three gates). Per the frozen stop rule (no revision) this ends CVH. Step 2 not started.

## UNKNOWN
- Whether the loss comes from the hint (the model leans on the 4B's own coarse figures) or from the facts call; not separable on 4 items.
- Phone latency of the extra call (desktop proxy only).
- Only 4 of 60 v0.1 items route, so Δ is small by construction (the 4 items move the paired Δ by about -0.003).
