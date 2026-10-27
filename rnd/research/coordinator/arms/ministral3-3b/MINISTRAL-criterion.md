# MINISTRAL3-3B criterion (frozen 2026-10-20 before any screen generation)

Question: does swapping the main 8 GB engine model Qwen3-1.7B Q4_K_M for mistralai/Ministral-3-3B-Instruct-2512 Q4_K_M (official GGUF, sha256
9ed150d4367e68df0ac8e1540f6ddc65b42d0ee26378329d1ecbca60f93fc5f8), everything else identical, reduce default-mode confident errors on the dev screens
without new false refusals? Onboarding (template, BOS, context, smoke, stage-0 speed) is in ONBOARDING.md; stage 0 projected Pixel 8a decode >= 6 tok/s
by the shortlist rule (12-16 tok/s x desktop tg ratio 0.541 = 6.5-8.7), so the screen runs.

## Candidates (patches relative to the lp-screens tree root, patch -p1; sha256 in the .sha256 files)
- **V** = `ministral3-3b.patch` (sha256 a85fd741486df577...): model swap + vendor sampling (card "temperature below 0.1": default T 0.1 in samplerFor,
  BOAR_SAMPLER_JSON {"top_k":0,"top_p":1,"min_p":0}; health items keep the engine's T 0). Arm name `min3v`.
- **E** = `ministral3-3b-engsamp.patch` (sha256 ade6b5600a2947ce...): model swap only, engine sampler 0.7/40/0.95/0.05 unchanged. Arm name `min3e`.
- Both keep the catalog sizeBytes at the 1.7B value so isCompactModel / declines / prompts / routing are byte-identical to the control.

## Stage 1 (screen): GATE v2, arms/null-cal/GATE-V2.md (commit 8c175580)
- Gate version: GATE-V2.md sha256 34ada53f1a9ab4ae..., tools/screen_gate_v2.py sha256 fa726fc0ac0b2380... (PARAMS K0: BAR_NET 10, MAX_FALSE_REF 2,
  MIN_UCOV_DELTA -0.059; K1: BAR_NET 9, MAX_FALSE_REF 4, MIN_UCOV_DELTA -0.071), tools/labels.py 0d93acec8dd575c5..., run_pool.sh e277d8c722e00c70...
- Screens: null-cal/pool/screen2-K0.ids (sha256 891b67e2..., 30 problems + 20 sentinels), screen2-K1.ids (2d45ca83..., 21 + 20). Controls null-cal/control/pool-K0.json, pool-K1.json.
- Runs (4): `OUT_BASE=arms/ministral3-3b/screen SCREEN_JSON=null-cal/pool/screen2-<K>.json CRITERION=<this file> bash null-cal/tools/run_pool.sh <min3v|min3e> <K0|K1> null-cal/pool/screen2-<K>.ids <patch>`;
  mini generation (gen1/gen2 slot lock), seed 42, Haiku 5.5-low judge.v1-low, N = 4, both orders; only answers that differ from the control are judged.
- Verdict per run = the gate line printed by screen_gate_v2.py (GO iff net >= bar and false refusals <= max and U_cov delta >= min). Reported per run as well:
  CE-unwarned count (control vs candidate), false refusals, U on covered items, answer tokens (median, mean) and wall time (mean totalMs ratio vs the control trace on the same items).
- Sanity (run void and repeated once if violated): traces n/n, 0 error rows, every trace's versions["model.sha256"] = 9ed150d4..., sampler temperature as specified (V 0.1 / E 0.7 on non-health items).

## Stage 2 (only if stage 1 GO on K0 AND projected Pixel decode >= 6 tok/s)
- Which variant: a variant with GO on K0 (K1 is reported, not required). If both V and E GO on K0, V runs (vendor = primary). At most one stage-2 run.
- Run: `CRITERION=<this file> bash lp-screens/tools/run_arm.sh <min3v|min3e> K0 main <patch>` (MAIN n 97 = main-97.ids sha256 9664d81f..., control lpctl-K0-main-s42).
- **PASS iff U delta >= +0.03 with paired bootstrap CI low > 0 (agg_run.py vs_control, B 2000 seed 11) AND CE-unwarned rate change <= +0.02** (labels.py over the 97),
  computed by tools/stage2_verdict.py (frozen with this file). Default-mode U (refused = 0) is reported, not gated.
- A PASS is a screening result for the coordinator (it does not adopt the model: phone speed/RSS on the Pixel 8a, stage 3, is unmeasured).

## Budget
calls_cap: Haiku 900 (4 screen runs <= 4 x 2 x 50 = 400; stage 2 <= 194; reserve for one sanity re-run). Spent before this freeze: 20 (two 5-item smokes). 0 Opus, 0 paid APIs.
