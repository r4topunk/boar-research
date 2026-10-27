# ORACLE-ST — retrieval ceiling on the 180 pack-matched self-tests: the known fact chunk injected into the 4B's context (2026-10-13 23:10; criterion ORACLE-ST-criterion.md sha 4c4651b1…; opus/high runner, text saved by the coordinator; a parallel session)

**Verdict (Opus rows): RETRIEVAL-HEADROOM.** ADD − S **+0.095 (+0.070…+0.122)** raw ≥ +0.08 with CI low > +0.03 → per the criterion, **H8-ST (build-time document expansion / contextual chunk headers) becomes rank 1**, with a PACKDENSE-style step-0 reach gate on the 180. ONLY − S **+0.115 (+0.088…+0.142)**: once the fact is present, the rest of the kept context is worth nothing or slightly negative. The declared split behaves as predicted: the gain sits on the 137 items whose S run did not keep the fact chunk (+0.112) vs +0.043 on the 43 that did; on the 27 items where the oracle chunk was already kept, ADD − S = −0.007. The ADD gain is a lower bound (125 items have further fact chunks; only the first was injected, as frozen). Dev numbers (agent-written gold from pack text). 0 paid API; 720 Opus + 720 Haiku judge calls, 0 failures, 0 429 (the "429" strings in the logs are list prices).

## Cells (raw ratio; paired per-item bootstrap B 2000 seed 11; S = cut 7 + the item's pack, existing traces)
| split | ADD − S Opus | ADD − S Haiku | ONLY − S Opus | ONLY − S Haiku |
|---|---|---|---|---|
| pooled 180 | **+0.095 (+0.070…+0.122)** | +0.090 (+0.066…+0.114) | **+0.115 (+0.088…+0.142)** | +0.096 (+0.072…+0.120) |
| SE (100) | +0.112 (+0.074…+0.150) | +0.096 | +0.126 | +0.105 |
| topic (80) | +0.075 (+0.043…+0.109) | +0.083 | +0.102 | +0.085 |
| S kept the fact chunk (43) | +0.043 (+0.011…+0.079) | +0.045 | +0.071 | +0.051 |
| S did not keep it (137) | +0.112 (+0.081…+0.143) | +0.105 | +0.129 | +0.110 |
| oracle chunk already kept (27) | −0.007 | −0.000 | +0.039 | +0.036 |

Levels: S 0.500 (0.475–0.527) Opus / 0.493 Haiku; ADD 0.596 (0.569–0.621) / 0.583; ONLY 0.616 (0.590–0.642) / 0.588. above_min: ADD +0.119 (+0.088…+0.153), ONLY +0.144 (+0.110…+0.178) Opus. Items better/worse: ADD 96/38, ONLY 121/36 (Opus). Per pack ADD Opus: travel +0.166, ethereum +0.080 (CI crosses 0), bitcoin +0.155, health +0.081, outdoors +0.076, firstaid +0.117, medlineplus +0.071, factbook +0.084, simplewiki +0.028 (CI crosses 0); ONLY: +0.177, +0.074, +0.175, +0.101, +0.106, +0.125, +0.068, +0.152, +0.062 (Haiku per pack in aggregates/oracle-st.json).

Aggregation stdout (aggregates/oracle-st.stdout.txt): `oracleadd-opus: n 180 cell raw 0.596 [0.569, 0.621] vs S 0.5 [0.475, 0.527] pooled d_raw 0.095 [0.07, 0.122] d_above_min 0.119 [0.088, 0.153] better/worse 96/38` · `oracleadd-haiku: 0.583 vs 0.493, d_raw 0.09 [0.066, 0.114]` · `oracleonly-opus: 0.616 vs 0.5, d_raw 0.115 [0.088, 0.142], 121/36` · `oracleonly-haiku: 0.588 vs 0.493, d_raw 0.096 [0.072, 0.12]`.

## Stage 0 (0 calls) — PASS
Oracle coverage 180/180 (first `in_pack_facts` entry with a `chunk_index`, chunks ordered by start as in d0_st2.py; the fact quote is inside the chosen chunk on 180/180). Setting OFF vs the S trace on bitcoin-001, simplewiki-002, travel-003: answer text, kept and raw lists, reasonCodes, promptTokens, outputTokens identical 3/3 (S traces carry no prompt text). Setting ON: the ADD prompt = OFF prompt + exactly one `[n] title\nbody` block whose body (after the engine's `section: ` prefix) is byte-equal to the pack chunk read from sqlite (zstd block, UTF-16 slice, trim); checksums match 3/3. Engine change: setting `BOAR_ORACLE_FILE` (default off, byte-identical off), patch oracle.vs-cut7.patch sha dbecafcd…, copy tree kiln-local/be-0cfd4a77-cut7-oracle (ARM cut7-oracle; adapter unchanged 6298e5d3).

## Generation (MacBook, one llama-server; swap pressure from an unrelated 16 GB process made it 2–4× slower than S)
| | ADD | ONLY |
|---|---|---|
| items / errors | 180 / 0 | 180 / 0 |
| p50 s/item (S 8.3) | 13.1 | 10.7 |
| kept total, mean (S 273, 1.52) | 422, 2.34 | 338, 1.88 |
| prompt tokens p50 (S 454) | 622 | 596 |
| fact chunk handling | appended 152, already kept 27 | 163 got [lead, fact], 16 fact only (fact chunk = lead) |
| fact chunk in the final LLM prompt | 132/152 items with an LLM call | 152/152 |
The 26 appended items with no LLM call are health-extractive or instant answers (chunk reached the sources, no model read it); factbook-018 answered from the facts table before retrieval in both cells.

## Reading for the programme
- **The reader is not the wall on pack-matched items: retrieval reach is.** The 4B gains +0.095 from one chunk — 3× the single-pack lift (+0.032 Haiku / +0.042 Opus), ≈ 2× the deep tier's pooled +0.054 over the 4B, and ≈ 5× the biggest measured retrieval lever (ST2 +0.017). Fact chunk kept today: 43/180 (keep step) / 55/180 in raw top 6; the oracle puts it at 180/180.
- READERSWEEP's READER-ORACLE-A condition ("only if ADD − S ≤ +0.03") is NOT met → reader swaps are not the next experiment. PROMPT-READ stays low priority. SFT4B (H10) targets a reader bucket worth ≤ +0.04; the retrieval bucket is worth ≤ +0.095.
- Next (criterion first): **H8-ST step 0** — build-time expansion of format-2 packs so the fact chunk reaches raw top-8 on ≥ 90/180 (BACKLOG gate; today 55–67 depending on tree): (a) contextual chunk headers (title + section path in the indexed text; 0 LLM); (b) doc2query synthetic questions per chunk (≈ 14 h of 4B generation per 55k chunks on the mini). The keep step (R47: chunk kept 43 → 54 under the best rule) is the second bottleneck: ONLY shows that even displacing the kit's context is fine once the fact is present.
- Caveats: dev gold written from the pack text (favours the pack); one seed (deterministic generation); the oracle knows the answer's location — it bounds, it does not propose.

## Files
tools/{build_oracle.py, oracle-add.json, oracle-only.json, oracle-facts.json, mkreq.py, run_oracle.sh, gen_chain.sh, judge_chain.sh, stage0_check.py, oracle_agg.py}; runs/st-<pack>-cut7-oracle{add,only}-s42.{requests,traces,prompts,ids,judgments,judgments.opus}.jsonl + .shards/, runs/stage0/; aggregates/oracle-st.json, oracle-st.stdout.txt; logs/. Public items only → no EXPOSURES row.
