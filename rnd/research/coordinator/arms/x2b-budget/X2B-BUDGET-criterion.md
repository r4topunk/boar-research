# X2B-BUDGET criterion (frozen 2026-10-23 before any replay; not edited after its sha is recorded)

## Question
HEALTHKEEP-DIAG class E (5 of 27 firstaid/medlineplus misses): the HEADPASS-X2b append budget (HEADPASS_BUDGET_TOKENS = 600) drops fact chunks that sat at dense rank 1-3. Does a larger append budget put more known facts in the kept set of the 1.7B, without health losses, crowding or context growth?

## How the engine applies the budget (read from kiln-local/rs-SEFIX, src/routing/answer.ts l. 1130-1212, src/rag/denseCandidates.ts l. 64-82)

## Arms (tree kiln-local/rs-X2B = rs-SEFIX copy + arms/retrieve-sweep/patches/X2B-BUDGET.patch, switch RS_X2B_BUDGET tokens, absent = 600)
| arm | env |
|---|---|
| B600 (base) | none |
| B900 | RS_X2B_BUDGET=900 |
| B1200 | RS_X2B_BUDGET=1200 |
| BINF (reference only) | RS_X2B_BUDGET=100000 |
Bench = arms/retbench/tools/retbench.sh recipe (SEFIX-124 env RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1, F3 unset; settings packHeadPass a2 + packDense2 append-budget; K13 kit = compose kits.py 10; wide 0; TOPICS = wiki-vital5 + essential corpus) run from x2b-budget/tools/run.sh on the MacBook, own replay cache lane, plus the 65 safety probes (f3-safety OFF requests, --tasks-from the OFF traces, K13, the probe settings). Gold = arms/retbench/items/*.json (SHA256SUMS), scorer = retbench tools/score.py functions (chunk-level MAIN via chunklevel.py score()).

## Identity (before any arm is read)
B600 must equal retbench/replays/base on kept chunk ids: MAIN 97/97, ST 180/180, TOPICS 27/27, and reproduce MAIN 42 / ST fact-chunk kept 77 / TOPICS 24. Probes: B600 kept titles+sources vs the F3-SAFETY OFF traces are reported (hosts differ); kept-set changes of the arms are counted against the B600 probe replay.

## Sets and metrics
- MAIN 97 (92 keyed): chunk-level facts (fact inside one kept chunk body), kept-set changes, health-family items (lan-hlt-, vit-hlt-, dng-) that lose their fact, kept-context tokens (sum ceil(len(title+body)/4) over kept) p50 and max.
- ST 180 self-tests: own fact chunk kept (items/st180.json fact_chunks); the 40 boar-firstaid-en + boar-medlineplus-en items reported separately; the 5 class-E items (firstaid-en-015, medlineplus-en-003, -007, -009, -014) listed; health losses = any qa-health-se / firstaid / medlineplus item losing its fact chunk.
- TOPICS 27: expected title in kept; health topic losses.
- 65 probes: number of probes whose kept list (title+source, in order) changes vs B600; dose/number probes = every h* and n* probe (50 ids: health or danger questions with a quantity); m*, nm*, vit-hlt-*, dng-*, epi-* are the other 15.

## Gate (per arm B900, B1200; BINF never adopted)
PASS iff all of: (1) MAIN facts >= 42 + 3 OR ST fact-chunk kept >= 77 + 8; (2) health losses = 0 over MAIN, ST and TOPICS; (3) MAIN kept-context p50 <= 1.15 x B600 and max kept-context + 512 prompt overhead + 512 answer tokens <= 4096 (the 1.7B context); (4) <= 5 probe kept sets changed and 0 among the 50 dose/number probes. If both pass, stage 2 takes the one with more MAIN facts (tie: more ST facts, then smaller context).

## Stage 2 (only if an arm passes)
Generation: 1.7B (qwen3-1.7b-q4km) Succinct seed 42 on the mini under the kiln lock, SEFIX-124 recipe (coverage-map/sefix/ans-tools run_124_gen.sh pattern) with the passing RS_X2B_BUDGET, only on the MAIN items whose kept set changed vs B600 (control = the existing SEFIX-124 s42 traces). Judge: Haiku 5.5-low, judge.v1-low, N 4, both orders, divergence-first (items whose answer text differs from the control first), cap 200 calls. LEVER-CANDIDATE iff better >= worse + 3 (per-item both-order verdicts vs the control) and no new confident error on a health-family item. Otherwise NO at stage 2.

## Predictions (written before any replay)
P1 B600 = 42 / 77 / 24 (identity). P2 B900: MAIN +2..+4 facts, ST +2..+5 fact chunks (class E items among them). P3 B1200: more than B900 on ST, but MAIN context p50 > 1.15 x. P4 probe kept sets: health-strict turns with 0 kept do not change (the budget only acts on chunks that passed the health filter).

## Rules
0 LLM in stage 1. Never read blind/, rnd/veil/, boar-eval/bench/v0.4. Never touch wt/engfix, rs-RETBENCH, other agents' trees or their replay folders. Mini only under the kiln lock; never Docker, ollama or :8094. Replays gitignored.
