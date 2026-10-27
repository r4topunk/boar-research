# QWEN35-2B criterion (frozen 2026-10-20 before any screen generation)

## Question
Does Qwen3.5-2B at native quant (unsloth Q4_K_M), dropped into the 1.7B's slot of the LITEPACKS system (refuse-by-default product: compact declines released behind the warning line), give fewer default-mode confident errors and more usefulness than Qwen3-1.7B? Audit finding MC-1 (research-2026-10-20/model-usage/model_choice.md, refute-2.md): the only earlier measurement used the 1-bit ternary derivative (Bonsai2-2B PTQ1_0).
Onboarding passed: ONBOARDING.md (checkpoint, template diff byte-identical, thinking off, context fit, smoke 0 failures). Known risk from the smoke: answers are 1.5-2.4x longer.

## Model and candidates
- Weights: Qwen/Qwen3.5-2B @ 15852e8c (Apache-2.0) as unsloth/Qwen3.5-2B-GGUF @ f6d5376b `Qwen3.5-2B-Q4_K_M.gguf`, sha256 aaf42c8b7c3cab2bf3d69c355048d4a0ee9973d48f16c731c0520ee914699223. llama-server b11010, -t 4, `--reasoning off`, -c 4096. Same requests, retrieval, prompts, packs, warning line, release logic and seed 42 as the control.
- **V (primary; the coordinator's spec):** qwen35-2b.patch (sha256 f5c18f12b01f8136d29f962eee39a7eab6f3c9d8847479f3d9754aec942d7aa8) = model swap + the vendor's non-thinking text sampling T 1.0, top_p 1.0, top_k 20, min_p 0, presence_penalty 2.0 (health items keep the engine's T 0).
- **E (secondary; model swap only, engine sampling 0.7/40/0.95/0.05 unchanged):** qwen35-2b-engsamp.patch (sha256 a0e202d1f900fa8b1ae3a1f9d15f8352f0018d911d9b37ce6f8a0d80d120e3f1). It separates the model from the sampler, because a NO on V alone could be a sampler artefact.
- Control = the deterministic mini controls of GATE v2 (null-cal/control/pool-K0.json, pool-K1.json) and, for stage 2, lp-screens lpctl-K0-main-s42.

## Gate: GATE v2 (arms/null-cal/GATE-V2.md + tools/screen_gate_v2.py, commit 8c175580)
- Screens (dev only): null-cal/pool/screen2-K0.ids (30 problems + 20 sentinels, sha256 891b67e2...) and screen2-K1.ids (21 + 20, sha256 2d45ca83...).
- Run: `OUT_BASE=arms/qwen35-2b/screens SCREEN_JSON=null-cal/pool/screen2-<K>.json run_pool.sh <q35v|q35e> <K> null-cal/pool/screen2-<K>.ids <patch>` (mini via the gen1/gen2 slot lock; judge on the MacBook).
- GO per screen iff net >= 10 (K0) / 9 (K1), false refusals <= 2 (K0) / 4 (K1) of 20 sentinels, and U_cov delta >= -0.059 (K0) / -0.071 (K1). Parameters as frozen in screen_gate_v2.py PARAMS.
- Reported per screen: the gate line verbatim, CE-unwarned counts (control vs candidate), declines, warned, answer tokens, and wall time (tools/wall.py: sum totalMs over live items vs the mini control traces; the control ran earlier under a different mini load).

## Stage 2 (per candidate)
- Runs only if (a) that candidate's **K0** screen says GO (stage 2 is on K0; the K1 line is reported but cannot authorise stage 2 alone) AND (b) its K0-screen wall ratio (tools/wall.py) <= 1.5.
- Set: MAIN n 97 on K0 (lp-screens/main-97.ids, sha256 9664d81f...) via `lp-screens/tools/run_arm.sh <q35v|q35e> K0 main <patch>` vs the cached mini control lpctl-K0-main-s42.
- Verdict (tools/verdict2.py, frozen with this file; paired item bootstrap B 2000 seed 11): **PASS iff U delta >= +0.03 AND paired CI low of U delta > 0 AND CE-unwarned rate delta <= +0.02** (CEu with the corrected labels of null-cal/tools/labels.py; rate = CEu count / 97). Otherwise NO.
- If both V and E pass stage 1, both run stage 2 and both verdicts are reported. No re-run to rescue a NO; no other quant or sampler is tried under this criterion.

## Judge
Haiku 5.5-low, judge.v1-low, N = 4 shards, both orders (identical answers reuse control judgments). 0 Opus, 0 paid. Spent before this freeze (onboarding smoke): 20.

## Budget
calls_cap: Haiku 800
(4 screens <= 4 x 100 + up to 2 stage-2 runs x 194.)

Format amendment (23:2x, after the V K0 generation and before any judge call): the heading "## Judge and budget" was split into "## Judge" and "## Budget", because the judge preflight (_lib/preflight.py) parses calls_cap only inside a "## Budget" block. Content, cap and decision rule are unchanged.
