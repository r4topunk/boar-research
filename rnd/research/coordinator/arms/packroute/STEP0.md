# PACKROUTE step 0 — **FAIL at step 0** (2026-10-13 13:04; criterion sha 801e9ac9…; 0 LLM / 0 judge / 0 paid; MacBook; tools/run_step0.sh + step0.py → aggregates/step0.json)

Correction (TK2-REPLAY, 2026-10-13 22:4x): the identities below are replay-vs-replay on the patched tree (wt/packs = dt512 + T-K2 sources patch), not matches to the cut-7 generation traces; the patch changes kept lists on 52/180 (arms/packs/tk2-replay/TK2-REPLAY.md).

Setup: wt/packs (dt512 + T-K2 + packDense2 off) + the PACKROUTE patch (src/rag/packRoute.ts, packs.ts packRouteLog, retrieve.ts packRoute/quota; default off byte-identical: kit-only off/router/quota = kit reference 60/60; single-pack off = SELFTEST-SCORES S 20/20 for all 9 packs). All 9 published packs + the kit installed; modes off (P), router (R), quota 2/6 (Q), off again (P2, warm p50). Reference S = one pack installed.

| gate | rule | result | verdict |
|---|---|---|---|
| G1 routing accuracy | R selects the item's own pack on ≥ 153/180; "none" on ≥ 21/24 kit items whose gold is not in a wave pack | own pack **45/180 (0.25)**, none 58/180; kit "none" **6/24** (simplewiki picked 16/24) | **FAIL** |
| G2 reach (180) | R fact chunk raw6 ≥ 60 and fact article kept ≥ 61 (≥ 90 % of S) and ≥ P | S 67 / 68; **P 42 / 46**; **R 25 / 25**; Q 43 / 51 | **FAIL** (R below P; Q above P, below the bar) |
| G3 kit no-harm + cost | lost-context 0 vs kit-only (RULE 26); p50 R ≤ 1.5 × P | lost-context v0.1: P 1, R 0, Q 1; v0.2: **P 3, R 2, Q 5** (honesty-refusal + crypto items); p50 180: P2 409 ms, R 262 (×0.64), Q 525 (×1.29) | **FAIL** (P itself fails: installing 9 packs removes a kept kit source on 4 dev items) |

Family: SE packs S 24/28 → P 10/14 → R 7/8 → Q 14/18 (chunk raw6 / art kept); topic packs S 43/40 → P 32/32 → R 18/17 → Q 29/33. Confusion (R): outdoors → none 15/20, medlineplus → simplewiki 15/20, health → simplewiki 11/20, factbook → simplewiki 10/20; simplewiki routes to itself 20/20; SE packs accuracy 0.20 (bitcoin 0.10, health/outdoors 0.00).
Kit side (descriptive): v0.1 all-gold kept 12 (kit) → 23 (P) → 21 (R) → 22 (Q): the wave packs (simplewiki) carry v0.1 gold articles; v0.2 resolvable gold kept 4 → 3 / 2 / 3; all-gold 15 → 45 / 44 / 37. Wave packs take 109/139 (P) kept slots on v0.1 and 248/274 on v0.2.

## Reading
1. **Crowding is real and large:** with 9 packs as peers the fact article is kept on 46/180 vs 68/180 with the one relevant pack installed (−32 %); the fact chunk reaches raw6 on 42 vs 67. The oracle router (= S) is the upper bound: +22 article kept, +25 chunk reach.
2. **The deterministic vote router is not a router:** 0.25 accuracy; the lead-cosine / FTS-share / title votes favour the largest general pack (simplewiki) and send long SE-style questions to "none". It loses more than peers (R 25 < P 46).
3. **Quota 2/6 recovers 5 of the 22 lost article-kept items** (51) at ×1.29 cost and 5 lost kit contexts on v0.2 → not adoptable as is.
4. **Product finding (maintainer note):** today's engine with many packs installed harms the kit on 4/170 dev items (a kept kit source disappears) and halves pack reach; the "install everything" setup is the worst of the measured ones.

Verdict per the criterion: FAIL at step 0 (R fails G1/G2/G3; Q fails G2/G3). Per its rule, a learned router (the 4B as a zero-shot classifier over pack descriptions) is a separate criterion → PACKROUTE-2.
Files: runs/{diff-*.jsonl, all9-st180.jsonl, all9-v01.jsonl, step0.log, step0.py.log}, blind/bench-v02/runs-packs/packroute-all9-v02.jsonl (script-only), aggregates/step0.json. Patch in wt/packs (uncommitted; packroute.vs-dt512.patch to be written with PACKROUTE-2).
