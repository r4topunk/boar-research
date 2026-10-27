# COMBINED = SEFIX-ALL + RD1 READ-SEQ (2026-10-22, Haiku 196 of 200, Opus 0, paid 0, phone 0; criterion sha 9a9c8550 not edited) - verdict: FAILS the frozen rule
Build: rs-COMBINED = rs-H4 + SEFIX-ALL + RD1 (kiln-local); on the mini base litepacks + H4-MERGE + SEFIX-ALL + RD1 (all apply clean, src tree sum c59fdcf3e3f41b78 identical to the local clone). Patch sha256: H4-MERGE 4cd94755, SEFIX-ALL e3d6c3db, RD1 7281afb8. Switches RS_MERGE=gidf + SEFIX F1..F4 + BOAR_READ_SEQ=1, 13-pack kit packs-k13, seeds 42 and 43, 1.7B, -t 4, stock. Tools in tools/, data answers-combined.{json,md}, replays-read.json.
## Delivery (0 LLM, MacBook replay MAIN 97)
- Switch-off (BOAR_READ_SEQ unset) vs SEFIX-ALL replay: raw, wide12, kept ids, reason codes identical 97/97. RD1 on: chunk-level delivery unchanged (92 keyed: art 55, chunk 47, cm 19, v0.1 28; 0 flips), as expected.
- RD1 rewrites the context of 38 items (20 lose a chunk: question echoes dropped; mean kept 4.40 -> 4.20, kept tokens 574 -> 560, junk on the 45 no-fact items 3.64 -> 3.47 chunks).
## Generation sanity (per seed)
97/97, 0 errors, 0 empty, 0 loops; 19 deterministic items byte-identical to SEFIX-ALL; readseq codes on 38 items; 37 answers differ from SEFIX-ALL (same ids both seeds; 1 readseq item with same text); mean out tokens 36.1/36.7 vs 37.6/38.1.
## Answer screen (Haiku 5.5-low judge.v1 N4 both orders; item bootstrap B 2000 seed 11)
| seed | arm (all 97) | U | corr | CE | CE unwarned |
|---|---|---|---|---|---|
| 42 | K3 control / SEFIX-ALL / COMBINED | 0.4102 / 0.4352 / 0.4339 | 2.54 / 2.70 / 2.66 | 29 / 22 / 20 | 12 / 10 / 12 |
| 43 | K3 control / SEFIX-ALL / COMBINED | 0.4126 / 0.4334 / 0.4337 | 2.58 / 2.67 / 2.65 | 24 / 22 / 21 | 10 / 10 / 10 |
- dU COMBINED vs SEFIX-ALL on the 37 changed: s42 -0.003 [-0.038, +0.033], s43 +0.001 [-0.034, +0.038], pooled -0.001 [-0.029, +0.027] (all 97: -0.0004 [-0.011, +0.011]); dcorr -0.08 [-0.32, +0.14].
- dU vs K3 control, all 97: s42 +0.024 [-0.002, +0.051], s43 +0.021 [-0.002, +0.047], **pooled +0.022 [+0.0005, +0.047]**; SEFIX-ALL alone pooled +0.023 [-0.001, +0.048]: RD1 adds nothing.
- CE-unwarned (sum of two seeds): K3 22, SEFIX-ALL 20, COMBINED 22 (s42 12 vs 10). Warned answers +4 / +5 vs SEFIX-ALL (38 -> 42, 31 -> 36) (RD1 labels, it does not fix); CE new 3+3, fixed 5+4.
- By source, pooled vs K3: v0.1 n57 -0.003 [-0.027, +0.023]; cooking n20 +0.090 [+0.029, +0.153]; money n20 +0.029 [-0.013, +0.072]. RD1 effect on changed items by source (vs SEFIX-ALL): v0.1 n6 -0.104 / -0.061 (s42/s43; CIs exclude 0: lan-rsn-001, lan-hlt-003, trv-004 get worse), cooking n12 +0.036 / -0.027, money n19 +0.004 / +0.039.
- Chunk-level 2x2 (pooled, 92 keyed; K3 replay delivered x COMBINED delivered): K3 A / C A n45: C - K3 -0.007 [-0.028, +0.014]; K3 A / C P n26: **+0.097 [+0.039, +0.152]** (C - SEFIX-ALL +0.010 [-0.007, +0.029]); K3 P / C P n21: +0.010 [-0.031, +0.055] (RD1-fired 4 of them: C - SEFIX-ALL -0.087 [-0.159, -0.008]). The gain sits entirely where SEFIX-ALL delivers the fact; RD1 is +0.02 [-0.02, +0.06] on its 13 fired items there and 0 elsewhere.
## Frozen rule: PASS needs pooled dU vs K3 >= +0.03 with CI low > 0 (+0.022: no; CI low +0.0005: yes), dU vs SEFIX-ALL >= 0 (-0.001: no), CE-unwarned <= SEFIX-ALL (22 vs 20: no) -> **COMBINED FAILS; no Opus read warranted** (Opus 0). Prediction +0.03..+0.05 vs K3: missed (+0.022); CE-unwarned 10 -> 8..10: missed (12 and 10 per seed); CV5 neutral: not tested. RD1 does not stack on SEFIX-ALL; the reading is that the 1.7B stays the limit once the fact chunk is in the context (RD1 earlier: +0.022 on its changed items, CI crossing).
## Caveats
Dev items, one model, Haiku judge (compresses gaps); 8 s43 K3 control rows are replicate proxies (delta 0 imputed, bias toward 0 on at most 8 items); the pooled CI is over items with two seeds averaged per item; SEFIX-ALL rows of s43 reuse the replicate's judgments plus 12 own fills.
