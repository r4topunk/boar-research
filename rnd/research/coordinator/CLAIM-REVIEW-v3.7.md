# CLAIM-DRAFT v3.7 review (independent Opus reviewer, 2026-10-09; scope: diff 2566b6e → 1e1b4c3 only)

**Verdict: ACCEPT WITH EDITS.** 0 blockers, 1 major, 6 minor, 1 nit. No blind/veil material read.

## Checks passed
- Numbers: every v3.7 figure matches its source. 256: raw 0.514, floor-adj 0.387, win 0/51 ×2, Q−T −0.028 (−0.056…−0.003), Q−H −0.039 (−0.066…−0.015), Q−D +0.047 (+0.012…+0.083), 63 % (= 0.047/0.075), 40 % time, p50 ≈ 55 s (57.5/53.2), budget binds 51/51 (DT256.md:2, :22–24, :29–34; paired_gap-Qvs{T,H,D}-2seed.json). Curve 0.329/0.387/0.436/0.422/3072 no gain (DT256.md:39). v0.2 512: raw 0.608 (0.575–0.641), floor-adj 0.508 (0.467–0.550), win 0/110, −0.005 (−0.020…+0.009), +0.089 (+0.057…+0.122), 62 %, p50 82 vs 133 s (DT512V02.md:2, :13–17; L2-H-1seed.opus.json; paired_gap-Hvs{TV,K}-1seed.json; QUEUE.md:848).
- Statistic consistency: all paired figures in the v3.7 text are two-level gaps, same as the v3.6 512 passage. For H−TV the two statistics coincide; for H−K they differ (finding 2).
- Seed counts stated (2 seeds for 256; "seed 42 only" for v0.2 512; 3072 "Haiku judge, one seed"); "development data" on v0.2; bar reading not met with CI low and win rate 0; 512 compared to 1024 "on the same seed", not to the two-seed 0.514.
- Caveat "AI-reviewed, not clinically reviewed": 8 occurrences before and after; untouched.
- No em-dashes in the new body text (the "—" only in the line 1 version header, which is pre-existing convention).

## Findings
   The two-seed CI vs 1024 ends at −0.003, and the loss comes from one seed (s42 +0.001 (−0.026…+0.027), s43 −0.056 (−0.091…−0.025)). "Measurably" without the seed split overstates it.
   Source: arms/dt256/DT256.md:2, :33.
2. **MINOR (statistic not named), l.189.** Current: "paired −0.005 (−0.020…+0.009) against the 1024 budget on the same seed and +0.089 (+0.057…+0.122) over the 4B claim run"
   For H−K the items-resampled CI is +0.054…+0.126; the sentence must say which one it uses. The unit (raw) is also unlabeled.
   Replace: "paired raw −0.005 (−0.020…+0.009) against the 1024 budget on the same seed and +0.089 (two-level paired gap, +0.057…+0.122) over the 4B claim run"
   Source: arms/dt512v02/DT512V02.md:17; aggregates/paired_gap-HvsK-1seed.json.
3. **MINOR (rounding), l.189.** Current: "V-para floor removed 0.387 (0.348–0.425)"
   The JSON gives ci95 [0.3485, 0.4255], and QUEUE.md:846 reads 0.349–0.426. DT256.md:29 truncates. Use one rounding.
   Replace: "V-para floor removed 0.387 (0.349–0.426)"
   Source: arms/dt256/aggregates/L2-Q-2seed.opus.json (Q.above_min); QUEUE.md:846.
4. **MINOR (ambiguous base), l.189.** Current: "while keeping about 63 % of the gain over no thinking (+0.047, +0.012…+0.083)"
   The 63 % is relative to the 1024 gain (+0.075), not the 512 gain (+0.086, where it would be 55 %).
   Replace: "while keeping about 63 % of the 1024 budget's raw gain over no thinking (+0.047, +0.012…+0.083, vs +0.075)"
   Source: DT256.md:2; QUEUE.md:842 (H−D +0.086).
5. **MINOR (wording vs CI), l.189.** Current: "so the knee is at 512 and 512 stays the recommendation"
   512 (0.436) and 1024 (0.422) overlap within CI (+0.011, −0.010…+0.031), so the order between them is not measured.
   Replace: "so gains stop at 512 (512 and 1024 are within CI of each other: +0.011 raw, −0.010…+0.031) and 512 stays the recommendation"
   Source: DT256.md:39; QUEUE.md:842.
6. **MINOR (missing reason for one seed), l.189.** Current: "On v0.2 (development data, seed 42 only, Opus)"
   Replace: "On v0.2 (development data, seed 42 only because the pre-registered seed-43 trigger (CI vs 1024 excluding 0) did not fire, Opus)"
   Source: DT512V02.md:2, :21.
7. **MINOR (precision), l.277.** Current: "on v0.2, 256 is unmeasured and only 1024 has two seeds."
   The no-thinking deep tier also has two seeds on v0.2.
   Replace: "on v0.2, 256 is unmeasured and among thinking budgets only 1024 has two seeds."
   Source: QUEUE.md:839 (TV two seeds); DEEPVPARA (D two seeds).
8. **NIT (CI stated), l.72.** Current: "(0.51 at 512, one seed)"
   Replace: "(0.51 at 512, 0.467–0.550, one seed)"
   Source: DT512V02.md:13.

## Consistency notes (no edit needed)
- §2 ladder (0.51 at 1024, two seeds; 0.51 at 512, one seed) agrees with the §6 row and with the UNKNOWN bullet.
- The changelog (l.279–285) lists every change. S40/S41 (l.252–253) cite the right files and QUEUE lines (843/845/846, 847/848).
