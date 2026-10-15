# HEADPASS-ST — append the top retrieved pack article's neighbour chunks outside the keep step (criterion HEADPASS-ST-criterion.md sha e8ee3eed…)

## Step 0 (2026-10-14 00:5x; 0 LLM / 0 judge / 0 paid; replays on the 180 + v0.1)
**X1 (`packHeadPass "a2"`) misses G1 by a hair and passes G2/G3.** Fact chunk present in the final context **35 → 72 (+37)** (clears ≥ OFF+15; misses the power line ≥ +40 by 3); reach raw ∪ appended 55 → 79 (bar 90, FAIL). G2: v0.1 kit-only byte-identical 60/60 (never fires); v0.1 + simplewiki: lost-context 0, fires on 24/60, +282 prompt tokens p50 on fired items, gold-kept 10 → 10, 6 items go from empty to non-empty; health-strict: 0/9 appended chunks fail an independent onHealthTopic recheck (15 candidates filtered). G3: retrieval + keep p50 0.97× (keep step 0.6 → 1.0 ms); prompt tokens p50 500 → 751 (+251 ≤ +450). Default-off identity: 180/180, 60/60, 60/60 vs the tk2off reference (raw, kept, promptSha, task, query, k); OFF2 repeat identical. v0.2 identity replay skipped tonight (blind).

| Group | Reach OFF → X1 | Present OFF → X1 | Fires on | Prompt tok p50 |
|---|---|---|---|---|
| SE (100) | 24 → 43 | 10 → 38 | 85 | 502 → 758 |
| Topic (80) | 31 → 36 | 25 → 34 | 42 | 495 → 731 |
Per pack present: travel 1 → 10, ethereum 2 → 7, bitcoin 1 → 3, health-se 1 → 9, outdoors 5 → 9, firstaid 1 → 3, medlineplus 10 → 13, factbook 3 → 6, simplewiki 11 → 12. A2 fired on 127/180 items, 205 chunks appended (78 items got 2, 49 got 1, 53 none); 46 items had a fact chunk among the appended. Declared-split denominators: fact newly present 37 (SE 28 / topic 9); appended only non-fact chunks 81 (17 already had the fact); second fact chunk appended 9; prompt unchanged 53. The 108 still without the fact: 64 appended the wrong neighbours, 29 have no user-pack passage in raw at all (A2 cannot anchor), 8 health-filtered, 7 head chunks already kept.

