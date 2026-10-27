# TOPICS27-SUCCINCT criterion (FROZEN 2026-10-23 before any run; never edited after; addenda go to SUCCINCT.md)

Question: TOPICS27 (criterion sha c97bd9d7..., Detailed persona) found 46.8 % unsupported sentences, 98 invented specifics, 11 banners, KEEP 7/27, and its reading said nine topics are "fine for the 1.7B only with the Succinct style" (not measured). Measure the Succinct persona on the same 27 topics, everything else identical, so the two arms are comparable.
Public set (maintainer's strings), dev use only. Judge Haiku 5.5-low only; Opus 0, paid API 0, phone 0, no pushes, no llama.cpp changes. Never read blind/, rnd/veil/, bench/v0.4.

## System (identical to TOPICS27 except the persona)
Tree K1 litepacks (mini <runner>/kiln/be-0cfd4a77-cut7-litepacks, APFS clone per job, no patch, same answer.ts 0d1ac07d / adapter d53c1487 guards), settings K1 (quickFirst true, alwaysComplete false, packHeadPass a2, packDense2 append-budget) + personalityId **"succinct"**. Kit wiki-vital5 only (sha d3b87d56...), corpus essential, qwen3-1.7b-q4km, seed 42, --reasoning off, LITEDECLINE_OFF=5, llama-server b11010 CPU -t 4, mini_gen_dump.sh (slot lock, disk >= 25 GiB, detector :8094 used, never started/stopped). Requests = in/t27-detailed-s42.requests.jsonl with personalityId -> succinct and runId -> t27-succinct-s42 (nothing else changed). Job t27-succinct-s42; outputs gen-succinct/ (gitignored). Detailed outputs (gen/, judge/audit.jsonl, aggregates/topics27.json, summary.json) are not touched.

## Split + audit (identical rules)
Splitter tools/split.py (sha256 b8a389a41ce9bd7ccc21c3ed3b08ae8a00cfe1f0dcb857f2fcde4b42c1eadaa1, unchanged). Context = the context block of the Succinct answer's own dumped prompt; if absent, replay keptFull; if no context, "(no source chunks were given to the model)" (TOPICS27 Addendum 1 handling). Same system prompt, same user prompt, same JSON schema, same Haiku 5.5-low via runClaude, retry once, unresolved = missing.
Batching (mirrors the Detailed keys exactly): per-sentence calls for every sentence of q1..b13 and the first 3 sentences of b14 (TOPICS27 audited b14#0-#2 singly); the remaining sentences of b14 and all sentences of b15..b21 get ONE batched call per topic (same batched prompt as TOPICS27 audit.mjs), flagged batched. 0-LLM num_absent as in TOPICS27.
Secondary (sensitivity only, never changes a verdict or a prediction outcome): if calls remain, (s1) per-sentence audit of the Succinct units that were batched; (s2) only if primary + s1 + 95 <= 295, per-sentence audit of the 95 Detailed units that TOPICS27 batched, written to a new file (judge-succinct/sens-detailed.jsonl), so both arms can also be compared fully per-sentence. Cap: <= 300 Haiku invocations for this whole task (ledger CALLS.md).

## Verdict (TOPICS27 frozen rule, applied mechanically to the Succinct trace)
unsup = UNSUPPORTED / audited; inv = UNSUPPORTED or PARTIAL with invented_specific. SWAP if not PRESENT (aggregates/titles.json) or (unsup >= 1/3 and inv >= 1) or empty / declined; else FIX-PACK if not IN KEPT (live Succinct trace); else KEEP (+ watch note as in TOPICS27).

## Predictions (frozen; each scored hit/miss)
P1 unsupported share (pooled) Succinct <= Detailed - 0.15 absolute, i.e. <= 0.318 (Detailed 0.468).
P2 invented specifics Succinct <= half of Detailed, i.e. <= 49 (Detailed 98).
P3 banner count Succinct <= 5 (Detailed 11; shorter answers should trip the weak-sources check less).
P4 KEEP count under the frozen verdict rule >= 12/27 (Detailed 7).

## Caveats to state
Bench engine K1 tree, not the native Kotlin app; one seed; Haiku support audit (UNSUPPORTED = not in context, not false); shorter answers make the 1/3 rule coarser per topic (few sentences); EN only, 1.7B only.
