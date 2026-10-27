# KEEP-K1 (2026-10-21): keep-step replay, 0 LLM. Verdict: CLOSED AT THE REPLAY (no variant moves >= 10 S3 items within any usable token cost)

TL;DR (0 generation, 0 judge calls, 0 paid; stub llama-server + the real LITEPACKS adapter on the MacBook, 21 variant runs x 280 rows)
- **Gate (GOAL K1): judge only if a variant brings the fact chunk into the kept set on >= 10 of the 17 K1 S3 items (RAG-FUNNEL).** None does.
  - Best real candidate **ED4B** (empty-raw dense fallback + 4 dense picks + 1200-token append budget): **7/17**, prompt tokens **+50 %** (MAIN), +49 % (PM).
  - Within the adopt rule's token cap (<= +15 %): best is **E+V1orC 3/17** (-14 % tokens), base+V1orC / V2b / V3 / V4 **2/17**.
  - Only the ceiling probe **D8X** (8 dense picks, 2400-work budget) reaches **10/17**, at **+129 %** prompt tokens: not a candidate.
- **More dense picks alone do nothing:** D3 / D4 / R05 fix 0/17. The 600-token append budget binds first; the fact chunks sit at dense ranks 3-10, not "just outside the top 2".
- **New finding: 17/100 MAIN rows get no append at all.** The lexical list is empty, so the X2b append path is skipped although 12 dense candidates were attached. 3 S3 items are among them (vit-hum-003, vit-sci-001, st-qa-money-se-012; fact at dense rank 0/0/3). Variant E (run the append path on empty raw) changes 14 MAIN rows, +2 S3, +8 % tokens.
- **Value even if reached is small:** ORACLE-REAL gives +0.015 with the fact at slot 1, and FACTPRESENT's real prior is -0.010 per item reached. 7 items x the self-test upper prior (+0.139 x ref) is about +0.01 on MAIN, below the +0.02 bar before any token penalty.
- K1 closes here. Step 2 (frozen criterion + generation + Haiku) was not run, by the task's gate.

## Replay table (MAIN 97 / v0.1 57 / PM 180 = the 180 self-tests, each with its own pack)
s3 = K1 S3 items newly holding the fact in the kept chunk texts (RAG-FUNNEL fact rule, share >= 0.5; 2 S3 items already pass on full chunk text in base and are excluded). fc = an RAG-FUNNEL fact-candidate chunk id newly kept. keyed = MAIN keyed items (92) with the fact in kept text. Tokens = engine approxTokens (ceil(chars/4)) of the dumped prompt, mean per item, % vs base.

| variant (KEEP + RETFLOOR) | s3 /17 | fc | keyed present (gain/lost) | kept set changed MAIN / v0.1 / PM | kept chunks MAIN | PM fact reach /180 | tok MAIN | tok PM |
|---|---|---|---|---|---|---|---|---|
| base | 0 | 0 | 24 | 0 / 0 / 0 | 270 | 97 | 626 (0) | 0 |
| D3 (3 dense picks, cap 5) | 0 | 0 | 24 (0/0) | 27 / 20 / 36 | 297 | 98 | +5.2 % | +3.5 % |
| D4 (4 picks, cap 6) | 0 | 0 | 24 (0/0) | 27 / 20 / 36 | 310 | 98 | +8.2 % | +3.7 % |
| D4B (D4, budget 1200) | 4 | 3 | 28 (4/0) | 61 / 40 / 155 | 411 | 119 | +35.5 % | +48.2 % |
| Q2 (max 2 chunks per article) | 0 | 0 | 24 (0/0) | 11 / 8 / 41 | 270 | 96 | -0.5 % | +0.3 % |
| R05 (rescue: +2 within cos 0.05 of last pick) | 0 | 0 | 24 (0/0) | 27 / 20 / 33 | 308 | 98 | +7.8 % | +3.4 % |
| R05B (R05, budget 1200) | 4 | 3 | 28 (4/0) | 61 / 40 / 151 | 407 | 119 | +34.5 % | +46.2 % |
| E (append path on empty raw) | 2 | 2 | 26 (2/0) | 14 / 2 / 3 | 297 | 99 | +8.1 % | +0.6 % |
| ED4B (E + D4B) | **7** | 6 | 31 (7/0) | 75 / 42 / 158 | 467 | 121 | +50.1 % | +49.3 % |
| D8X (ceiling probe: 8 picks, cap 10, budget 2400, E on) | **10** | 9 | 34 (10/0) | 77 / 44 / 159 | 774 | 130 | +128.6 % | +130.3 % |
| RETFLOOR V1 | 1 | 1 | 24 (1/1) | 48 / 29 / 92 | 179 | 73 | -23.0 % | -16.5 % |
| RETFLOOR V2 | 0 | 0 | 24 (0/0) | 34 / 18 / 10 | 216 | 95 | -14.0 % | -1.8 % |
| RETFLOOR V2b | 2 | 2 | 26 (2/0) | 48 / 28 / 49 | 176 | 97 | -24.4 % | -4.2 % |
| RETFLOOR V3 | 2 | 2 | 26 (2/0) | 34 / 23 / 91 | 235 | 102 | -8.4 % | -7.2 % |
| RETFLOOR V4 | 2 | 2 | 26 (2/0) | 19 / 12 / 64 | 267 | 99 | +0.1 % | +0.4 % |
| RETFLOOR V1orC | 2 | 2 | 26 (2/0) | 43 / 25 / 29 | 202 | 98 | -17.2 % | -1.8 % |
| RETFLOOR V1V4 | 1 | 1 | 24 (1/1) | 50 / 31 / 110 | 179 | 74 | -22.8 % | -16.4 % |
| E + V1orC | 3 | 3 | 27 (3/0) | 50 / 26 / 32 | 213 | 100 | -14.1 % | -1.2 % |
| D4B + V1orC | 4 | 3 | 28 (4/0) | 58 / 39 / 149 | 261 | 117 | -1.5 % | +40.1 % |
| R05B + V1orC | 4 | 3 | 28 (4/0) | 58 / 39 / 147 | 259 | 117 | -1.9 % | +38.9 % |
| D4B + V4 | 4 | 3 | 28 (4/0) | 61 / 40 / 155 | 411 | 119 | +35.6 % | +48.2 % |