Patch `headpass.vs-cut7.patch` sha de143ab1…: settings.ts:44,489,500 (`packHeadPass?: "off"|"a2"`); wikiPack.ts:652 `headChunksOf(chunkId, 1, 2)`; packs.ts:219 `packHeadPass(raw)` (first raw passage from a non-kit format-2 pack); answer.ts:1016 records retrievedRaw, :1060 appends after grounding + health block, never on multipass, skips already-kept, onHealthTopic on health-strict, no displacement / onSubject / compression; reason codes `headpass:add:*`. Tree runner-local/be-0cfd4a77-cut7-headpass. Tools tools/{replay-hp.ts, replay-hp.sh, run_hp.sh, compare_hp.py}; runs/*.{ref,hp}.jsonl, runs/split.jsonl; aggregates/compare.json.

**Decision (criterion's variant rule):** X2 (dense extra slots) cannot run tonight — the int8 caches are gone from the MacBook and a re-embed is out of scope — so X1 proceeds as the criterion's **component estimate** (stage 1 generation on the 180 + Haiku L1 only, no Opus; verdict capped at "not decidable at MDE 0.03"). Why spend it: +37 newly-present items is the first direct test of the 0.11–0.17-per-item conversion fitted on ORACLE-ST/ST2 (projected +0.023…+0.035 pooled, concentrated on the 37); the declared split (newly present / non-fact neighbours only / unchanged) measures the distractor cost of the 81 items that received only non-fact chunks — the number every later retrieval lever (dense, doc2query) depends on. Cost ≈ 25 min of 4B generation on the MacBook + 360 Haiku.

## Stage 1–2 (2026-10-14 02:5x; X1 component estimate; Haiku 5.5-low N = 4, 588 calls; 300 generations on the MacBook; 0 Opus / 0 paid)
**Δ vs S pooled 180: +0.023 (+0.009…+0.038) raw** (X1 0.515 vs S 0.493; better/worse 74/54) — by rule "not decidable at MDE 0.03" (no Opus by design; Haiku compresses). **The declared split confirms the mechanism:** fact chunk newly present (37) **+0.092 (+0.051…+0.132)**, 22/6; non-fact neighbours only (81) +0.007 (−0.012…+0.029) → distractor cost ≈ 0; unchanged (53) +0.001; generation-side "fact appended, absent under S" (32) +0.111 (+0.070…+0.154). SE +0.029 (+0.009…+0.048), topic +0.015 (−0.005…+0.038). Per pack: travel +0.060 (+0.018…+0.102), factbook +0.048 (+0.004…+0.103), health-se +0.038, ethereum +0.032, firstaid +0.031 (+0.003…+0.068), medlineplus +0.009, outdoors +0.007, bitcoin +0.006, **simplewiki −0.028 (−0.070…+0.015)** (13 non-fact-only items, 8 already had the fact; unexplained, n 20). No-harm v0.1 + simplewiki ON − OFF +0.004 (−0.018…+0.025), 19/17; on the 24 fired items +0.016; adoption clause (CI high ≥ −0.03) holds. Precheck 120/180 prompts changed (bar 20 %); step-0 replay vs generation agree on 163/180 (real gate + mmBERT detector vs the replay's always-search gate). RULE 27 field: 57/60 kept-unchanged items same answer (3 factbook differ at equal prompt length); v0.1+sw 33/33.

**Reading:** the per-item conversion holds at the Haiku scale — ≈ +0.09–0.11 raw per item that newly gets its fact chunk, as projected from ORACLE-ST/ST2 — and appending wrong neighbours costs nothing measurable. **Reach is the limiter, not the mechanism:** X1 reaches 37 new items; the dense variant X2 (projected 43 → 117 present) needs the bge-small sidecars (re-embed on the mini after SFT4B, or ≈ US$ 1 of GPU). An Opus pass on the same traces (360 calls) would turn the component estimate into a decision; left to the loop's judgement (Haiku +0.023 is a near-miss of the +0.03 threshold under the L1 near-miss rule → Opus N = 4 is the protocol's own next step).

Files: tools/{mkreq.py, run_hp_gen.sh, busy.sh, gen_chain.sh, judge_chain.sh, precheck_hp.py, agg_hp.py}; gen/<runId>.{requests,traces,prompts,judgments}.jsonl (9 ON runs + v01sw OFF/ON); aggregates/{precheck.json, agg.json, agg.stdout.txt, same_answer.*}; headpass-dump.eval.patch (env-gated prompt dump, sha 475ddbc9…, identity re-checked 600/600).

## Opus L2 (2026-10-14)

Judge: Opus judge.v1 (claude-opus-5-5), N = 4 shards, both orders, 9 ON sets x 40 = **360 calls, 360/360 ok, 0 failures** (exit 3/4: 0, exit 7: 0, rate-limit lines 0; fail-closed `_lib/check_judgments.py` ok on all 9; no --allow-splice). 0 Haiku, 0 paid. Control = existing S Opus rows (ST2 L2, not re-judged). Estimator = l2_agg.py unchanged (per-item bootstrap of the ratio-of-sums difference, B 2000, seed 11, paired on queryId). Tools: `tools/l2_chain.sh`, `tools/l2_agg_headpass.py`; logs `logs/l2.log` (+ lane1/lane2); outputs `gen/st-<pack>-cut7-headpass-s42.judgments.opus.jsonl`, `aggregates/l2-opus.json`, `aggregates/l2-opus.stdout.txt`. Split = `runs/split.jsonl` (step-0 replay, the same ids as the Haiku stage).

| Group | n | ON raw | S raw | d_raw (95 % CI) | d_above_min (95 % CI) | better/worse |
|---|---|---|---|---|---|---|
| **pooled** | 180 | 0.533 | 0.500 | **+0.033 (+0.016…+0.050)** | +0.041 (+0.020…+0.063) | 65/45 |
| SE | 100 | 0.534 | 0.482 | +0.052 (+0.027…+0.079) | +0.065 (+0.034…+0.099) | 41/23 |
| topic | 80 | 0.531 | 0.523 | +0.008 (−0.012…+0.029) | +0.010 (−0.015…+0.037) | 24/22 |
| split: fact chunk newly present | 37 | 0.596 | 0.477 | **+0.119 (+0.069…+0.172)** | +0.150 (+0.087…+0.216) | 21/7 |
| split: non-fact chunks only | 81 | 0.511 | 0.499 | +0.012 (−0.012…+0.039) | +0.015 (−0.016…+0.048) | 30/26 |
| split: prompt unchanged | 53 | 0.520 | 0.517 | +0.003 (−0.007…+0.014) | +0.004 (−0.010…+0.018) | 10/10 |
| split: other changed (9) | 9 | 0.547 | 0.509 | +0.037 (−0.004…+0.082) | +0.048 (−0.003…+0.102) | 4/2 |
| split: changed, all | 127 | 0.538 | 0.493 | +0.045 (+0.022…+0.070) | +0.056 (+0.028…+0.087) | 55/35 |

Per pack (d_raw, CI, better/worse): travel +0.090 (+0.032…+0.154) 11/5; ethereum +0.069 (+0.013…+0.127) 11/4; bitcoin +0.021 (−0.045…+0.101) 5/6; health-se +0.044 (−0.004…+0.102) 5/5; outdoors +0.037 (+0.007…+0.072) 9/3; firstaid +0.003 (−0.011…+0.021) 6/5; medlineplus +0.027 (−0.002…+0.058) 5/3; factbook +0.025 (−0.012…+0.074) 7/4; simplewiki −0.024 (−0.081…+0.030) 6/10.

Win/tie/loss vs reference: 0/0/180 for both ON and S (every item lost to the reference in both arms, so win-rate carries no information here). Positional consistency etc. in `l2-opus.json`.

Haiku vs Opus agreement (same 180 items): same winner ON 179/180, S 180/180 (uninformative: the winner is the reference almost everywhere); per-item Δ (ON−S) correlation Haiku vs Opus r = 0.747; pooled Haiku d_raw +0.023 vs Opus +0.033 (Opus larger, split newly-present +0.092 Haiku vs +0.119 Opus).

## Verdict (coordinator, 2026-10-14 02:4x)
**By the frozen rule: "not decidable at MDE 0.03" (capped).** Step 0 missed the power line (fact present +37 vs the required ≥ +40 over OFF) and the reach bar (79 < 90), so the criterion restricts X1 to a Haiku component estimate with a capped verdict. **Deviation disclosed:** the coordinator ran the Opus L2 anyway (360 calls, week-2 budget) on the L1 near-miss; that measurement — pooled **+0.033 (+0.016…+0.050)** raw, above_min +0.041 (+0.020…+0.063), SE +0.052 (+0.027…+0.079), topic +0.008 (−0.012…+0.029), fact newly present (37) **+0.119 (+0.069…+0.172)**, non-fact neighbours only (81) +0.012 (−0.012…+0.039), unchanged prompt (53) +0.003 — would read LEVER under the standard rule (CI low > 0, Δ ≥ +0.03) and is reported as such, labelled "measured beyond the frozen plan". It does not change the frozen label; it sets the prior for the next arm.
Reading: the mechanism converts (+0.119 where it puts the fact chunk in the context, ≈ 0 elsewhere, no harm on the kit, 0 LLM, append-only); what limits it is reach (72/180 present). Next: **HEADPASS X2** (the same append path fed by the ST2 dense extra slots; projected present 117/180) after the bge-small sidecars are re-embedded on the mini (TEACHER-PROBE first), under a criterion whose power line is set from this run (present ≥ 72 + 30). Product note: X1 is a candidate default for the pack line (0 LLM, +282 prompt tokens p50 on fired items, kit byte-identical when no pack fires), subject to the engine-scope rule (same tree for reach and quality) and the maintainer PR plan. Simplewiki −0.024 (−0.081…+0.030) is the one pack where appended neighbours may hurt (n 20).

## X2b stages 1–3 (2026-10-14)
Criterion HEADPASS-X2-criterion.md (sha 1b70f6f3…) + addendum 1 (a66a3b79…). Numbers only; the verdict is the coordinator's.
**Generation (MacBook, 4B cut 7, one job at a time):** tree runner-local/be-0cfd4a77-cut7-headpass-x2 (headpass-x2b.vs-cut7.patch 2f0b0ea5…); settings packHeadPass "a2" + packDense2 "append-budget"; item pack = its sidecar copy (shared-data/packs/v3proto, sha-pinned in the requests); runIds st-<pack>-cut7-headpassx2b-s42 + v01-sw-cut7-x2b-{off,on}-s42 (gen-x2b/; tools/mkreq_x2b.py, run_x2b_gen.sh, gen_chain_x2b.sh). 300 rows, 0 errors, wall 62 min. **Adapter fix:** adapter 6298e5d3 dropped retrieve() options, so packDense2 never reached retrieval (first smoke: headpass:dense:nosidecar 20/20, voided in gen-x2b/void-noopts/). Replaced with the cut7-stack adapter a77838f1, which forwards the options (adapter-forward-opts.patch; no options → the call is unchanged).
**Traces (180):** fired 155 (X1 neighbours on 120 items / 187 chunks; dense on 125 / 203); budget drops on 74 items (103 chunks). Prompt tokens p50: S 453.5, X1 665.5, X2b 872 (152 LLM items). Total time p50: 8.3 / 10.3 / 13.4 s. Retrieval p50: 332 / 360 / 392 ms. v0.1 + simplewiki prompt tokens p50: OFF 481.5, ON 878.5; 41/60 fired.
**Reach from traces:** fact present 97/180 vs the replay's 102; per-item agreement 167/180; appended list = replay 157/180. All 23 diverging items have identical raw retrieval. They differ only on health-strict classification (generation uses the mmbert detector, the replay the lexical one): 17 health-strict in generation only (appends dropped), 6 the reverse.
**Precheck:** changed vs S 155/180 = 0.861 (bar 0.20). same_answer vs S: all 28/180, kept-unchanged 25/25 (2 same-prompt, 23 no-LLM). vs X1: all 56/180, kept-unchanged 54/54 (28 / 26). Generation-side split: newly present 32, present under X1 64, non-fact only 59, unchanged 25.

| Cell (raw, paired, B 2000) | Haiku 5.5-low X2b − S | Opus judge.v1 X2b − S | Opus X2b − X1 (descr.) |
|---|---|---|---|
| pooled (180) | +0.056 (+0.036…+0.076), b/w 100/43 | **+0.066 (+0.043…+0.091)**, b/w 87/38 | +0.034 (+0.014…+0.054) |
| SE (100) / topic (80) | +0.060 (+0.033…+0.087) / +0.051 (+0.022…+0.084) | +0.070 (+0.036…+0.104) / +0.061 (+0.029…+0.097) | +0.018 / +0.053 |
| split newly present under X2b (30) | +0.155 (+0.090…+0.228) | +0.177 (+0.098…+0.263) | +0.174 |
| split present under X1 already (71) | +0.060 (+0.034…+0.087) | +0.081 (+0.053…+0.113) | +0.008 |
| split non-fact only (65) | +0.017 (−0.009…+0.045) | +0.008 (−0.025…+0.043) | +0.003 |
| split unchanged (14) | +0.000 (−0.030…+0.028) | +0.025 (−0.007…+0.065) | +0.007 |
| gen-side newly / X1 / non-fact / unchanged (32/64/59/25) | +0.142 / +0.064 / +0.021 / +0.009 | +0.180 / +0.089 / +0.010 / −0.004 | — |

Per pack X2b − S, Haiku | Opus:
- travel +0.144 | +0.157
- ethereum +0.072 | +0.087
- bitcoin +0.044 | +0.008
- health-se +0.045 | +0.069
- outdoors −0.003 | +0.031
- firstaid +0.011 | +0.009
- medlineplus +0.042 | +0.054
- factbook +0.127 | +0.132
- simplewiki +0.021 | +0.050

Haiku X2b − X1 pooled: +0.034 (+0.015…+0.052).
**No-harm v0.1 + simplewiki ON − OFF (Haiku, 57):** all +0.012 (−0.019…+0.046), b/w 18/21; fired (41): +0.006 (−0.032…+0.050).
**Haiku/Opus agreement (180):** same winner X2b 179/180, S 180/180; per-item Δ r 0.839.
**Judge calls:** Haiku 588 (360 + 228); Opus 360. 0 paid.
**Files:**
- aggregates/{agg-x2b, l2-opus-x2b, precheck-x2b, gen-split-x2b}.json, *.stdout.txt
- aggregates/same_answer.x2b-vs-{S,X1}.json
- gen-x2b/
- tools/{mkreq_x2b.py, run_x2b_gen.sh, gen_chain_x2b.sh, judge_chain_x2b.sh, l2_chain_x2b.sh, precheck_x2b.py, agg_x2b.py}
- logs/*_x2b*
**Adapter identity (closes the unverified item; 0 judge):** qa-health-se S requests with no settings, run on the cut7-headpass-x2 tree with the forwarding adapter a77838f1 and with the pinned 6298e5d3. Compared with the S traces: 20/20 identical on answer text, raw, kept, promptTokens, reasonCodes, tier and error. The same 20/20 holds S vs 6298e5d3 and 6298e5d3 vs a77838f1. same_answer.py 20/20 each (aggregates/adapter-identity.json; gen-adapter-id/; tools/{adid_chain.sh, run_adid_gen.sh, adid_compare.py}).

## Verdict X2b (coordinator, 2026-10-14 17:1x)
**LEVER on the 180 pack-matched self-tests (dev data).** Rule (HEADPASS-X2-criterion.md sha 1b70f6f3… + addendum 1 sha a66a3b79…): CI low > 0 and Δ ≥ +0.03 on the Opus pass declared up front → **+0.066 (+0.043…+0.091)** raw vs S (Haiku +0.056 (+0.036…+0.076)); above the +0.03 bar with the CI low at +0.043; v0.1 + simplewiki ON − OFF +0.012 (−0.019…+0.046) clears the no-harm clause (CI high ≥ −0.03); kit-only runs byte-identical; the adapter swap verified neutral (20/20 identical on every field, three adapter pairings). Mechanism: the fact chunk reaches the context on 102/180 (S 35) within a per-item budget of +600 prompt tokens, and the reader converts it (+0.177 where newly present, +0.081 where X1 already had it, +0.008 where only non-fact chunks were appended).
Scope and caveats: pack-matched dev items with agent-written gold; one seed (deterministic path); same tree for reach and quality (cut 7 + the headpass-x2 patch, no T-K2 sources patch); health-strict classification differs between the replay (lexical) and generation (mmbert) on 23 items (raw retrieval identical; present 97 in traces vs 102 in the replay); the X2 (unbudgeted) variant failed its cost gate and stays FAIL (R73). Not a bounty-bar lever: V-para is not pack-matched.
Product recommendation (pack line): **X1 + budgeted dense append as the default when a format-v3 pack (chunk vectors) is installed**; costs to state: sidecars ≈ +60 % pack size, dense scan p50 95 ms (simplewiki), +≈ 420 prompt tokens p50 (prefill on the phone), firing on ≈ 86 % of pack questions; kit-only behaviour unchanged. Next: X3 (reranker-chosen slots under the same budget; targets the 14 fact chunks the budget dropped and the 65 non-fact appends) — running; the cards' quality lines stay S numbers until a judged re-score under X2b.
