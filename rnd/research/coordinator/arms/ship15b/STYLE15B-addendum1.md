# STYLE15B addendum 1 (2026-10-21, after the Haiku rows, before any Opus call on style arms): post-hoc Opus diagnostic, no rule

Reason: the task asks both judges for the 1.7B (LENGTH-SLOPE: +0.31 s per doubling under Opus). Opus left after SHIP15B: 26 of 120.
Units: the 11 of the 51 ids where the 1.7B-S text already has an Opus judge.v1 pool row AND the 1.7B-D text differs (every such id, no sampling;
list opus17/D17.ids). 22 Opus calls (judge.v1, both orders, seed 7, N 4) on the 1.7B-D texts. Report: paired Opus S - D on these 11 (mean s, U floor-adj,
CE count) next to Haiku on the same 11. Diagnostic only: the frozen STYLE15B verdict (Haiku, 51) is unchanged by it. Opus total for the task: 94 + 22 = 116 <= 120.