Items fixed: ED4B = lan-cmp-004, lan-hlt-002, lan-rsn-005, st-qa-money-se-012, vit-hlt-003, vit-hum-003, vit-sci-001. D8X adds lan-cmp-005, vit-cry-007, vit-hum-005. E+V1orC = lan-cmp-004, lan-rsn-005, vit-sci-001. No variant fixes vit-hum-002, lan-cmp-002, lan-cmp-003 (dense ranks 8-10), the grounding/compress items vit-cry-001, vit-cry-010, vit-hlt-001, vit-hlt-002, or the 2 base-present items.

Where the fact chunk sits (K1 RAG-FUNNEL traces, 0-based dense rank): hum-002 8, hum-005 5, cmp-002 10, cry-007 4, hlt-003 4, cmp-003 9, cmp-005 7, money-012 3 (empty raw), hum-003 0 (empty raw), sci-001 0 (empty raw), cmp-004 1 (budget), rsn-005 0 (budget), cry-010 1 (grounding).

## Reading
- The keep step is budget-bound, not pick-bound: every variant that moves S3 items raises the append budget (600 -> 1200 tokens) or opens the empty-raw path. Under the +15 % token cap the reachable S3 gain is 2-3 items.
- The "10 dense candidates just outside the top 2" premise (RAG-FUNNEL) does not hold at the rank level: 7 of them sit at ranks 4-10, so rescue rules near the cut (R05, within 0.05 of the last pick) catch none.
- Budget growth adds context to most PM items (149-158 of 180 change), so a budget variant is a context-length arm, not a keep-step fix; ORACLE-REAL / CTX history says reading binds and longer contexts do not help the 1.7B.
- E (empty-raw dense fallback) is the one mechanism-level gap found: cheap (+8 % tokens, 14 MAIN rows), and E+V1orC is token-negative (-14 %). It does not pass this gate (3 < 10); it is a candidate for the routing/coverage line (R1/C1) if someone wants a one-screen test, with the RETV1ORC caveat that its fixes were refusals.

## Patch sketch (not adopted; replay-only, env-gated)
- E: in answer.ts the head-pass/dense append block condition `retrievedRaw.length` becomes `retrievedRaw.length || denseCandidatesOf(retrievedRaw)?.candidates.length`, so an empty lexical list still gets the X2b dense appends (same D, cap, budget, health filter).
- D / budget knobs: HEADPASS_DENSE_D, HEADPASS_MAX_APPEND, HEADPASS_BUDGET_TOKENS in src/rag/denseCandidates.ts (no code change needed beyond constants).

## Method and parity
- Tree: clone of the RAG-FUNNEL replay tree (kiln-local litepacks + apply_retfloor.py + apply_funnel.py) + tools/apply_keep.py (env KEEP_VARIANT; absent = byte-identical). Lanes A/B ran answer.ts sha 1328e888… (variants up to R05B), lane C 775020be… (adds E/ED4B/D8X; identical code path for the older variants).
- Requests: arms/retfloor/req (MAIN 100 rows of the K1 requests, PM 9 x 20 = the 180, each with its own pack). LITEDECLINE_OFF=5, detector :8094 (already up, not started or touched), stub server on 18791-18793.
- Parity of base: kept ids equal the RAG-FUNNEL K1 replay on 97/97 MAIN and the RETFLOOR base on 180/180 PM; PM fact reach 97 = RETFLOOR base.
- S3 list = RAG-FUNNEL K1 stage S3 (17); fact rule copied from ragfunnel.py (FACTPRESENT semantics) applied to the full kept chunk texts read from the kit pack files.
- Dev sets only (v0.1 public + self-tests). No blind/, no rnd/veil, no v0.4, no mini, no phone, no Opus, no paid API.

## Files
- tools/apply_keep.py, tools/keep_replay.sh, tools/keep_analyze.py, tools/stub_server.py (copy of the RAG-FUNNEL stub).
- aggregates/keep-replay.json (per variant: counts, item ids, tokens), aggregates/replay-traces.sha256 (210 trace files; traces left in the session scratchpad, about 93 MB).
- Rerun: bash tools/keep_replay.sh <job> <funnel tree> <port> <KEEP/RETFLOOR pairs> (about 5 min per pair on the MacBook; one tree per lane, the tree cache DB locks across lanes), then python3 -I tools/keep_analyze.py aggregates/keep-replay.json <job>/out ...
