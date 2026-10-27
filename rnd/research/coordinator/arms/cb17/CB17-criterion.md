# CB17 criterion: closed-book Qwen3-1.7B (no added knowledge) on MAIN 97, for the per-item pack table (frozen 2026-10-21 before any generation or call)

## Question
How good is the 1.7B with no added knowledge on the same items where we already have the 1.7B with packs (K0 claim kit, K1 + simplewiki, K3 + factbook/health)?
Fills the missing rung of the per-item table "1.7B with vs without added knowledge" (research page, r4to request). Report arm; no ship decision rides on it.

## What "no added knowledge" means in this engine (exact)
- Same tree as the mini controls: the mini:<runner>/kiln/be-0cfd4a77-cut7-litepacks (cut 7 + X2b + CMP30OFF answer.ts 0d1ac07d, adapter-litedecline.ts d53c1487),
  plus ONE patch, tools/cb17-noretrieval.patch: src/rag/retrieve.ts `retrieve()` returns [] at entry. That is the only retrieval entry point
  (answer.ts deps.retrieve via the adapter, and the multipass orchestrator via the shim); packHeadPass and packDense2 then act on empty lists (inert).
- Requests: tools/mkreq_cb17.py = the LP-SCREENS K0 MAIN-97 control requests byte-for-byte except runId cb17-main-s42, config.arm
  cut7-headpass-x2+litepacks+cb17 and **config.kit = []** (no pack installed: no crypto, no wikivoyage, no simplewiki...).
- So removed: every installed pack AND the knowledge base (the bundled 300 Wikipedia intros + corpus-standard/full are still seeded into the
  app DB by the adapter, but nothing queries them). The prompt therefore never carries a source.
- Kept as they are (deterministic layers, stated, not removed): the FACTS r6 table (src/rag/facts.v1.json, deps.facts), calculators/arithmetic,
  travel distance (worldCities.v1.json), emergency numbers + the mmBERT emergency detector (:8094), condition cards / first-aid cards / co-hazard,
  small talk, verdict guard, citation checks, the health-from-memory refusal and the phrase-question decline (both fire on "no source"), and
  LITEDECLINE_OFF=5: the compact no-source declines are released and the answer is prefixed by the warning line
  "Not found in this phone's offline library. From the model's memory, may be wrong:". With no source, every knowledge answer takes that path,
  so the closed-book answer is exactly what the product shows when nothing is installed (persona/prompt/succinct style unchanged).
- Model: Qwen3-1.7B Q4_K_M, --reasoning off, seed 42, llama-server b11010 build-cpu -t 4.

## Host and pairing (MINI-BASELINE rule)
- Generation on the Mac mini only, via the LP-SCREENS 2-slot guard (arms/lp-screens/tools/mini_gen.sh: slot lock gen1/gen2, disk >= 25 GiB,
  detector :8094 used never started/stopped). Never Docker/ollama/:8094 management.
- Same-host pairs: closed-book vs lpctl-K0-main-s42 and lpctl-K1-main-s42 (mini controls, same tree and request bytes except kit). K3 exists only
  as MacBook LITEPACKS traces (lp-K3-*): its column is labelled "MacBook host" and its deltas carry the ~70 % host text-noise caveat.

## Sets (dev only; no blind/, no rnd/veil, no bench/v0.4)
MAIN 97 = arms/lp-screens/main-97.ids (v0.1 57 judged ids + st-qa-cooking-se 20 + st-qa-money-se 20). 97 generations.
CV5 51 = ruler/cv5-ladder/in/set.json ids (v0.1 57 minus FLOOR's 6 nonmodel-path items).

## Judges and budget (calls_cap: Opus 110 / Haiku 900 / paid 0)
- Haiku 5.5-low judge.v1-low, N = 4 shards, both orders, seed 7, arms/deepthink/tools/shard_judge.sh, units v01 / qa-cooking-se / qa-money-se,
  all 97 closed-book answers (194 calls), preflight + check_judgments.py (fail closed). Same judge config as the mini controls' rows.
- Opus judge.v1 (judge.mjs default opus), N = 4, both orders, seed 7, v0.1 frame refs bd235bb9 / questions 568b3ece (as CV5-LADDER-OPUS), on the
  CV5 51 ids. Units identical (id, text) to an existing Opus row on that frame (ruler/tools/cv5_opus_pool.py) are reused, the rest judged: <= 102 calls.
- DECLINE2STAGE stage 1 (ruler/tools/decline2stage_stage1.mjs, Haiku 5.5-low, one call per answer) on the 97 closed-book texts (97 calls).
  DECLINE2STAGE failed its own bar (b), so U_D2S is report-only beside U, exactly as CV5 (d).
- Planned: Haiku 291, Opus <= 102.

## Metrics (tools/cb17_table.py, committed with the results)
- Per item and arm: s, r = mean of the 3 dims averaged over both orders; corr = mean correctness over orders.
- U = sum(s-1)/sum(r-1) (CV5-LADDER metric, primary); U_net = (U-0.058)/0.942; Q = sum s / sum r with declined := 0 (LITEPACKS metric, secondary).
- CIs: item bootstrap B 2000, numpy default_rng(11), 2.5/97.5 pct; paired deltas on the same draws.
- Win/tie/loss of arm vs closed-book per item: tie if |s_arm - s_cb| <= 0.25, else win/loss.
- Flags: warned = text starts with the warning line; declined = trace answer.declined or the engine refusal strings
  (arms/null-cal/tools/labels.is_decline); D2S not-attempted (closed-book).
- Splits of Δ(K1 - CB), Δ(K0 - CB): fact present in the K1 kept context (ruler/FACTPRESENT-2026-10-21.json items[id].K1.present; 92 keyed
  ids), in-pack (ruler/inpack-assignment.json side), RAG-FUNNEL K1 stage (ruler/RAG-FUNNEL-2026-10-21.json).
- Columns per item: id, set, domain tag, in-pack, fact present K1, funnel stage K1, Haiku s for CB / K0 / K1 / K3(MacBook), Opus s where it exists
  (CB on the 51; K0/K1 from the existing Opus pool on the identical unit), Δ(K1-CB), Δ(K0-CB), warned/declined flags.

## Prediction (stated before the run)
On the CV5 51 under Opus: U(CB17) lies between the closed-book Qwen2.5-1.5B (0.261) and the 1.7B K0 (0.351). Outcome labels, mechanical:
BETWEEN / BELOW_15B (< 0.261) / ABOVE_K0 (> 0.351); plus whether K0 - CB has CI low > 0 (packs separable from no packs under Opus).
Secondary expectation: Δ(K1 - CB) is larger where the fact is present in the K1 context than where it is absent.

## Outputs
arms/cb17/PACK-TABLE-17B.md, arms/cb17/aggregates/pack_table_17b.{json,csv}, traces/judgments under arms/cb17/, one QUEUE row, one EXPOSURES row, commit rnd (own paths).
