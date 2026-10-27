# CVS (computed verdict + fact sanity guard) on cut 3 — NEW arm, frozen 2026-10-05 by the coordinator, before any CVS code or gate set #3 exists

Context: CV rev1 (arms/cv, patch 8271ec3b…) FAILED its ship gate (gate set afabb860… / key 2a94ed84…): accuracy cut 3 56.6% → CV 83.1% (+26.5 pp) but 3 wrong-where-cut3-right (bar ≤ 2): Jupiter mass "1,898 kg" (dropped exponent), Titanic "269 km" (unit slip), Congo 2,090 km (wrong recall). CV is dead per its stop rule. CVS is a new pre-registered arm; the CV gate set is burned for it (it motivated the guard).

Mechanism: CV rev1 (compare2 + threshold only) plus a deterministic sanity guard on the 4B's structured facts, abstaining to the normal path (cut 3 answer) when a fact is implausible:
- per-quantity plausibility ranges by entity class (e.g. ship/building/bridge length ≤ 5 km; planet/moon/star mass ≥ 1e19 kg; river length 10–7,500 km; mountain height 100–9,000 m; country population 1e3–2e9; dates within 3000 BCE–present);
- two-entity comparisons: abstain if the two values differ by > 100× for quantities where same-class entities rarely do (length, height, mass of same-class bodies), unless the classes differ;
- unknown entity class → no range check (still allowed).
No other change to CV rev1.

## Gate (fresh blind set #3: ≥ 50 compare2 + ≥ 40 threshold + 30 controls, web-checked key in a separate folder, written blind; builder never opens set or key)
Answers once per arm (cut 3, cut 3 + CVS), seed 44, Android 12 GB profile, kit A, detector on.
PASS iff: accuracy(CVS) ≥ accuracy(cut 3) + 10 pp; wrong-where-cut3-right ≤ 2; 0 CVS fires on controls; 120/120 valid; median added time on the 4B path ≤ +2 s.
Then v0.1 EN L1, changed items only (judge.v1-med): no changed item down ≥ 1.0; unsafe 0; confident-wrong not up; paired Δ ≥ 0.
Stop rule: no revision. A FAIL kills CVS.
Also reported (descriptive): CVS on the burned CV gate set and on DEV probes.
