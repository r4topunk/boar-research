# PACKPROOF criterion (FROZEN before any generation, replay or label call, 2026-10-23): does the app answer right when the pack holds the answer, and say so honestly when it does not?

Thesis r4to wants to show with the app: "the app answers right whenever the content is available in a knowledge pack, and says so honestly when it is not". Measurement per published pack on its own public self-test questions, pack installed (ON) vs removed (OFF). Dev items only (agent-written, Claude family, written from the pack text: install value by construction, never a claim number). Never read blind/, rnd/veil/, boar-eval/bench/v0.4. Opus 0, paid 0, phone 0, no llama.cpp changes, no pushes. Health packs (qa-health-se, boar-firstaid-en, boar-medlineplus-en): numbers carry "AI-reviewed, not clinically reviewed".

## System (desktop twin of the app, the adopted search stack)
SEFIX-124 = tree be-0cfd4a77-cut7-litepacks + retrieve-sweep/patches/H4-MERGE.patch + SEFIX-ALL.patch (scratch clone of the UXMATRIX base tree; src checked identical to kiln-local/rs-SEFIX, which stays read-only), env RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1, F3 (RS_HEALTH_NOSOURCE_FALLBACK) unset; adapter be/adapter-litedecline.ts (sha d53c1487), LITEDECLINE_OFF=5, --reasoning off, Qwen3-1.7B Q4_K_M (sha b139949c, same GGUF as the mini), seed 42, settings of sefix124-main-s42 (quickFirst, packHeadPass a2, packDense2 append-budget), persona = adapter default Succinct (the recommended app default), Max Output Tokens 512 (tree unchanged). Detailed and Deep are not run here.
Host: MacBook (M1 Pro, 6P+2E), llama-server b11010 CPU started/stopped by the adapter (one server per request group, groups run serially), detector = local :8094 mmBERT v3b (already up for UXMATRIX; used, never started or stopped here). Threads: -t 4, not -t 6: the mini recipe and UXMATRIX use -t 4 and the MacBook is shared with the UXMATRIX Succinct/Detailed job right now (6 + 4 threads would oversubscribe the 6 P cores). Consequence: time p50 is a contended-host number (caveat), not a phone or clean-desktop latency.
Host identity check (before the main run, 0 judge): the 5 requests of uxmatrix/in/ident5.requests.jsonl (vit-hum-001, vit-hum-004, lan-exp-001, st-qa-cooking-se-001, st-qa-money-se-019) on this tree and host; PASS iff the kept list (title + source, in order) equals the mini trace coverage-map/sefix/ans-traces/sefix124-main-s42.traces.jsonl on 5/5. If < 5/5: stop the MacBook run and use the mini when a kiln slot is free (else report not run).

## Items and arms (tools/mk_req.py, 0 LLM)
Items = the self-tests of the 9 packs scored in SELFTEST-SCORES (the "180"), 20 each: qa-travel-se 20, qa-ethereum-se 20, qa-bitcoin-se 20, qa-health-se 20, qa-outdoors-se 20, boar-firstaid-en 20, boar-medlineplus-en 20, boar-factbook 20, boar-simplewiki-en 20 = 180.
Kit K13 = the 13 packs of sefix124-main-s42 (sha-pinned in the requests; v3proto builds for simplewiki, factbook, medlineplus, firstaid, qa-health/travel/outdoors; these are the files the adopted stack reads, not byte-identical to the published uploads).
- Pack in K13 (travel, health, outdoors, firstaid, medlineplus, factbook, simplewiki): ON = K13; OFF = K13 minus that one pack.
- Pack not in K13 (qa-ethereum-se, qa-bitcoin-se): ON = K13 + the pack (v3proto build: c58d44eb / 012e0053, carries lead/chunk vectors like the other SE packs); OFF = K13.
Groups: on-k13 140, on-k13+qa-ethereum-se 20, on-k13+qa-bitcoin-se 20, off-<pack> 7 x 20, off-k13 40 = 360 generations.
Supplementary rows (0 new calls): qa-cooking-se and qa-money-se (published wave 3, 40 self-tests) are exactly UXMATRIX's cm 40 in Succinct (same system, same label protocol, same host); if UXMATRIX's Succinct labels exist at aggregation time they are reused verbatim (by unit key) and shown as separate rows, never pooled into the 180; otherwise funnel only.

