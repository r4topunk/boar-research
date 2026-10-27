# RD3 READ-KEEPANS answer screen (2026-10-22 22:0x; criterion READER-criterion.md sha f361f738, not edited)
Fix: compression floor + thread keep for short SE answer chunks after `compressContext` (restoreSeAnswers in src/rag/compress.ts; switch BOAR_READ_KEEPANS=1, cap BOAR_READ_KEEPANS_TOKENS default 250; unset = F1b byte-identical). Patch `arms/retrieve-sweep/patches/RD3-READ-KEEPANS-compression-floor-and-thread-keep-for-SE-answer-chunks.patch` (sha256 be631454ed95af8f915c25c35e6ecd9ee42139659e0e915259ec3842eecb50d6; tree kiln-local/rs-RD3 = rs-H4 + patch; adapter metadata in be/adapter*.ts and boar-eval runner/adapter.ts). 0 Opus, 0 paid, 0 phone, nothing pushed or committed.
## Checks
- (a) unit tests 7/7 pass (src/rag/keepans.test.ts: 881-char cut chunk restored whole within cap, cap and 1000-char limit respected, non-SE chunk untouched, thread insert order, nothing-to-restore). tsc: the tree has no @types/node/vitest installed, so the project-wide tsc shows the same ~1,800 environment errors as rs-H4 (diff = vitest import + `process` lines, no new type errors in compress.ts/answer.ts); compress.ts + test compiled standalone strict with 0 errors.
- (b) switch-off identity: replay (MAIN 97, RD3 tree, switch unset) vs sefix/replays/main.v3-extra.jsonl: kept chunks and bodies 97/97, reasonCodes 97/97. Generation, 20 items (reader/rd3/ident20.json): text, reasonCodes, cited, kept, warned 20/20 identical to the F1b traces.
- (c) switch on, replay: money-016 keeps the "$430K" sentence (68994 920 chars whole, was 590; 65943 750, was 294). money-020: chunk 136998 is restored by the floor and then dropped again by the topic guard (grounding:off-topic-dropped-2): NEGATIVE finding (no guard exemption in this arm). money-018 and cooking-001: the second-fact chunks are restored (96658/96659, 19347/3550) but 96659 and 3550 are dropped again by the guard.
- Prompt cost (replay, kept-source tokens, approxTokens): mean 442.8 -> 474.2 = **+7.1 %** (limit +15 %, so KEEPANS_TOKENS stays 250); +105 tokens on the 29 changed items, max +236 on one item. 60 whole + 9 thread restores in 29 items; 16 items had at least one restored chunk removed again by the topic guard.
## Generation (mini, 1.7B, 13-pack kit f1b dir, gidf, seed 42, switch on)
97/97, 0 empty, 0 loops, 0 errors; 26/26 deterministic items byte-identical to F1b. Answer text differs from F1b on 28 items (kept titles identical on all four targets; only the chunk bodies changed). Haiku 5.5-low judge.v1 N 4 both orders on all 28 = 56 calls (cap 100, none left unjudged; reader/rd3/judge/calls.log).
| all 97 | U | corr | CE | CE unwarned | warned |
|---|---|---|---|---|---|
| K3 control | 0.4102 | 2.536 | 29 | 12 | 46 |
| F1b | 0.4009 | 2.443 | 32 | 18 | 36 |
| RD3 | 0.3993 | 2.423 | 30 | **16** | 37 |
- dU vs F1b on the 28 changed: **-0.005 [-0.044, +0.037]** (corr -0.07); vs F1b over all 97: -0.0015 [-0.014, +0.010]; vs the K3 control over all 97: **-0.011 [-0.036, +0.013]**.
- By source (changed): v0.1 n 3 +0.039 [-0.035, +0.179]; cooking n 11 -0.047 [-0.109, +0.010] (corr 2.36 -> 1.95); money n 14 +0.018 [-0.037, +0.074] (corr 2.04 -> 2.21).
- CE-unwarned 18 -> 16 (not up); new CE 3 (cooking-014, cooking-019, money-009), fixed CE 5. corr up >= 1 on 4 (trv-004, money-011, money-012, money-016), down >= 1 on 6.
- Targets (n 4): corr 2.125 -> 2.25 (**+0.125**, clause needs +0.5): money-016 2.0 -> 3.0 (the answer now rejects the policy citing the opportunity cost, still carries the warning line, no citation), money-018 2.0 -> 2.5, cooking-001 3.5 -> 2.5, money-020 unchanged (1.0; chunk dropped by the guard).
## Verdict: **no** (frozen rule)
dU vs F1b on changed >= +0.02: fail (-0.005, CI low -0.044 < -0.01); CE-unwarned not up: pass (16 vs 18); targets +0.5: fail (+0.125); LEVER-CANDIDATE (vs K3 >= +0.02): fail (-0.011).
## Prediction vs result
Prediction: +0.5 to +1.0 on 1-3 targets, dU +0.01 to +0.03 on changed items. Result: one target moved a full point (money-016), the others +0.5, -1.0, 0; dU -0.005. The presence of the fact sentence is not enough: all 4 targets still end as warned memory answers with no citation, i.e. restoring text does not change the engine's grounding/cite path (class a/b of the autopsy), and the extra whole answers add distractor sentences in cooking (-0.41 corr). Cost +7 % prompt tokens.
Files: reader/RD3.json (rows, texts), reader/rd3/{replay-cmp.json,ident20.json,traces,judge,logs,tools}, reader/replays/main.RD3{on,off}.jsonl.
