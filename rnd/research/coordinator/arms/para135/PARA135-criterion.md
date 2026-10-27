# PARA135 criterion (FROZEN 2026-10-23 before any generation or judge call; never edited after; addenda go to PARA135.md)

Question (r4to): how does the 8 GB engine's model (Qwen3-1.7B Q4_K_M) behave when the answer is constrained to exactly 1, 3 or 5 paragraphs? Length curve of
support (does support decay with each extra paragraph), where invented specifics sit (paragraph 1 vs later), and what a judge makes of 1 vs 3 vs 5 paragraphs
on real dev questions. Measurement for r4to, no decision rule. Public / dev sets only. Haiku 5.5-low only; Opus 0, paid API 0, phone 0, no pushes,
no llama.cpp changes. Never read blind/, rnd/veil/, boar-eval/bench/v0.4.

## Arms (personas/paraN.json, file sha256 ee415c8a / e19fe460 / 54a04602)
System prompt = the tree's Detailed persona verbatim ("You are Boar, an analytical research partner. Provide thorough, structured explanations with comparisons
and evidence."). Style reminder = the Detailed reminder with its length instruction "3-5 paragraphs" replaced:
- p1: "Be thorough: Answer in exactly 1 paragraph that covers the key points in depth, with reasons, comparisons and examples. Don't repeat yourself." (adapter persona sha 66b3e6f1)
- p3: "... Answer in exactly 3 paragraphs that cover ..." (aea817de)
- p5: "... Answer in exactly 5 paragraphs that cover ..." (aee8b9a1)
Passed as the adapter's literal override (settings.personaSystemPrompt + personaStyleReminder; the engine sees only systemPrompt + styleReminder, as the chat passes them).
Detailed persona check: sha256(JSON [system, Detailed reminder]) = be0e6710... = runtime.versions.persona.sha256 of TOPICS27 and style17-detailed traces.

## System (TOPICS27 recipe)
Mini, APFS clone of <runner>/kiln/be-0cfd4a77-cut7-litepacks (answer.ts 0d1ac07d, adapter d53c1487 guards), no engine patch. One tree change: adapter Max Output Tokens
512 -> 1024 by sed in the clone (= the app's maxTokens setting option 1024 and the STYLE15B / style17-detailed Detailed cap; TOPICS27 Detailed ran at 512 and 2/27
answers reached it). Context budget is unchanged by this (min(1200, 4096 - maxTokens - 512 - 256) = 1200 at both caps). Settings K1 (quickFirst true, alwaysComplete
false, packHeadPass a2, packDense2 append-budget), qwen3-1.7b-q4km, seed 42, --reasoning off, LITEDECLINE_OFF=5, llama-server b11010 CPU -t 4,
topics27/tools/mini_gen_dump.sh (slot lock gen1/gen2, disk >= 25 GiB, detector :8094 used, never started/stopped), tools/run_gen.sh (sha c26fb720).
- Set A: the 27 Research Topics (topics27/in/topics.json EN strings), kit wiki-vital5 only (d3b87d56...) + corpus essential (compose/packs-k13 dir). Requests in/p135-a-pN-s42.
- Set B: the 51 CV5 dev ids (native-parity/cv5-51.ids; questions from style17-detailed requests), K1 kit (boar-crypto ae9fbd2c, boar-wikivoyage-en ff8595e3,
  boar-simplewiki-en 99bcec30; compose/packs-k1 dir) + essential. Requests in/p135-b-pN-s42.
Reference arms, reused, 0 new calls: set A = TOPICS27 Detailed (gen/ + judge/audit.jsonl + judge-succinct/sens-detailed.jsonl, maxTokens 512) and TOPICS27-SUCCINCT;
set B = style17-detailed (D17: same base tree, K1 kit shas, Detailed persona be0e6710, maxTokens 1024 via patch, FACTS on, its Haiku rows + K1 control rows for identical
texts as in ship15b_analyze.py) and the K1 Succinct control S17 (lpctl-K1-main-s42, maxTokens 512). They are shown beside the arms, not part of any prediction.