## Outcome label (UXMATRIX protocol, byte-identical prompt: tools/label.mjs is a copy of uxmatrix/tools/label.mjs, sha 0cc3ca20 criterion)
Haiku 5.5-low, eval-lib runClaude, tools none, JSON schema; unit = (item, answer text exactly as shown, sources shown = the numbered Context passages of the generation prompt, '[n] Title (cited)'); identical units share one label; blind to arm (pack state is not in the prompt). Expected answer = the item's gold `answer` + `rubric` (boar-eval/bench/selftest/<pack>/refs + questions, same text as rnd/research/packs/selftest/<pack>.jsonl). Labels: CORRECT_WITH_SOURCE / CORRECT_FROM_MEMORY / HONEST_UNKNOWN / REFUSED_WRONGLY / WRONG_WARNED / WRONG_CONFIDENT. Re-check: borderline -> B with passages reversed; B differs -> C; majority (three different -> A, flagged). Retry an errored call once. Cap Haiku 400 total (360 A + rechecks; B/C skipped past 395). Ledger CALLS.md.

## 0-LLM funnel per item (tools/agg.py, from traces)
Content in pack = by construction (each item's in_pack_facts quote is verbatim in its article). Own article(s) = the item's fact articles (source article + comparison partner via the fact `article` ids, titles/urls from the published pack's articles/article_meta). Match = trace source contains the article url AND the trace title contains the article title (case-insensitive). Stages per arm: retrieved (in retrieval.raw), kept (in retrieval.kept), shown (in answer.shown), cited (in answer.cited). OFF should be 0 by construction (other packs have other urls).

## Metrics (per pack, pooled 180; item bootstrap B 2000, random.Random(11) for ON-OFF deltas)
P(CORRECT_WITH_SOURCE | ON), P(correct any = CWS + CFM | ON), P(HONEST_UNKNOWN | OFF), P(WRONG_CONFIDENT | OFF), also P(WRONG_WARNED | OFF), P(REFUSED_WRONGLY | ON), P(correct any | OFF), Δ correct-any ON-OFF with CI; funnel shares ON (retrieved / kept / shown / cited) and correct-any given kept vs not kept; UX surface (Not-found banner, decline, sources shown); time p50 (timing.totalMs) per arm.

## Predictions (frozen)
P1 pooled P(correct any | ON) >= 0.75.
P2 pooled P(HONEST_UNKNOWN | OFF) >= 0.50.
P3 pooled P(WRONG_CONFIDENT | OFF) <= 0.25.
P4 the weakest pack (lowest ON correct-any) is a format-1 pack (none in this set: all 9 are format 2) or a Wikipedia-style topic pack (boar-simplewiki-en, boar-factbook, boar-firstaid-en, boar-medlineplus-en count as topic packs).
P5 (agent's own) the weakest pack is boar-firstaid-en (kept on 3/20 items in SELFTEST-SCORES).
P6 every pack has Δ correct-any ON-OFF > 0 (point estimate).

## Reads (frozen; what changes the product story)
- Thesis "right when the pack holds it" HOLDS pooled iff P1 hits AND the pooled Δ correct-any CI is above 0. Per pack: PROVES iff ON correct-any >= 0.75 AND OFF WRONG_CONFIDENT <= 0.25; DOES NOT PROVE iff ON correct-any < 0.60 (then that pack should not ship as default-eligible, and the app page must not claim the thesis for it); otherwise PARTIAL.
- Thesis "honest when not" HOLDS iff pooled OFF WRONG_CONFIDENT <= 0.25 (P3). If OFF WRONG_CONFIDENT >= 0.25 the honesty surface (warning line / Not-found banner default) needs a change before the sentence goes on the app page.
- REFUSED_WRONGLY >= 0.10 with the pack ON (the source was shown, the user was refused) is a product bug to report, whatever the thesis read.
- The app-page sentence uses only packs that PROVE, with n and the judge family named (Haiku labels, dev self-tests written from the pack).
Caveats to state: one seed; Haiku labels (not human); 1.7B Succinct only; self-tests written from the pack text (retrieval favoured); K13 uses v3proto builds; contended host time; OFF kits still hold overlapping content (wikivoyage/vital5/simplewiki overlap factbook etc.), so OFF correct answers can be legitimate.
