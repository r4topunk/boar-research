# DEEPCOVER: does asking the deep thinking tier to enumerate the key facts in its reasoning and state them in 120–200 words raise completeness without losing correctness? (frozen 2026-10-11 13:1x, loop coordinator)

## Tags
Tags: none

## Question
Arm **C** = H (dt512: cut 6 + DEEPTHINK + DT512; Qwen3.6-35B-A3B UD-Q2_K_XL, thinking 512, succinct persona, ctx 400, k 6) + the DEEPCOVER patch with `settings.deepCover = true`: on the deep thinking generation only, the system message gains one instruction after the persona — "Before answering, list in your reasoning the 5–8 key facts, figures or steps a complete answer needs. Then answer in 120–200 words that state each of them explicitly, in plain prose." — and the output cap is 300 tokens (DEEP_COVER_MAX_TOKENS) instead of 200. Fast tier, health extractive path, multipass and the no-deep-model fallback are untouched; default-off is byte-identical to dt512 (differential 6/6, unit tests). Does it move the deep tier on v0.2 (direction) and V-para (confirmation)?
Mechanism evidence: LOSSMAP (10-11): the *thin* axis co-fires on 49–52 % of H's items (thin ∧ ¬wrong = 39 % / 46 % of the loss, an upper bound); LENGTHSHARE: ≈ 17 % of H's gap is reference length; completeness 0.30 / usefulness 0.34 are the dimensions carrying the gap. Risk: correctness loss from asserting facts the model does not hold (COMPLETE on the 4B: −0.80 correctness; the 35B with thinking is the stronger reader).
reopen: DEEPFULL closed the long persona ("detailed", cap 200 → truncated; −0.066 / −0.013 at the slice). This is not a persona or length change: it asks for an explicit key-point enumeration in the reasoning and a bounded answer under a cap that does not truncate.

## Fixed inputs
- Tree on the mini `<runner>/kiln/be-0cfd4a77-deepcover` = dt512 tree + `arms/deepcover/deepcover.vs-dt512.patch` (sha 180adac4…; content hash f94c11f4…); adapter unchanged (7a0282ae); runner `deepcover-remote-run.sh` (sha checks; refuses requests without deepCover true).
- Control **H** = dt512 rows: v0.2 Haiku `dhv-H-v02-s42`, Opus `L2-H-1seed`; V-para Opus s42/s43. K = cut 6 for the ladder.
- Requests = H's with `config.arm` deepcover and `settings.deepCover = true`.

## Power
expected_delta: +0.02…+0.04 raw on v0.2 (source: completeness 0.30 → 0.40 would be ≈ +0.03 raw; the thin ∧ ¬wrong bucket bounds the gain at 0.39–0.46 of the loss; DEEPFULL's −0.013 at ctx 1200 + cap 400 is the floor for a longer answer that does not truncate)
n: 110 (v0.2, s42) for direction; 51 × 2 seeds (V-para) for confirmation
seeds: 1 on v0.2; 2 on V-para
mde: v0.2 one seed ≈ 0.025 raw; V-para two seeds ≈ 0.03
slice: random20-v02.ids (sha a3e43672…)
l1_futility: stop only if Haiku delta <= 0 AND h2h <= control; any Haiku delta > 0 -> Opus N=4 on the same 20 ids
reopen: see Question

## Stages and rules
1. Smoke (3 v0.1 deep non-health items: vit-hum-001, lan-exp-001 = H's smoke items, lan-cmp-004): 3/3 `generate:deep-thinking` and `deepcover:on`, 0 errors, 1 ≤ reasoning ≤ 522, outputTokens ≤ 300 on 3/3, answers 90–230 words on ≥ 2/3 (cap hit on ≤ 1/3); record ttft / total vs H's smoke (61 / 67 s and 83 / 93 s). Else FAIL-INFRA (fix and rerun the smoke only). Correctness is not judged at the smoke.
2. L1 slice random20-v02 s42 (Haiku N=4) vs H's Haiku rows; rules above + the near-miss rule; **extra stop: correctness ratio on the slice < H's − 0.05 (Haiku) → NO (correctness clause)**.
3. v0.2 full 110 s42: Haiku vs H → Opus N=4 (220) vs L2-H-1seed: direction; the correctness clause applies with Opus.
4. V-para s42 + s43 (Opus N=4, 204) vs H two seeds (`paired.mjs --common-mode 0.020,0.025`).
Verdict: **LEVER** (V-para two-seed Δ ≥ +0.03, CI low > 0, correctness not below H − 0.03) / **SMALL** / **NO**; "not decided at MDE" when |Δ| < 0.03 with the CI through 0. One generation per seed and stage.

## Stop rules and budget
Mini: disk ≥ 25 GiB, heavy lock, one MoE server, detector untouched; smoke ≤ 15 min, slice ≤ 1 h, v0.2 full ≤ 4.5 h (longer answers), V-para ≤ 3 h per seed. Judge calls only from Mon 2026-10-12: Haiku ≤ 40 + 220 (+ 40); Opus ≤ 40 + 220 + 204. Mini order: VITALPACK-ADD's slice first (frozen earlier), then this arm.

## Outputs and exposure
`arms/deepcover/DEEPCOVER.md`, `aggregates/`, blind traces/judgments under `blind/<set>/runs-deepcover/`. One EXPOSURES row per set and stage.
