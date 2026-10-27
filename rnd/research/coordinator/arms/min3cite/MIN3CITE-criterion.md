# MIN3CITE criterion (frozen 2026-10-21 before any judged screen; 0 judge calls spent before this freeze)

Question: MINISTRAL3-3B (arms/ministral3-3b/MINISTRAL.md) fixed many confident errors on the GATE v2 screens but failed on false refusals, because
Ministral drops or misplaces the engine's `[n]` citations and the compact-model rules then release its answers behind the warning line. Does the same
model swap plus a minimal Ministral-only prompt adaptation (citation format + length, system/style text only) pass GATE v2?
No change to retrieval, routing, decline rules, citation checks (src/routing/citations.ts) or the warning logic.

## Candidate
- `min3cite.patch` (sha256 `26f4200a9ee88ad08c56ce8e6434a631bbd64317148f12485faff20b1501d9d4`, = patches/min3cite-v2.patch), relative to the lp-screens tree
  root (patch -p1). It is ministral3-3b.patch (V, sha256 a85fd741..., unchanged: Ministral-3-3B-Instruct-2512 Q4_K_M sha256 9ed150d4..., catalog size
  held at the 1.7B value, vendor sampler T 0.1 with top_k 0 / top_p 1 / min_p 0, health items keep T 0) plus:
  - be/adapter-litedecline.ts: `BOAR_MIN3CITE ??= "1"`, trace versions["prompt.min3cite"] = "v2".
  - be/server.ts `min3citeMessages` (applied to chat requests only when BOAR_MIN3CITE=1, i.e. only for the Ministral swap):
    1. system message: "Answer in 2-3 short, direct sentences" -> "Answer in 2-4 short, direct sentences" (persona length sentence only).
    2. last user message, the style reminder "Keep it short: 2-3 sentences. No lists unless the question asks for one." is replaced by
       - with sources in the prompt (k = highest "[n] " line number in the system message's Context; range = "[1]" if k = 1 else "[1] to [k]"):
         `Keep it short: 2-4 plain sentences, no lists or bold. Base the answer on the sources, numbered ${range}, and reuse their wording. End each sentence that states a fact from a source with that source's number, one number per bracket, for example: "Water boils at 100 degrees Celsius at sea level [1]." A sentence not taken from a source gets no brackets. Do not add a list of sources.`
       - without sources: `Keep it short: 2-4 plain sentences. No lists unless the question asks for one.`
    Prompts whose text does not contain those exact strings (other system prompts, gate/verifier calls) pass unchanged. Unit check over the 103
    LITEPACKS prompts (onboarding/prompts-litepacks.jsonl): 103/103 system and user messages changed, k distribution 1-7 matches the 57 source prompts.
- Arm name `min3cite`. Sampler = vendor's (T 0.1) as in the best Ministral run (min3v).

## Smoke (generation only, 0 judge calls; 10 screen items with sources: smoke/smoke-K0.ids 5 + smoke/smoke-K1.ids 5; tools/smoke_gen.sh = run_pool.sh steps 1-3)
Compliance = share of source-present answers (shown sources, not declined) whose final answer.cited is non-empty, i.e. >= 1 [n] the engine kept
after CT-1 removal and attribution (tools/citecomp.py). Wording iterated 3 times on the smoke only.
| version | change | compliant | warned (of 10) | answer tokens median / mean | sentences median |
|---|---|---|---|---|---|
| base min3v (same items, screen traces) | none | 2/10 | 8 | 102 / 96 (13 rows incl. K0/K1 overlap) | 2 |
| v1 | format line + example + `Never write "[1, 2]", "[general knowledge]" or a list of sources` | 6/10 | 4 | 84.5 / 82.5 | 3.5 |
| **v2 (frozen)** | v1 minus the negative examples (v1 primed "[general knowledge]"), plus "Base the answer on the sources ... reuse their wording", "A sentence not taken from a source gets no brackets" | **10/10** | **0** | 100 / 96.7 | 4 |
| v3 | v2 + "under 70 words in total" | 6/10 | 4 | 77.5 / 79.7 | 4 |
v2 is frozen: it is the only version with full compliance; the word cap (v3) cut about 20 tokens but lost 4 citations. Length is not reduced vs min3v
(the 2-4 sentence ask is met at about 4 sentences); expected answers about 2.2-2.4x the 1.7B's.

## Stage 1 (screen): GATE v2, arms/null-cal/GATE-V2.md sha256 `34ada53f1a9ab4ae31d971b6989eba3b4b979de8e05516fa687aad238a582982` (commit 8c175580)
- tools/screen_gate_v2.py sha256 fa726fc0ac0b2380... (K0: BAR_NET 10, MAX_FALSE_REF 2, MIN_UCOV_DELTA -0.059; K1: BAR_NET 9, MAX_FALSE_REF 4,
  MIN_UCOV_DELTA -0.071), tools/labels.py 0d93acec8dd575c5..., run_pool.sh e277d8c722e00c70...
- Screens null-cal/pool/screen2-K0.ids (891b67e2...), screen2-K1.ids (2d45ca83...); controls null-cal/control/pool-K0.json, pool-K1.json.
- Runs (2): `OUT_BASE=arms/min3cite/screen SCREEN_JSON=null-cal/pool/screen2-<K>.json CRITERION=<this file> bash null-cal/tools/run_pool.sh min3cite <K> null-cal/pool/screen2-<K>.ids arms/min3cite/min3cite.patch`;
  mini generation (gen1/gen2 slot lock), seed 42, Haiku 5.5-low judge.v1-low, N = 4, both orders; only answers that differ from the control are judged.
- Verdict per run = the gate line printed by screen_gate_v2.py (GO iff net >= bar and false refusals <= max and U_cov delta >= min).
- Reported per run: CE-unwarned (control vs candidate), false refusals, U on covered, citation compliance (tools/citecomp.py, control vs candidate
  vs min3v), answer tokens median/mean, wall (mean totalMs ratio vs control; ministral3-3b/tools/screen_extras.py), projected Pixel 8a model time
  (tools/pixel_proj.py: output tokens / 6.5-8.7 tok/s + prompt tokens / 41.1 tok/s, full prefill, retrieval excluded; 1.7B: /12-16 and /85).
- Sanity (run void and repeated once if violated): traces n/n, 0 error rows, model.sha256 9ed150d4 on every row, temperature 0.1 on non-health items,
  versions["prompt.min3cite"] = "v2" on every row, 0 dead items changed.

## Stage 2 (only if stage 1 GO on K0)
- `CRITERION=<this file> bash lp-screens/tools/run_arm.sh min3cite K0 main arms/min3cite/min3cite.patch` (MAIN n 97 = main-97.ids sha256 9664d81f...,
  control lpctl-K0-main-s42).
- **PASS iff U delta >= +0.03 with paired bootstrap CI low > 0 (agg_run.py, B 2000 seed 11) AND CE-unwarned rate change <= +0.02**, computed by
  arms/ministral3-3b/tools/stage2_verdict.py (sha256 e60e7371..., frozen with MINISTRAL-criterion.md, reused unchanged). Also reported: projected Pixel
  8a answer time p50 on the 97. A PASS is a screening result (phone speed/PSS unmeasured), not an adoption.

## Budget
calls_cap: Haiku 450 (2 screens <= 2 x 2 x 50 = 200; stage 2 <= 194; rest = one sanity re-run). 0 Opus, 0 paid APIs.
