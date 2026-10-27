# CLAIM-REVIEW v3.5 (independent reviewer, 2026-10-09; scope: v3.4 → v3.5 diff, commit 38fd601 vs 1858ee5)

**Verdict: ACCEPT WITH EDITS** (0 blocker, 3 major, 7 minor). No file under blind/ or rnd/veil/ was read.

## Verified (no change needed)
- Every new number matches its source: T raw 0.542 (0.513–0.571), floor removed 0.422 (0.385–0.459), above-decline 0.340 (0.298–0.382) = L2-TvsD-2seed.opus.json floorD; paired +0.075 (+0.040…+0.110) / +0.093 (+0.050…+0.137) = L2-TvsD-2seed.paired_gap.json; wins 0/51 ×2 = DEEPTHINK.md l.31; bar gap 0.078, CI-low gap 0.115, anchor gap 0.046 = DEEPTHINK.md l.2, l.32; median 1,034 tokens, hits 36/31 = think-T-s42/s43.json; per-category counts = cat-opus-2seed.json (all 7 rows); 3072 arm +0.010 (−0.014…+0.041), ≈1.3k tokens, 176 s = DEEPTHINK2.md l.2, l.23–24, l.29; run counts 4+2+1 = EXPOSURES.md l.14; S33 QUEUE lines l.818/820/821/823 correct.
- Ladder 4B 0.26 → deep 0.33 → deep + thinking 0.42, win 0 at every rung: supported (CLAIM-DRAFT l.18 0.261; L2-TvsD-2seed.opus.json floorK 0.329 / floorD 0.422; QUEUE l.816, l.821). Wording edit in finding 2.
- "AI-reviewed, not clinically reviewed" intact (l.100, l.103, l.168, l.207). DEEPTHINK-V02 placeholder present at l.188 as an HTML comment, plainly marked "pending", and mirrored in UNKNOWN l.267.

## Findings
1. **major**, l.188 (deep-tier row). The ruling (l.174, EXPOSURES l.89) makes every V-para number after 10-06 development-style, but the row still labels these results "held-out-style", and the thinking passage does not say that the arm was chosen after reading the deep tier's V-para category scores (DEEPTHINK-criterion.md l.3).
   - Current: `**Held-out-style sets (new in v3.4; desktop proxy,`
   - Proposed: `**Bounty-style and v0.2 sets (new in v3.4; development-style evidence under the section 5 ruling; desktop proxy,`
   - Current: `**With thinking (new in v3.5):** the same deep tier`
   - Proposed: `**With thinking (new in v3.5; development-style evidence: the arm was chosen after reading the deep tier's V-para category scores, so this is not a held-out estimate):** the same deep tier`
   - Source: EXPOSURES.md l.14, l.89; DEEPTHINK-criterion.md l.3; QUEUE l.827.
2. **major**, l.72 (§2 ladder pointer). This sentence puts a held-out rung (4B) and two development-style rungs on one line without saying so.
   - Current: `its V-para rungs (floor removed: 4B 0.26 → deep 0.33 → deep + thinking 0.42, win rate 0 at every rung, bar 0.50) are in section 6.`
   - Proposed: `its V-para rungs (floor removed: 4B 0.26 (held-out claim run) → deep 0.33 → deep + thinking 0.42 (both development-style, measured after 2026-10-06, section 5); win rate 0 of 51 at every rung; bar 0.50) are in section 6.`
   - Source: EXPOSURES.md l.89; DEEPVPARA (QUEUE l.816); DEEPTHINK.md l.31.
