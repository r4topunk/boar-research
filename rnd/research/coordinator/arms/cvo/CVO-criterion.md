# CVO (computed-verdict OVERRIDE only on disagreement) on cut 3 — NEW arm, frozen 2026-10-05 by the coordinator before any CVO code exists

Lesson from CV/CVS/CVH: replacing or hinting the prose loses judged quality where cut 3 already has the right verdict. CVO never touches those answers.
Mechanism: run the normal cut 3 answer first. For questions CVS routes (compare2 + threshold), run the CVS facts call + sanity guard; extract the normal answer's verdict (VG v3 extraction). Only if (a) facts pass the guard, (b) the computed verdict is defined, and (c) it DISAGREES with the normal answer's verdict → rewrite only the verdict sentence (VG-style template) and append one "Facts (model recall):" line. Otherwise the cut 3 answer is returned byte-identical.

## Step 1 — v0.1 EN L1 (s44 + s45, cut3-confirm config; judge changed items only, judge.v1-med)
PASS iff: no changed item down ≥ 1.0; unsafe 0; confident-wrong not up; paired Δ ≥ 0; median added time on routed items ≤ +4 s desktop proxy (routed items only; non-routed must be +0).
## Step 2 — verdict gate on the burned-for-CV-family sets as DESCRIPTIVE + fresh blind gate #4 as the decider
Fresh set ≥ 50 compare2 + ≥ 40 threshold + 30 controls, web-checked key (separate folder).
PASS iff: accuracy(CVO) ≥ accuracy(cut 3) + 8 pp; wrong-where-cut3-right ≤ 2; 0 control changes; 120/120 valid.
Stop rule: no revision; any FAIL kills CVO.
