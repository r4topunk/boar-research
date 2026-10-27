# DEEPMODE criterion (FROZEN 2026-10-23 before any generation or judge call; never edited after; addenda go to DEEPMODE.md)

Question (r4to): the app's "Deep Research" mode (multi-pass on the SAME small model) has never been measured with Qwen3-1.7B. Measure it with the PARA135 protocol
so the numbers line up with TOPICS27 / TOPICS27-SUCCINCT (set A) and style17-detailed D17 / K1 Succinct control S17 (set B). Measurement for r4to, no adoption rule.
Public / dev sets only. Haiku 5.5-low only; Opus 0, paid API 0, phone 0, no pushes, no llama.cpp changes. Never read blind/, rnd/veil/, boar-eval/bench/v0.4.

## What the mode is (read from the code before any run)
Bench engine K1 litepacks tree (mini <runner>/kiln/be-0cfd4a77-cut7-litepacks; answer.ts 0d1ac07d, depth.ts b606d147, src/services/orchestrator.ts 0034f31f,
adapter be/adapter-litedecline.ts d53c1487, app-shims/orchestrator-retrieve.mjs 8cde9d9d).
- Trigger: a settings flag. The app's Deep Research switch sets AnswerSettings.alwaysComplete (boar-app src/models/settings.ts:499 `alwaysComplete: s.answerAlwaysComplete ??
  s.deepResearchMode`; the native app's toggle calls its DeepResearch.run, a port with the same prompts, golden-tested). depth.ts planAnswer: complete = requestedTier deep or
  (auto and alwaysComplete); no deep model installed -> generation {tier "deep", mode "multipass" (single when the task needs no retrieval), retrieveK FAST_RETRIEVE_K 6,
  contextTokens 1200, thinking true}; instant = "preview" (a no-LLM snippet first, not the answer). The engine's other entry, deepen() after a fast answer's
  deep_available ("offer-deep:multipass"), runs the same multipass (tier deep, reuseSources; the orchestrator retrieves on its own and does not read the reused
  sources). We run the toggle (alwaysComplete true), which is what both apps expose; the user-triggered second-pass cost is reported as fast Detailed ms + DEEP ms.
- Passes (orchestrator.ts runDeepResearch): (1) decompose: system "You plan research.", 2-3 sub-questions, nPredict 150, temperature 0.4; (2) per sub-question (<= 3):
  retrieve(sub, 6) (plain retrieve: no packHeadPass / packDense2 / grounding guard), compressContext to 600 tokens, keep chunks onTopic(sub) or onTopic(query),
  global [n] numbering; generation with system "<persona system prompt> Answer the question in a short paragraph using the context. Cite sources ... If the context does
  not cover it, say so.", nPredict 300, temperature 0.6; (3) synthesize: system "<persona system prompt> You are synthesizing multiple research perspectives into one
  answer. Compare them, reconcile any conflicts, and write one unified, well-reasoned answer. Keep the source numbers ...", user = original question + the sub-answers
  (the synthesis sees no source chunk), nPredict = Max Output Tokens, temperature 0.6. Stage timeout 120 s. The persona's style reminder is NOT passed to multipass.
  Health questions never go multi-pass (grounding:health-no-multipass): single pass, retrieveK 6, context budget max(256, min(1200, 4096 - maxTokens - 512 - 1024)).
- Persona: Detailed (personalityId "detailed", persona sha be0e6710 = TOPICS27 / D17). Max Output Tokens 2048 (= the native app's Deep Research auto cap
  AUTO_MAX_TOKENS_RESEARCH; adapter sed 512 -> 2048 in the job clone, the only tree change). llama-server ctx 4096.

## System (PARA135 recipe)
Mini, APFS clone of the base tree (shas above), no engine patch, tools/run_gen.sh (sha 6d6aacae; topics27/tools/mini_gen_dump.sh 8816220f: slot lock gen1/gen2, disk >= 25 GiB,
detector :8094 used, never started/stopped), qwen3-1.7b-q4km, seed 42, --reasoning off, LITEDECLINE_OFF=5, llama-server b11010 CPU -t 4, --dump-prompts.
Requests (tools/mk_req.py sha 923c0639): set A = topics27/in/t27-detailed-s42 requests, set B = para135/in/p135-b-p1-s42 requests (CV5 51, questions of style17-detailed),
with only settings changed (personalityId detailed, persona override keys removed, alwaysComplete true). Kits: A = wiki-vital5 only (d3b87d56) + essential corpus
(compose/packs-k13); B = K1 (boar-crypto ae9fbd2c, boar-wikivoyage-en ff8595e3, boar-simplewiki-en 99bcec30; compose/packs-k1) + essential. K1 settings packHeadPass a2,
packDense2 append-budget stay in the requests (used only by single-pass items).
Reference arms, reused, 0 new calls: set A fast Detailed = TOPICS27 (gen/, judge/audit.jsonl + judge-succinct/sens-detailed.jsonl, maxTokens 512), fast Succinct =
TOPICS27-SUCCINCT (gen-succinct/, judge-succinct/); set B fast Detailed = D17 (style17-detailed K1 s42, maxTokens 1024) and fast Succinct = S17 (lpctl-K1-main-s42,
maxTokens 512), with the judge rows PARA135 tools/agg_b.py loads for them (K1 control rows for identical texts).

## Set A (27 Research Topics) metrics
Retrieval (0 LLM): HIT = an expected/anchor title of topics27/aggregates/titles.json (any title of any group, the TOPICS27 agg.py rule) is among the chunks the model read:
DEEP = titles of the chunks in its research-stage contexts (single-pass items: the context block), fast = trace retrieval.kept (TOPICS27 in_kept 23/27). Also in-raw
(any retrieve call), chunks read per answer (DEEP distinct [n]; fast kept count), route mode counts, retrieval ms (trace timing.retrievalMs) and generation ms (totalMs).
Support audit: tools/prep_a.py (sha bca69cc9) splits with para135/tools/para.py (ed6afae3; sentence rules = topics27 split.py b8a389a4) and sets the audit context: single-pass
context block if any; else the union of the research-stage contexts (deduplicated by [n], ordered by n); else "(no source chunks were given to the model)". tools/audit_a.mjs
(sha 18f8c9ed) = the exact TOPICS27/PARA135 Haiku 5.5-low per-sentence prompt + schema, no batching, cap 450 invocations incl. retries (retry once; unresolved = missing,
reported). Sample: all sentences if <= 430, else stratified by paragraph position (1..5, 6+), proportional largest remainder, >= 1 per non-empty stratum,
default_rng(2048). Metrics: sentences, audited, unsupported share (UNSUPPORTED / audited, stratum-weighted estimate when sampled), PARTIAL share, invented specifics
(UNSUPPORTED or PARTIAL with invented_specific; sample count and estimate), num_absent (0 LLM), banner count, output tokens p50 / mean, at cap (>= 2047), words p50;
BY POSITION 1..5, 6+: sentences, audited, unsupported share (Wilson 95 %), invented per audited sentence, share of invented. References: Detailed 0.468 primary (0.447 all
per-sentence), Succinct 0.283 (TOPICS27-SUCCINCT summary); Detailed by position from its per-sentence labels (PARA135 secondary table rule).

## Set B (51 CV5 dev ids) metrics
Judge: Haiku 5.5-low judge.v1-low, deepthink/tools/shard_judge.sh N 4, both orders, set v01, bench/v0.1 (tools/judge_b.sh sha fc03b489), 102 planned calls.
PARA135 agg_b.py definitions: U floor-adj = sum(s-1)/sum(r-1) with item bootstrap B 2000 default_rng(11), U raw, win-rate vs the reference, correct-shown per 100,
confident errors per 100 (LITEPACKS rule: not declined and correctness <= 1.5), output tokens p50, at cap, total ms p50 (timing.totalMs; DEEP = the whole multipass),
deepen cost p50 = per-item D17 ms + DEEP ms. Paired DEEP vs D17 and DEEP vs S17: dU (CI), better / tie / worse per item (s compared).
Chunk-level delivered facts (0 LLM): coverage-map/tools/chunklevel.py share_v01 (v0.1 keyed items only) on each chunk body the model read, PRESENT = any chunk share >= 0.5;
DEEP = research-stage (or single-pass) context chunks; fast = the context block of para135 p135-b-p1-s42's dumped prompts (same tree, kit and retrieval settings as D17/S17;
persona does not enter retrieval; kept titles checked against D17's trace, mismatches reported). Reported as delivered / keyed for fast and DEEP, gained / lost.
Subgroup (stated in advance): items where fast kept nothing (D17 trace kept empty) vs the rest: DEEP - D17 paired dU on each.

## Predictions (frozen; scored hit/miss)
P1 Set A: DEEP hit rate >= fast + 2 topics (>= 25/27).
P2 Set A: DEEP unsupported share (estimate) strictly between Succinct 0.283 and Detailed 0.468.
P3 Set B: U(DEEP) - U(D17) >= +0.02 (point estimate).
P4 Time: DEEP total ms p50 >= 2x fast Detailed ms p50 on both sets (A vs TOPICS27 Detailed, B vs D17).

## What would change the recommendation (stated, not a rule)
Current: Succinct default for the 1.7B; Deep Research is exposed in the app but unmeasured. Offer/keep it as a general option only if set B U(DEEP) >= U(S17) - 0.02 with
CE/100 not above S17's and set A unsupported <= Detailed's. If DEEP beats D17 only on items where the fast pass kept nothing (subgroup dU > 0, rest <= 0), the reading is
"deep worth offering only when the fast pass kept nothing" (a fallback trigger, not a mode). If U(DEEP) < U(D17) - 0.02, or set A unsupported >= Detailed's, the reading is
to hide or relabel Deep Research for the 1.7B (slower and not better).

## Caveats to state
One seed (42), temperature 0.4-0.6 stages; Haiku audit (UNSUPPORTED = not in the context read, not false) and Haiku judge (compresses gaps; over-calls CE on long warned
answers); bench engine K1 tree, not the native app (same prompts, but different retrieval/guards); multipass skips the K1 head pass / dense append and the grounding guard;
maxTokens 2048 vs 512 (TOPICS27) / 1024 (D17); DEEP audit context is every chunk the research stages read although the synthesis reads only the sub-answers; dev sets.

## Budget
calls_cap: Haiku 654 / Opus 0
(set A audit 450 + set B judge 204 incl. retries; set B plans 102.)
