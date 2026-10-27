# RETBENCH SWEEP criterion (frozen 2026-10-23 before any arm replay; base identity replay only)

## Question
Which combination of retrieval knobs puts the most known facts inside one kept chunk (MAIN 92, chunk-level) on the SEFIX-124 engine, without losing a health item and without growing the context?

## Bench (fixed)
tools/retbench.sh <config.json> on kiln-local/rs-RETBENCH = rs-SEFIX + retrieve-sweep/patches/RETBENCH-KNOBS.patch, SEFIX-124 env (RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1), settings packHeadPass a2 + packDense2 append-budget, 13-pack K13 kit (TOPICS: wiki-vital5 + essential corpus, as VITAL-MISSES), wide 0. Gold = items/*.json (SHA256SUMS). Base = all RS_RB_* absent; base must equal the rs-SEFIX references (kept chunk ids) before any arm is read: MAIN 97/97, ST 180/180, TOPICS 27/27, F8 96/96, LS 50/50, and reproduce MAIN 42 / ST own-article kept 100 / F8 survived 1 (TOPICS is recorded as measured).

## Knobs (env, absent = stock)
| knob | env | levels (stock first) |
|---|---|---|
| per-article cap | RS_RB_CAP | 2, 3, 4, 6 |
| within-article pick | RS_RB_PICK | bm25 (pool order), vec (chunk-vector cosine; packs without chunk_vecs fall back to bm25) |
| k | RS_RB_K | engine per task (lookup 3 / other 4 / deep 6), 4, 6, 8 (one k for every task) |
| cosine floor | RS_RB_FLOOR | 0.70, 0.65 (fused relevance gate + format-2 lead keep) |
| FTS pool | RS_RB_POOL | 400, 2000 (format-1 PACK_CANDIDATES; format-2 bm25 pool scaled by the same x5, 80 -> 400) |
| article lead header | RS_RB_LEAD | off, on (ARTCAP cap4lead's header, standalone) |
| compress floor | RS_RB_COMPRESS | 0.5, 0.4 (routing/context.ts relative relevance floor) |
cap 2 + pick bm25 = the stock path (no regroup). Full grid 4x2x4x2x2x2x2 = 512 cells; pruned as below to <= 48 runs.

## Pruning rule (outcome-dependent only through stage A, fixed here)
- Stage A, one factor at a time from base (14 runs): cap 3/4/6 x pick bm25; pick vec at cap 2/3/4/6; k 4/6/8; floor 0.65; pool 2000; lead on; compress 0.4.
- A level is HELPFUL if it passes the constraints below and has MAIN facts >= base + 1, or MAIN facts = base and ST fact-chunk kept >= base + 3. Per knob keep its best helpful level (MAIN facts, then ST fact, then smaller MAIN context p50); cap and pick are one knob (the cap x pick cell).
- Stage B: all combinations of 2 or more of the (at most 5, ranked as above) knobs with a helpful level, each at that level (<= 26 runs).
- Stage C (if runs remain, <= 48 total): around the stage-B winner, swap one knob to its second-best stage-A level (passing constraints), one run per knob.
- ARTCAP overlap: cap 4 + vec = ARTCAP cap4, cap 2 + vec = ARTCAP capfact (same code). If ARTCAP's MAIN/ST replays for those points exist and match on kept ids when compared, they are cited, not rerun (TOPICS/F8/LS still run here).

## Ranking and constraints
Rank = MAIN chunk-level facts /92. Eligible only if (a) health losses = 0: no MAIN health-family item (lan-hlt-, vit-hlt-, dng-) loses its fact, no ST health-pack item (qa-health-se, boar-firstaid-en, boar-medlineplus-en) loses its fact chunk, no TOPICS health topic loses its expected title, all vs base; and (b) MAIN kept-context p50 <= 1.15 x base. Ties: ST fact-chunk kept, then smaller MAIN context p50. Reported, not gating: ST own-article kept, TOPICS, F8 / LS survival, crowding per pack, bytes/q, ms p50.

## Reporting
Top 5 eligible configs with deltas per set; full table of all runs; which knobs move MAIN (>= +2 at stage A or in combination) and which do not. ms recorded while load > 10 is marked not comparable; top 5 re-timed on a quiet machine if possible. One deterministic replay per config: counts are item counts, no CI.

## Predictions
P1 base = 42 / 100 / 1. P2 no single knob gives >= +6 MAIN (ARTCAP P3). P3 cap and pick move ST fact-chunk most (+5..+15), MAIN <= +3. P4 floor 0.65 and pool 2000 move TOPICS (b20) but cost context. P5 k 8 breaks the context constraint. P6 the best config is within +5 of base on MAIN.

## Rules
0 LLM, 0 judge, 0 paid, MacBook only (never the mini), one replay at a time while other agents load the MacBook. Never read blind/, rnd/veil/, boar-eval/bench/v0.4. This file is not edited after its sha is recorded.
