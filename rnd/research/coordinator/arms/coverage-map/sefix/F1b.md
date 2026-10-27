# SEFIX F1b: chunk_vecs sidecars for qa-cooking-se / qa-money-se + delivery read (2026-10-22, 0 LLM / 0 judge / 0 Opus / 0 paid / 0 phone)
Criterion SEFIX-criterion.md (sha 07ea2b5e, not edited). Sources were in shared-data/packs/**wave3** on both machines (not wave1); shas = manifests 81990fa9 / 37411234, equal MacBook and mini.
## Build (mini M4, Metal, bge-small q8_0 ec38e8da, script mini/f1b_sidecars.sh = g2_sidecars.sh with two rows; output v3proto/, v2 files untouched)
| pack | chunks | build | v2 bytes | v3 bytes | delta | v3 sha |
|---|---|---|---|---|---|---|
| qa-cooking-se | 98,477 | 483 s | 88,973,312 | 129,368,064 | +40.4 MB | 79ed2699bccb |
| qa-money-se | 143,397 | 752 s | 137,240,576 | 196,059,136 | +58.8 MB | 87e4a4cd2a01 |
Total 1,236 s, +99.2 MB (≈ 388 B/chunk, not the criterion's 94 MB). verify (f1b.verify.json): chunk_vecs = chunks = source chunks, 0 chunks without vec, 0 bad rows, emb sha same, only meta diff = densechunk. scp to MacBook v3proto/, sha256 equal both sides, manifests .sqlite.json written. Mini free 29 GiB (floor 25).
## Replays (MacBook, not the mini: the mini has no boar-eval/replay tooling; kit 13 packs N10, rs-H4 clone, RS_MERGE=gidf, MAIN 97, funnel-K3 traces, compose scorer; run_f1b.sh, score_f1b.py)
| arm | kept92 | v0.1 52 | cm40 | stages S1/S2/S3/K | mean kept | kept tok | wall ms/q (mean) |
|---|---|---|---|---|---|---|---|
| N10 gidf, v2, append-budget (COMPOSE replay) | 32 | 28 | 4 | 8/31/21/32 | 3.73 | 522 | 735 |
| control: v2, packDense2=extra | 32 | 28 | 4 | 7/31/22/32 | 3.29 | 414 | 795 |
| **F1b: v3 sidecars, extra** | **45** | 27 | **18** | 7/16/24/45 | 3.49 | 446 | 839 (rerun 830; kept lists 97/97 identical) |
## Reads
- +13 kept vs N10 gidf and vs the v2+extra control (the gain is the sidecars, not the extra mode): cm40 4 -> 18 (+14: cooking 5, money 9 newly kept), v0.1 -1 (28 -> 27).
- Losses among the 32: 2 (lan-hlt-002, vit-trv-003); both are lost already by the v2+extra control, so they come from the packDense2=extra mode, not from the sidecars. Gained vs N10 gidf: 14 cm + vit-hum-003.
- Junk (mean kept chunks on items with no fact kept): 2.48 vs 3.14 N10 gidf (0.79x), vs 2.72 control; crowding other-pack share 22.6 % vs 25.8 %. Kept tokens -15 % vs N10 gidf. Wall +14 % vs N10 gidf, +5 % vs the extra control (load varies, +-15 %).
- QFORM six-file: not run, n/a for F1b (no engine change; the two SE packs are not in A-union, so the read is 0 by construction).
- DELIVERS (F1b): kept 45 >= 40 yes; losses 2 <= 2 yes (at the limit, caused by the extra mode); junk 0.79x <= 1.15 yes; QFORM n/a -> **DELIVERS**. Answer screen: see ## Answer screen below.
- F3 variant skipped: no F3 patch under arms/retrieve-sweep/patches/ (RS_HEALTH_NOSOURCE_FALLBACK) when the replays ran.
## Prediction vs result
F1b ~ F1 with 2 threads, about +17 cm: result +14 cm / +13 total (below, same direction); junk <= 1.1x: hit (0.79x); +94 MB: +99 MB. Caveat: the 40 cm items were written from the threads in these two packs, so +14 is install value on self-tests, not coverage of unseen questions; v0.1 did not move (-1).
Note: my score_f1b.py first overwrote sefix/kfull.json and cmstage.json (the SEFIX agent's names) at 20:11; it now writes f1b.kfull.json / f1b.cmstage.json; the other agent should regenerate its two files. replays/ gitignored (19 MB); MacBook disk is at 5 GiB free.

## Answer screen (2026-10-22 20:1x-20:3x, Haiku 132 of 300, Opus 0, paid 0, phone 0; full table sefix/answers-f1b.md, data answers-f1b.json)
Arm F1b on the mini: MAIN 97, 13-pack kit with the v3 cooking/money files (shas 79ed2699 / 87e4a4cd, per-run dir compose/packs-f1b of APFS clones), RS_MERGE=gidf (H4 patch), packHeadPass a2 + packDense2 extra, seed 42, -t 4, reasoning off, LITEDECLINE_OFF=5. Controls reused: ARM-G (compose/screen) and the K3 control (pool-K1). Divergence-first: 64 changed vs ARM-G judged (kept AND text differ), rest reuse ARM-G rows.
Sanity: 97/97, 0 empty, 0 loops, 24/24 deterministic items byte-identical to ARM-G; kept identity vs the F1b replay 94/97 = 96.9 % (3 live traces keep one chunk more than the replay).
| all 97 | U | corr | CE | CE unwarned | warned |
|---|---|---|---|---|---|
| K3 control | 0.4102 | 2.536 | 29 | 12 | 46 |
| ARM-G | 0.4167 | 2.582 | 24 | 14 | 40 |
| F1b | 0.4009 | 2.443 | 32 | 18 | 36 |
- dU vs ARM-G on the 64 changed: **-0.026 [-0.051, -0.002]**; vs the K3 control over all 97: **-0.009 [-0.033, +0.013]**. By source (vs ARM-G, changed): v0.1 n 33 -0.061 [-0.098, -0.027]; cooking n 13 -0.001; money n 18 +0.022 [-0.011, +0.061].
- Fact present: the 14 newly delivered cm facts go corr 2.286 (ARM-G, fact absent) -> 2.250 (F1b, fact present), dU +0.001 [-0.05, +0.05]; 9 of the 14 answers still carry the "Not found" warning line (same as ARM-G): the engine's grounding gate does not use the delivered chunk. 2x2 A->P (n 14) dU 0.000.
- CE-unwarned 18 vs 14 (ARM-G) / 12 (control): up.
- **Verdict: NO, not a LEVER-CANDIDATE** (all three clauses fail). Retrieval delivery (+13 kept facts, 0-LLM DELIVERS) does not become answers on the 1.7B; the v0.1 loss cannot be split between packDense2 extra and the sidecars (no live v2+extra arm).
- UNKNOWN: whether a stricter use of the delivered chunk (warning/grounding path) would convert the 14; not tested (engine change, out of scope).
