# RETV1ORC result (2026-10-20 22:47)

Criterion RETV1ORC-criterion.md sha256 0f2a70169d69b2164a82649120e1ce825ce685841663c3c1a3f66f31fc935b32 (frozen + committed 1ce2d6b8 before generation; GATE v2 sha 34ada53f).
Stage 1 (mini, slot lock, 41 rows, 0 error rows, dead changed 0; Haiku 5.5-low N 4 both orders, 26 calls):

    screen2 K1: problems 21 | fixed_u 2 (by refusal 2) | new CEu 0 | net 2 (bar 9) | false refusals 1/20 (max 4) | sentinels worse 0 (report only) | U_cov -0.0262 [-0.0643, 0.0035] (min -0.071) | changed 13 | dead changed 0 -> NO-GO

- CE-unwarned (41 screen items) control 21 -> arm 19; default-mode refused (R) 0 -> 3 (both fixes are refusals, i.e. warned memory answers once the off-topic appends are gone; 1 sentinel newly refused).
- Coverage (>= 1 retrieval.kept) 28 -> 27 of 41; V1orC fired (pending appends present) on 28 items, 28 appends removed, context changed on 13, answer text changed on 13.
- Prompt tokens (live mean) 646 -> 583 (-63, -10 %).
- agg_run U 0.4306 -> 0.4325 (+0.002, CI -0.008..+0.014), CE count 21 -> 21.
- Reading: net 2 is below both K1 nulls (6, 7), but the nulls perturb every item while V1orC changes only 13/41 (the control is deterministic), so the null bar is conservative here; still, 2 fixes of 21 is no detectable lever. Stage 2 not run (NO-GO).
Files: retv1orc.patch, report.py, traces/, judgments/, aggregates/ (incl. .gate2.txt/.json), runs/.
