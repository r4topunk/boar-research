# CVH (computed verdict as a HINT to the normal answer path) on cut 3 — NEW arm, frozen 2026-10-05 by the coordinator, before any CVH code exists

Context: CVS (arms/cvs, 7bb693c8…) passed its blind verdict gate (+22.9 pp, 1 loss) but FAILED v0.1 L1: replacing cut 3's cited prose with a terse "verdict + facts" block lowered judged quality where cut 3 was already right (lan-cmp-004 −1.08; Δ −0.005). CVS is dead.

Mechanism: for questions CVS routes (compare2 + threshold) AND whose facts pass CVS's sanity guard, run the CVS facts call, compute the verdict, then run the NORMAL cut 3 answer path with one added instruction carrying the computed verdict and the facts (e.g. "A computed check from your recalled figures says: <verdict>. Facts: … Lead with this verdict if it is consistent with your sources; keep your usual explanation and citations."). If sources in the prompt contradict a fact, the normal path may say so. Abstain → plain cut 3. No other change.

## Step 1 — v0.1 EN L1 (first; decides the CVS failure mode)
s44 + s45, Android 12 GB profile, same config as cut3-confirm; byte identity vs cut 3; judge only changed items with judge.v1-med; reuse cut 3 verdicts.
PASS iff: no changed item's mean rubric down ≥ 1.0; unsafe 0; confident-wrong not up; paired 57-item Δ ≥ 0; median added time on routed items ≤ +2 s (desktop proxy).
## Step 2 — fresh blind verdict gate #4 (only if Step 1 passes)
≥ 50 compare2 + ≥ 40 threshold + 30 controls, web-checked key in a separate folder, blind writer; scored with arms/cv/tools/cv-score.mts.
PASS iff: accuracy(CVH) ≥ accuracy(cut 3) + 10 pp; wrong-where-cut3-right ≤ 2; 0 control fires; valid 120/120.
Stop rule: no revision; any FAIL kills CVH.
