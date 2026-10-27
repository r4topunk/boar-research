# VALIDATION-criterion Addendum 5 (2026-10-24, r4to "y" to the recommended judge runs; earlier text unchanged)

Judge runs named (Haiku 5.5-low, protocols and prompts unchanged as frozen):
1. V2 UXMATRIX S vs S+ seed 42: label.mjs, cap 520 (A on every unit, B on borderline, C on A != B).
2. V2 P2 vs S seed 42: label.mjs on night/judge/v2-p2 with labels.jsonl pre-seeded from run 1 (S units with identical keys reuse their labels); cap 260 new invocations. Reported next to S and S+; ADOPT rule not applied to P2.
3. V3 layer 2 seed 42, tag S only (S+ is labelled only if run 1 ADOPTs S+): label_v3.mjs, cap 70.
4. V3 layer 2 with subject carry: label_v3.mjs on night/judge/v3-s-carry, tag S, cap 70.
Total cap 920 calls, expected about 410-500. Opus 0. Verdicts by the frozen rules: V2 S PASS rule, S+ ADOPT rule; V3 reported.
