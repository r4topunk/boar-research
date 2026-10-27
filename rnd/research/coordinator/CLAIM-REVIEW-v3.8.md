# CLAIM-DRAFT v3.8 review (independent Opus reviewer, 2026-10-10; scope: v3.8 delta = header, levers row "Thinking 4B on the fast path", S42, changelog; plus two §6 additions)

**Verdict: ACCEPT WITH EDITS.** 0 blockers, 1 major, 6 minor, 1 nit. No blind/veil material read.

## Checks passed
- Numbers in the v3.8 row match the sources: 256 slice Haiku −0.012 (−0.050…+0.025) (L1-YvsC-slice); 512 full Opus raw 0.439 vs K 0.413, paired +0.026 (−0.013…+0.068) = items-resampled dRatioCI [−0.0128, 0.0684]; floor-adj 0.293 vs 0.261; win 0/51; h2h 17/13/21 (L2-Z-1seed.opus.json); p50 23.6 s, ttft 19.9 s (think-Z-full-s42.json); ×3.7 (THINK4B.md:2, QUEUE.md:863). "Development-style" applies (V-para after 2026-10-06, S34). Changelog line matches the row.

## Findings (all in the levers row, l.125, unless stated)
1. **MAJOR (phone time).** The row gives only the desktop ×3.7. THINK4B.md:31 estimates "+30–45 s per answer" from an assumed 8–12 tok/s A15 decode; the measured A15 decode is 2.0–2.7 tok/s (QUEUE.md:695; claim l.21, S28), so the source estimate is ≈ 4× too low and must not be quoted.
   Add: "On the 8 GB A15, where decode measured 2.0–2.7 tokens/s [S28], 370 extra tokens would add roughly 2–3 min per answer before the first visible token (our arithmetic, not measured; the fast-path p50 there is 49 s)." (370/2.7 = 137 s, 370/2.0 = 185 s.) Coordinator: correct THINK4B.md l.31 in the arm file.
2. **MINOR (why one seed).** "one seed" without the stop reason. Add: "so the frozen rule stopped the arm after seed 42 (seed 43 not run)". Source THINK4B.md:2, QUEUE.md:863.
3. **MINOR (slice overstated).** The Opus slice read +0.091 (+0.010…+0.185) and drove continuation; the full set gave +0.026. Add: "the same slice judged by Opus read +0.091 (+0.010…+0.185) over the instruct 4B and sent the arm to the full set, where the gain shrank". Source L2-ZvsC-slice.opus.json; THINK4B.md:19, :30.
4. **MINOR (time base).** "p50 23.6 s vs 6.3 s": 6.3 s is C (instruct 4B, same llama-server backend), not the claim run K. Replace with "≈ 3.7× the answer time of the instruct 4B on the same desktop backend". Source THINK4B.md:27.
5. **MINOR (CIs, statistic).** Add CIs beside points and name the paired statistic: raw 0.439 (0.401–0.476) vs 0.413 (0.381–0.446), "paired +0.026 (items resampled, …)", floor-adjusted 0.293 (0.244–0.340), paired floor +0.032 (−0.016…+0.088). Source L2-Z-1seed.opus.json (Z/K raw, above_min), paired dFloorCI.
6. **MINOR (256 evidence strength).** The 256 negative is 20 hardest items, Haiku only (Haiku compressed the 512 slice gap +0.029 vs Opus +0.091). Replace "(20-item V-para slice, Haiku triage, …)" with "(20-item V-para slice of the hardest items, Haiku triage only, …)". Source THINK4B.md:17–19, :30.
7. **MINOR (§6 l.190, stale routing conclusion).** The S32 sentence ("a device plan is all-deep … or none") now has V-para hybrid numbers (DEEPROUTE-VPARA) that a reader needs beside it; the v0.1 26 %/58 % figure has no V-para counterpart. Fixed by the S44 sentence and a pointer after [S23] (below).
8. **NIT (premise).** "the engine already asks the fast model to think" needs "but the instruct model produces 0 reasoning tokens on 58 of 58 items" (QUEUE.md:856).

## Added (§6 deep-tier row, l.190; sources S43, S44; changelog v3.8 extended)
- After the S41 sentence (DEEPBO2): best-of-2 oracle raw 0.590 (0.559–0.622), +0.038 (+0.027…+0.051) over the expected single 0.553; S1/S2 order-consistent on 33 %/43 %, oracle agreement 49 %/46 % (chance), both below seed 43 (−0.028, −0.031 raw, CIs excluding 0); device plan = one deep answer, no best-of-2 or verifier pass. Checked vs DEEPBO2.md:2, :15–23, :28; QUEUE.md:855, :866.
- After the S32 sentence (DEEPROUTE-VPARA): R2 → deep + thinking 512, 19/51 (37 %) routed, hybrid raw 0.465/0.467 vs 0.413, paired +0.052 (+0.025…+0.087)/+0.054 (+0.022…+0.095), 43 %/34 % of the gain captured, which is near the 37 % random routing of the same share gives in expectation (reviewer arithmetic); ≈ 45 % of all-deep total time; floor removed ≈ 0.33 marked as estimated. Checked vs DEEPROUTE-VPARA.md:5–8, :15–17.
- Pointer after [S23]: "(on V-para the same rule routes 37 % and captures 34–43 % of the deep + thinking gain; see below [S44])".
- Framing kept: cut 7 is the claim build, deep tier separate, nothing meets the bar, win rate 0 everywhere. Header parenthesis updated.
