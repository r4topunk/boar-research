# PRECISION-GATE (2026-10-22, criterion sha a350a88b; 1.7B, 13-pack kit, RS_MERGE=gidf, MAIN 97, seed 42; Haiku 5.5-low, 38 of 300 calls, Opus 0, paid 0, phone 0)
Verdict (frozen rule): **P1 SCORE-GATE NO, P2 SELECT-GATE NO; no LEVER-CANDIDATE.** Control = ARM-G (compose/screen). Details: calibration.md, answers-gate.md, answers-gate.json.
## Built
- Clone kiln-local/rs-GATE = rs-H4 + patches/GATE.patch (sha 70d389f6; answer.ts + adapter): P1 env RS_SCORE_GATE=<tau>, P2 DG_ARM=GATE (SELECT call as gate only: NO_EVIDENCE -> sources = [], pick/unmapped/no sentences -> sources unchanged; skipped when no source was kept). Same hook scope as DECODE-GROUND (after the instant snippet; never health/multipass/deep). Mini job = base clone + H4-MERGE.patch + GATE.patch (tools/run_gate.sh).
- tau = 0.4842 (calibration.md): S = best fused score among chunks kept before the head pass (appended neighbours/dense carry 0/cosines, outside the keep step); 3/32 fact-present below it. Fused scores are quantised (best lexical hit = 0.5): 16/32 fact-present and 22/60 fact-absent sit at exactly 0.5.
- Switch-off identity: 20/20 live items identical to ARM-G (text, kept, reasonCodes); replay 97/97 identical to compose N10 gidf. Gate replay closes 16 of the 17 predicted (the 17th was already source-less).
## Result (MAIN 97; U / dU vs ARM-G on changed items [CI B 2000 seed 11])
| arm | U all 97 | changed | dU changed | dU all 97 | vs K3 control all 97 | CE-unwarned (G 14) | fact-present gated | fact-absent gated | totalMs (G 5594) |
|---|---|---|---|---|---|---|---|---|---|
| P1 | 0.4194 (G 0.4167, ctl 0.4102) | 16 | +0.016 [-0.047, +0.076] | +0.003 [-0.007, +0.012] | +0.009 [-0.013, +0.031] | 14 (12 with the UI weak flag) | 3/32 = 9.4 % | 13/60 (+1 already empty) | 4934 |
| P2 | 0.4176 | 18 | +0.004 [-0.037, +0.049] | +0.001 [-0.007, +0.010] | +0.007 [-0.015, +0.028] | 16 (up; 13 with UI flag) | 3/32 = 9.4 % | 15/60 | 6637 (select 72 calls, 3.4 s mean) |
- 2x2: fact-present items (32) dU P1 -0.0005, P2 +0.003 (the three gated: vit-cry-008 corr 3.0 -> 1.0 and vit-cry-001 2.0 -> 1.0 are real losses); fact-absent (60) P1 +0.005, P2 -0.0001. By set: money P1 +0.017 [-0.011, +0.050], P2 +0.015; cooking P1 0, P2 -0.015; v0.1 P1 -0.001, P2 +0.001.
- Rule: P1 fails dU >= +0.02 (+0.016) and CI low > -0.01 (-0.047); CE-unwarned flat and false closed-book 9.4 % pass. P2 fails the dU clause and CE-unwarned (16 > 14). Neither beats the K3 control by +0.02.
## Prediction vs result
- P1 +0.02..+0.04, money recovers most, false closed 5-10 %: **missed on size** (+0.016 on 16 items = +0.003 over 97); money is the largest set effect (+0.017) and false closed 9.4 % held. Closed-book share fact-absent 53 % predicted and met, but 18 of those 32 were already source-less before the gate; the gate newly moves 13-15.
- P2 similar with fewer false closed-books, +2.6 s: **missed** (3/32 false, same count; +3.4 s per select, +1.0 s mean per answer; NO_EVIDENCE on 18 of 72 calls).
## Reading
- ARM-G almost never answers closed-book (1 of 97 model answers has no source): its no-good-source items still carry head-pass chunks. Both gates turn 16-19 items into true closed-book answers; on those the corr change is a coin flip (P1 on 16: 6 up, 8 down by >= 0.5, 2 flat), so withholding wrong context helps (money-se-002 1.5 -> 3.5, -008 2.0 -> 3.5) about as often as it removes useful context (vit-cry-008, money-se-012 3.0 -> 1.5).
- The ceiling is low: only 16-18 of 97 answers can change, so +0.02 over all 97 would need about +0.11 per changed item; with that n the changed-item CI is +/- 0.06.
## Caveats
- Exploratory, one seed, Haiku judge; 4 P1 and 5 P2 changed answers equal the K3 control's text and take its row, 6 P2 answers equal P1's and reuse its row. The S definition (pre-head-pass) was fixed before generation but chosen after seeing both score distributions (calibration.md). Fact flag = replay stage K (9 live kept lists differ from the replay). The text warning line misses the UI weak-source warning (reported both ways). A tau between 0.4976 and 0.5 would be a cliff (22/32 fact-present closed).
- Not run: both gates together, a tau sweep, a second seed. Nothing committed or pushed; mini jobs' trees removed, no server left running.
