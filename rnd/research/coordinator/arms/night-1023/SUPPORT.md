# SUPPORT: does a JUDGED "kept chunk supports the gold answer" flag separate good from bad answers? (follow-up to B-TABLE)
**Verdict: DOES NOT HOLD** (frozen rule, criterion sha256 `93f342bd532289cd6d2c572d09b11c12eea93f081ea67a67f1b640dec2cc34f8`): MAIN 97, seed 42, support-yes minus support-no U: arm +0.001 [-0.074, +0.070], control +0.023 [-0.057, +0.099] vs required >= +0.2 with CI low > 0 in both arms. The judged flag is as flat as the lexical one.
Flag = Haiku 5.5-low, >= 1 single kept chunk states a central claim of the gold answer (replay chunk texts, A + reversed B on borderline + C tie-break; 133 units, 190 calls of 250; arm = K13 gidf+F1F2F4, control = B0 replay).

| set (arm, s42) | support-yes n, U | yes corr>=3.5 / <3.5 | support-no n, U | no corr>=3.5 / <3.5 | gap U [CI] |
|---|---|---|---|---|---|
| MAIN97 arm | 47, 0.427 | 16, 0.571 / 31, 0.348 | 50, 0.426 | 16, 0.689 / 34, 0.302 | +0.001 [-0.074, +0.070] |
| MAIN97 ctl | 21, 0.428 | 7, 0.581 / 14, 0.348 | 76, 0.405 | 17, 0.676 / 59, 0.326 | +0.023 [-0.057, +0.099] |
| v0.1 57 arm | 27, 0.440 | 9 / 18 | 30, 0.492 | 14 / 16 | -0.052 [-0.150, +0.050] |
| v0.1 57 ctl | 20, 0.425 | 7 / 13 | 37, 0.467 | 15 / 22 | -0.043 [-0.143, +0.057] |
| cm 40 arm | 20, 0.409 | 7 / 13 | 20, 0.324 | 2 / 18 | +0.085 [-0.006, +0.166] |
| cm 40 ctl | 1, 0.500 | 0 / 1 | 39, 0.345 | 2 / 37 | n=1 yes cell, no read |
s43 and pooled replicate (same labels; seeds share kept lists 97/97): MAIN97 arm +0.010 [-0.061, +0.077] / +0.005 [-0.065, +0.071]; ctl +0.038 / +0.030 (CI cross 0). cm 40 arm s43 +0.096 [+0.008, +0.174], pooled +0.090 [+0.009, +0.164] (the only CI above 0, under +0.2, cm questions written from the packs). Band share yes/no (corr>=3.5) MAIN97 arm 0.34/0.32 (s42), 0.23/0.32 (s43).

**Support flag rate:** arm 47/97 (48 %), control 21/97 (22 %); v0.1 57: 27 / 20; cm 40: 20 / 1. **Agreement with the lexical chunk flag (MAIN 92):** arm 35/10/7/40 (sup&lex / sup only / lex only / neither) = 81.5 %, kappa 0.63; control 16/3/5/68 = 91.3 %, kappa 0.75 (v0.1 52 arm 82.7 %, cm 40 arm 80.0 %). Lexical x support cross cells (arm, U s42): both yes 0.440 (n 35), support only 0.366 (10), lexical only 0.346 (7), neither 0.432 (40): "no support by either flag" scores as high as "both", so the flat table is not a flag-quality problem.
**Within-item arm minus control (MAIN 97, s42):** support-yes +0.040 [-0.008, +0.087] (n 47), support-no -0.006 [-0.032, +0.020] (n 50); s43 +0.029 / -0.007; pooled +0.034 [-0.005, +0.072] / -0.007. 28 items go control NO -> arm YES, 2 the other way. The arm adds support (22 % -> 48 %) and gains slightly where it does; CI touches 0 (B-TABLE's lexical split gave +0.044 [+0.009, +0.082]).
Parity (live kept titles = replay): arm 93/97, control 91/97; gap on those subsets -0.001 / +0.008, unchanged.

**Prediction vs result:** support share 30-40 % -> arm 48 % / control 22 % (straddles); gap +0.15...+0.3 -> +0.001 / +0.023 (missed by a wide margin); agreement ~70 % -> 81.5 % arm / 91 % control (higher). Reading: support is not what separates good from bad answers for this 1.7B; the 47 support-yes answers have U 0.427 and 34 % at corr >= 3.5, the same as the 50 support-no answers (0.426, 32 %). The model misses answers even when a chunk states the fact, and gets them right without it (memory, easy items).
Caveats: Haiku labels (strictness untested against a human; 48 of 133 first labels were borderline, 9 needed a tie-break); dev items only; chunk texts from the replay, not the live prompt; observational split (item difficulty confounds); the control support-yes cell is tiny on cm (1); one engine (Qwen3-1.7B).
Files: support-2x2.{json,md}, support/labels.jsonl, support/tools/{prep.py,label.mjs,support_agg.py}, SUPPORT-criterion.{md,sha256}, CALLS.md. Nothing committed or pushed.