## Paragraphs and sentences (0 LLM)
tools/para.py (sha ed6afae3) on the answer text; sentence rules = TOPICS27 split.py (sha b8a389a4, unchanged; para.py's flattened sentence list equals split.py on all
27 TOPICS27 and 57 style17-detailed answers). Paragraph boundary = blank line, or a newline before a prose line when the previous line ends a sentence; bullets stay in their
paragraph; dropped headings close a paragraph; paragraphs with 0 sentences are not counted; the banner line is removed and counted. Position = paragraph index 1..5, 6+.
Compliance = produced paragraphs == N (also reported: within +-1). Both sets.

## Set A audit (Haiku 5.5-low, TOPICS27 sentence support protocol, exact system + user prompt + JSON schema of topics27/tools/audit.mjs, per-sentence calls only, no batching)
Context = the context block of the answer's own dumped prompt; else replay keptFull; else the fixed "(no source chunks were given to the model)" string.
Cap 450 invocations incl. retries (retry once; unresolved = missing, reported). Sample (tools/prep_a.py sha bb1bc504, outcome-blind, depends only on sentence counts per
position): 430 primary calls; p1 all sentences if <= 150 else stratified 150; the rest split p3 / p5 evenly (slack of a fully audited arm moves to the other); strata =
paragraph position, proportional largest-remainder allocation, >= 1 per non-empty stratum, uniform without replacement default_rng(135 + N).
Metrics per arm: sentences (all), audited, unsupported share (UNSUPPORTED / audited; estimate weighted by stratum sizes when sampled), PARTIAL share, invented specifics
(UNSUPPORTED or PARTIAL with invented_specific; count in the sample and the stratum-weighted estimate for all sentences), num_absent (0 LLM, all sentences), banner count,
compliance, output tokens p50/mean, at cap (>= 1023), generation ms p50 (timing.totalMs), words p50; BY POSITION (1, 2, 3, 4, 5, 6+): sentences, audited, unsupported share
with Wilson 95 % CI, invented per audited sentence, share of the arm's invented specifics. Secondary (0 calls): the same position table for TOPICS27 Detailed
(all per-sentence labels incl. the sensitivity re-audit of its batched units).

## Set B judge (Haiku 5.5-low judge.v1-low, deepthink/tools/shard_judge.sh N 4, both orders, set v01, bench/v0.1; the style17-detailed recipe)
Each arm judged once on all 51 ids against the references (2 calls per id; identical (id, text) to D17 or S17 may reuse those rows, stated). Metrics (ship15b_analyze.py
definitions): U floor-adj = sum(s-1)/sum(r-1) with item bootstrap B 2000 default_rng(11), U raw, win-rate vs reference, correct-shown and confident errors per 100
(LITEPACKS rule: not declined and correctness <= 1.5), output tokens p50, at cap, ms p50 (timing.totalMs), compliance; paired vs p1: dU (CI), better/tie/worse per item.

## Predictions (frozen; scored hit/miss)
P1 Set A unsupported share rises monotonically with N (p1 < p3 < p5, point estimates).
P2 Set A invented specifics concentrate in paragraphs >= 3: in p5, positions 3-5 hold > 50 % of its invented specifics (estimate) and their invented rate per audited
   sentence exceeds that of positions 1-2.
P3 Set B judged U peaks at 3 or is flat 1-3 (U(p3) >= U(p1) - 0.02) and drops at 5 (U(p5) < U(p3)), with more confident errors at 5 (CE/100 p5 > p3).
P4 Compliance >= 80 % at N = 1 and N = 3 and lower at N = 5 (set A and set B pooled, 78 answers per arm).

## What would change the persona recommendation (stated, not a rule)
Current recommendation: Succinct over Detailed for the 1.7B (TOPICS27-SUCCINCT, STYLE15B). It would change toward a fixed-paragraph persona if p1 (or p3) matched or beat
S17 on set B (U within 0.02 or better, CE/100 not higher) while its set A unsupported share stays <= the Succinct 0.28; it would confirm "short is safer" if support
decays with position (first paragraph clearly better supported than later ones) and U does not rise with N.

## Caveats to state
One seed (42); Haiku audit (UNSUPPORTED = not in the context, not false) and Haiku judge (compresses gaps; known to over-call CE on long warned answers); bench engine K1
tree, not the native app; set A sample-based estimates for p3/p5; maxTokens 1024 vs TOPICS27 Detailed 512; dev sets (CV5 51 of v0.1 is dev; the 27 topics are public).

## Budget
calls_cap: Haiku 1062 / Opus 0
(set A 450 + set B 612 = 3 arms x 51 x 4; set B plans 306.)
