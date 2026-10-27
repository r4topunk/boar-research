# STACK step 0 gate — **FAIL at step 0 (G1 fact-chunk kept 36 < 39)**; G1 article, G2 and G3 pass; no generation, no judge (2026-10-13 16:5x; criterion sha 56ed7ccf…; 0 LLM / 0 judge / 0 paid; MacBook only)

Replay tree wt/groundst (dt512 + T-K2 + PACKROUTE quota + packGround incl. "perpack"; it already carried the quota hunks, no code change needed). All 9 published packs + kit. P = settings absent, X = {packGround: "perpack", packRoute: "quota"}; components quota-only (Q) and perpack-only (G) replayed for attribution. Passes off, stack, off2, stack2, quota, perpack.

| gate | rule | P → X (Q / G) | verdict |
|---|---|---|---|
| G1 fact article kept (180) | ≥ 56 | 46 → **72** (51 / 60) | pass |
| G1 fact chunk kept (180) | ≥ P + 8 = 39 | 31 → **36** (28 / 36) | **FAIL** (−3) |
| G1 by family, chunk/article kept | report | SE 6/14 → 9/32; topic 25/32 → 27/40 | – |
| G2 lost context vs kit-only OFF, v0.1 | X adds none to P's | P 1 → X 0; kit-only X 0 | pass |
| G2 lost context vs kit-only OFF, v0.2 | X adds none to P's | P 3 → X 0; kit-only X 0 | pass |
| G2 empty kept over OFF-retrieving v0.1 / v0.2 | not above P (all 9) / kit OFF (kit only) | all 9: 6 → 2 / 10 → 1; kit only: 11 → 2 / 28 → 2 | pass |
| G2 v0.1 gold kept (39 gold items) | ≥ 12 | kit OFF 12, P 23, X 22, kit-only X 12 | pass |
| G2 v0.2 resolvable gold kept (9) | ≥ 3 | kit OFF 4, P 3, X 3, kit-only X 5 | pass |
| G2 tokens over cap (kit + 180) | 0 | X 0, kit-only X 0, 180 0 | pass |
| G3 retrieval + keep p50 (180) | ≤ 1.3 × P | warm off2 429.6 → stack2 423.1 ms (×0.98); first pass ×0.93 | pass |
| step 0 | G1 ∧ G2 ∧ G3 | | **FAIL** |

Rule (criterion stage 0): FAIL at step 0 → no stage 1a/1b, no 4B generation, no Haiku call. Per the criterion NOTE, the pack stack closes with the component numbers as the product note.

Reading:
1. The article line clears its bar with room (+26: enter 29 / leave 3), but the fact chunk gains only +5 net (enter 11 / leave 6). raw6 barely moves (chunk 42 → 43; article 65 → 78).
2. The two components pull against each other on the chunk. Perpack alone: chunk 31 → 36 (+5/−0), article 46 → 60. Quota alone: chunk 31 → 28 (+3/−6), article 51. In X, the quota's 6 lost chunks are on the topic packs where the item's own pack held > 2 slots (simplewiki 12 → 10, factbook 11 → 10). The keep rule only recovers its own +5 on top.
3. Per pack, chunk/article/empty kept P → X: travel 0/3/9 → 3/10/0, ethereum 2/4/5 → 2/9/0, bitcoin 0/2/3 → 0/3/0, health 1/1/3 → 1/6/2, outdoors 3/4/7 → 3/4/2, firstaid 0/1/4 → 0/2/2, medlineplus 2/4/6 → 7/10/3, factbook 11/14/2 → 10/15/0, simplewiki 12/13/3 → 10/13/0.
4. Crowding under X: own-pack kept slots 130 → 158 (of 368 → 530 kept slots); simplewiki's share of all kept slots 62 % → 41 % (182 of its slots are foreign); wikivoyage 4 % → 10 %. Under perpack alone simplewiki stays at 58 %.
5. Kit side: X removes P's 1 + 3 lost kit contexts (all 9 installed). Kit only, X changes 17/60 v0.1 and 51/110 v0.2 kept lists (empty → filled on 9 / 26). keepCodes on the 180: kept-1 60, kept-2 50, kept-3 22, none 31.
6. The kept lists change on 160/180 items vs P, so a stage-1 precheck would have passed.

Identity: P = PACKROUTE's all-9 OFF replay (raw + kept) 180/180, v0.1 60/60, v0.2 110/110; P = off2 180/180; X = stack2 180/180; kit-only OFF = DENSECHUNK-ST kit OFF 60/60. P's numbers equal PACKROUTE step 0 (article kept 46, chunk raw6 42).
Tests: wt/groundst `vitest run src/rag src/routing` 826 tests, 824 pass, 2 pre-existing deep-tier failures (as GROUND-ST); tsc clean. The cut-7 stack tree (built for stage 1, not run), on a scratch copy with wt/packcond node_modules: 840/840 pass (pristine cut 7: 829/829), tsc 0 errors.
Prepared but not run (FAIL): kiln-local/be-0cfd4a77-cut7-stack (cut 7 + stack.vs-cut7.patch sha 0049d3c3…, quota-only packRoute.ts + perpack packGround + adapter forwards retrieve opts; ARM cut7-stack, node_modules symlinked, 17 MB), tools/{mkreq.py, run_stack.sh, chain.sh}, runs/*.requests.jsonl (180 + v0.1 OFF/ON).
Caveats: replay tree is dt512-based, not cut 7 (cut 7 differs only in answer.ts FACTS hunks); G1 uses chunkId reach as PACKROUTE step 0 (generation traces would use URL reach); v0.2 read by script only (counts + ids).
Files: tools/{replay-stack.ts,.sh, run_step0.sh, gate.py}; runs/{st180-all9, v01-kit, v01-all9}.jsonl, runs/step0.log; blind/bench-v02/runs-packs/stack-v02-{kit,all9}.jsonl; aggregates/gate.json.