3. **major**, l.174 (ruling). "No engine change may be validated on it" conflicts with the claim build: cut 7 was adopted on 10-07 partly on a V-para gate (0/58 fires, 58/58 identical replay; l.22, l.135, l.137; EXPOSURES l.61). That gate is an identity check, not a quality validation, and the ruling should say so.
   - Current: `is development-style evidence, no engine change may be validated on it, and the ledger`
   - Proposed: `is development-style evidence and validates no engine change (the cut 7 deterministic replay of 2026-10-07, 0 of 58 facts-tier fires and 58 of 58 identical answers, only carries the cut 6 numbers forward to cut 7; it is not a quality result), and the ledger`
   - Source: EXPOSURES.md l.61; QUEUE l.772 (cited in EXPOSURES l.61); CLAIM-DRAFT l.22.
4. **minor**, l.198 (§7). "Best measured configuration" is a rank where a number belongs.
   - Current: `deep tier + thinking is the best measured configuration;`
   - Proposed: `deep tier + thinking has the highest measured V-para score (floor removed 0.422, development-style, still 0.078 below the bar);`
   - Source: DEEPTHINK.md l.2, l.31.
5. **minor**, l.188. "Adds nothing" is stronger than one Haiku seed whose CI reaches +0.041. The 3072 arm also changed the context to 8192, which the text leaves out.
   - Current: `A 3072-work budget adds nothing (Haiku triage judge, seed 42: +0.010, CI −0.014…+0.041, not promoted;`
   - Source: DEEPTHINK2.md l.2, l.10, l.29.
6. **minor**, l.188. "143 s vs 34 s (×4.2)" is seed 42 only. The same row's v3.4 text gives 33 s for the deep tier.
   - Current: `desktop full-answer p50 ≈ 143 s vs 34 s for the deep tier without thinking (×4.2;`
   - Proposed: `desktop full-answer p50 143 s and 146 s vs 34 s and 32 s for the deep tier without thinking (seeds 42, 43; ×4.2–4.5;`
   - Source: think-T-s42.json totalMsMedian 142925, think-T-s43.json 145983; DEEPTHINK.md l.16–18.
7. **minor**, l.188. The run needed a harness deviation: the adapter's 120 s per-answer timeout was raised to 600 s. The text omits it, and it matters for any device plan.
   - Insert after `budget hit on 36 and 31 of 51 items (seeds 42, 43).`: ` The desktop harness's 120 s per-answer timeout was raised to 600 s for this arm (at 120 s, thinking answers were cut before the first answer token); the app has no per-generation timeout.`
   - Source: DEEPTHINK.md l.11, l.47.
8. **minor**, l.188 (category sentence). The low-correctness categories were picked on the same D runs, so part of the gain may be regression to the mean.
   - Current: `the gain sits mostly where the deep tier's correctness was lowest (small per-category n, descriptive)`
   - Proposed: `the gain sits mostly where the deep tier's correctness was lowest (small per-category n, descriptive; those categories were identified on the same D runs, so part of the gain can be regression to the mean)`
   - Source: DEEPTHINK-criterion.md l.3; cat-opus-2seed.json.
9. **minor**, l.11 (§1). The VENUEGPS-2 result (10-07) sits inside the held-out bullet without the new status label.
   - Current: `the places path returned ≥ 3 OSM-gold venues on 7 of 7 (10 per item), both seeds;`
   - Proposed: `the places path returned ≥ 3 OSM-gold venues on 7 of 7 (10 per item), both seeds (measured 2026-10-07, development-style per section 5);`
   - Source: EXPOSURES.md l.63, l.89.
10. **minor**, S34 (l.244). It cites the EXPOSURES "TL;DR", but TL;DR l.3 still says "dev for the deep tier" and Open questions l.93 still says "A coordinator ruling is needed". The QUEUE ruling entry is l.827, not the one right after l.825.
   - Proposed S34: `rnd/research/coordinator/EXPOSURES.md l.14 (V-para row, status column) and l.89 (Open questions, RULED 2026-10-09); rnd/research/QUEUE.md l.825 (ledger) and l.827 (ruling)`. Outside the draft: update EXPOSURES l.3 and close l.93.
   - Source: EXPOSURES.md l.3, l.14, l.89, l.93; QUEUE l.825–827.
