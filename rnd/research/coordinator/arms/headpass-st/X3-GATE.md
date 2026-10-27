# HEADPASS-X3 step 0 gate (criterion HEADPASS-X3-criterion.md sha 275fe748...; 0 LLM / 0 judge / 0 paid; MacBook only)

Generated from tools/gate_x3.py (aggregates/gate-x3.json, runs-x3/split-x3.jsonl). **Verdict: x3a and x3b FAIL at step 0 (G1: 111 / 109 < 117). M2 (crowding) PASSES its step-0 gate → M2 generation eligible per stage 1; G3 makes any X3 mode an optional setting only (reranker 21.4 s / 3.9 s per item).** Stage 1 not run.

Tree kiln-local/be-0cfd4a77-cut7-headpass-x3 = X2b tree + `packRerank: "x3a" | "x3b" | "m2"` (src/rag/rerank.ts, packs.packRerankCandidates, retrieve.ts M2 mode, answer.ts append branch); headpass-x3.vs-cut7.patch sha 39b60376… (delta vs X2b: headpass-x3.vs-x2b.code.patch); tsc 0, vitest src/rag + src/routing 871/871 (X2b 855 + 16 new). Reranker bge-reranker-v2-m3-q4km.gguf sha e186a244… verified; llama-server --rerank -ub 2048 -t 4, CPU build; scores injected by the replay from runs-x3/scores.jsonl ({qsha, chunkId, score}, no text). Identity (setting absent / other modes in the X3 tree): off = S 180/180, x1 = X1 180/180, x2b = X2b 180/180, off = off2 180/180.

| Gate | Rule | x3a | x3b |
|---|---|---|---|
| G1 | fact present ≥ X2b 102 + 15 = 117 (power line 127) | **111** FAIL | **109** FAIL |
| G1 | ≥ X2b per family (SE 47 / topic 55) | SE 51, topic 60 | SE 52, topic 57 |
| G2 | v0.1 kit-only / v0.2 kit-only == off | 60/60 / 110/110 (0 fires) | 60/60 / 110/110 |
| G2 | v0.1 + simplewiki lost-context; gold kept ≥ off (10) | 0; 18 (41 fires) | 0; 17 |
| G2 | health-strict appended failing onHealthTopic | 0 (9 + sw checked) | 0 (11 + sw) |
| G3 | prompt tokens p50 ≤ S + 600 (S 500); per item max Δ | 925; +591, 0 > 600 | 964; +597, 0 > 600 |
| G3 | reranker per item (clean pass, 36 items, ≈ 70 % idle CPU) | 87 pairs p50: **21.4 s** p50 / 26.1 s p90 (≈ 250 ms/pair) | same scorer |
| — | engine cost p50 without the reranker (S 151.5 ms) | 190.2 ms | 195.3 ms |

M2 (all 9 packs + kit; fused top-20 reranked pack-agnostically, fires only with a user-pack chunk in the pool): fact article kept **41 → 64** (bar ≥ 57: PASS; our all-9 OFF in this tree is 41, packroute's P 46 on wt/packs); SE 22 → 38, topic 19 → 26; fact chunk kept 22 → 37; empty kept 47 → 41; article lost 1 / gained 24; fires 177/180. Lost kit contexts (v0.1 public with all 9, packroute's lost_context): **0** vs all-9 OFF and 0 vs kit-only (all-9 OFF itself loses 2 vs kit-only); gold kept 10 → 10 (kit-only 8): PASS. Kit-only v0.1 / v0.2: 60/60 / 110/110 identical (never fires); v0.1 + simplewiki: 35 fires, lost-context 0, gold kept 10 → 11. Reported, not gated: on the 180, 9 items go from kept sources (all-9 OFF) to none under M2; on v0.1 all-9, kit chunks displaced by pack chunks on 10/60 items (all kit chunks gone on 2: dng-005, trv-004). M2 reranker: 18–20 pairs, **3.9 s** p50 / 5.7 s p90 per item (clean pass).

Reach and appended sources (x3a | x3b): fact chunk among the reranker candidates 155/180 (= reach; X2b 153); reranker order puts the fact chunk at rank 1 on 78/155, ≤ 2 on 108, ≤ 4 on 138; fires 166 | 166 (rerank 166 | 125); appended 327 | 396 (X1 0 | 204, reranked 327 | 192, of which in the dense top-12 242 | 147, from the top article only 31 | 12, BM25-only 54 | 33; fact chunks 100 | 50). Budget drops: 2 chunks (0 fact) | 137 chunks on 97 items, **26 fact chunks** (17 items end without the fact), 111 non-fact. Health-strict drops of reranked chunks 23 | 24.

Per pack present S / X1 / X2b / x3a / x3b: travel 1/10/11/13/13, ethereum 2/7/9/8/10, bitcoin 1/3/6/6/5, health-se 1/9/11/12/12, outdoors 5/9/10/12/12, firstaid 1/3/7/9/7, medlineplus 10/13/17/15/16, factbook 3/6/15/17/16, simplewiki 11/12/16/19/18.

Split denominators (disjoint, 180). Declared split vs X2b — x3a: newly present under X3 (absent under X2b) **26**, present under X2b (still present) 84, non-fact appended only 56, unchanged (= S prompt) 14; fact lost vs X2b 17 → net +9. x3b: 10 / 98 / 58 / 14; lost vs X2b 3 → net +7. Vs S — x3a: newly present 54, present under X1 already 56, non-fact only 56, unchanged 14; x3b: 37 / 71 / 58 / 14.

D0 of the items still without the fact — x3a (69): fact chunk among the 2 picks but dropped by the health-strict rule **28** (SE 19), candidates without the fact 21, fact in candidates beyond D = 2: 16, no retrieval 4. x3b (71): budget-dropped 17, beyond D 15, health-dropped 14, candidates without fact 21, no retrieval 4.

## Reading (worker, 2026-10-14; facts only, coordinator to interpret)
- The reranker ranks well (fact chunk top-2 on 108/155 candidate sets) but present stays at 111: the health-strict filter removes the fact pick on 28 items (x3a) and X1's neighbours eat the budget in x3b (26 fact chunks dropped). x3a beats X2b by +9 net (26 gained, 17 lost), below the +15 bar.
- Implementation note (not a rescue): the first pass (runs-x3/pass1/, logs/run_x3.log) anchored the candidate union on a raw user-pack passage, so 29 items whose raw list held only kit/seed passages got no candidates (headpass:rerank:nocand), and fetch's 300 s client timeout cancelled 2 scoring requests under CPU contention (forge tests, load 40–140): x3a / x3b present 88 / 88. The criterion defines the union over "the pack", so packRerankCandidates now falls back to the installed user pack(s) (BM25 top-80 + dense, no top article) and the replay posts with no client timeout (tools/run_x3_fix.sh; cached pairs not re-sent). The gate above is the fixed pass; both FAIL either way.
- Timing: the full scoring pass ran under heavy contention (x3 p50 24.1 s, p90 56.3 s; M2 4.4 s); G3 uses tools/run_x3_timing.sh (36-item subset, CPU ≈ 70 % idle, no forge/4B). Either way the reranker is ≈ 20× over the 1.0 s default line: optional setting only.
- v0.2 kit-only replay: script-only, counts only (aggregates/v02-kit-counts.x3.json): 110/110 identical for x3a, x3b, m2, off2; 0 fires; 0 scorer calls. Output blind/bench-v02/runs-packs/headpass-x3-v02-kit.jsonl. EXPOSURES row to be logged by the coordinator.
