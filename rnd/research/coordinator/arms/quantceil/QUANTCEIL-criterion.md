# QUANTCEIL: how much knowledge does the 2-bit quant cost the deep thinking tier? UD-IQ3_XXS vs UD-Q2_K_XL, same configuration (frozen 2026-10-12 00:4x, loop coordinator)

## Tags
Tags: none

## Question
Arm **Q** = the recommended configuration H (dt512 tree unchanged: cut 6 + DEEPTHINK + DT512; thinking 512, succinct, ctx 400, k 6, engine sampling) with the deep model swapped from `Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf` (12.29 GB, ≈ 2.6 bpw) to `Qwen3.6-35B-A3B-UD-IQ3_XXS.gguf` (13.2 GB, ≈ 3.1 bpw; same HF repo `unsloth/Qwen3.6-35B-A3B-GGUF` @ a483e9e6cb; sha256 recorded in MODELS.md after download). Does the higher-precision quant move the deep tier on v0.2 (direction) and V-para (confirmation)?
Mechanism evidence: LOSSMAP (10-11): *wrong fact* is 0.40 of H's V-para loss (26/51 items) and 0.21 on v0.2; the deep tier's whole gain over the 4B sat in that bucket, and a 2-bit quant is the usual suspect for recalled-but-wrong facts (numbers, names, dates). Never measured (CLOSED.md has no row; HANDOFF §2 listed a KLD screen only). Choice of quant: UD-Q3_K_XL (16.8 GB) exceeds the mini's 16 GB RAM and the 12 GB device budget; IQ3_XXS fits the disk floor (27 + 12.3 − 13.2 = 26 GiB ≥ 25) and is the smallest 3-bit step. Device caveat: 13.2 GB still exceeds a 12 GB phone's RAM; a device plan would need bmoe expert paging (deep/RESUME.md); this arm measures the knowledge ceiling of the quant, not a shippable build.
reopen: n/a (never measured).

## Fixed inputs
- Tree `<runner>/kiln/be-0cfd4a77-dt512` unchanged (ARM dt512); the arm is identified by `config.settings.deepModelId = "qwen3.6-35b-a3b-ud-iq3xxs"` and the run prefix `qc-Q`. Adapter: boar-eval with a new catalog entry for that id (file + sha256 + sizeBytes; `--backend server`), deployed to the dt512 tree's be-repo; runner `quantceil-remote-run.sh` = dt512 runner with `--deep-model qwen3.6-35b-a3b-ud-iq3xxs` and the new adapter sha.
- Requests = H's (kit crypto + wikivoyage, places kit-vexact on V-para, noplaces on v0.2, seeds 42/43) with the deepModelId swapped.
- Control **H** = dt512 rows (v0.2: Haiku slice rows, Opus L2-H-1seed; V-para: Opus s42/s43). TV = labelled Haiku full-110 twin if a full Haiku screen is wanted.

## Power
expected_delta: +0.02…+0.05 raw on V-para (source: LOSSMAP wrong bucket 0.40 of the loss at mean ratio 0.46 on those 26 items; recovering a quarter of that bucket ≈ +0.03; the MoE screens put the closed-book plateau of three 2-bit MoEs within ±0.02, so the quant, not the family, is the untested axis)
n: 110 (v0.2, s42) for direction; 51 × 2 seeds (V-para) for confirmation
seeds: 1 on v0.2; 2 on V-para
mde: v0.2 one seed ≈ 0.025 raw; V-para two seeds ≈ 0.03 (expected ≈ mde: a LEVER needs the full two-seed stage)
slice: random20-v02.ids (sha a3e43672…)
l1_futility: stop only if Haiku delta <= 0 AND h2h <= control; any Haiku delta > 0 -> Opus N=4 on the same 20 ids
reopen: n/a

## Stages and rules
1. Smoke (H's smoke items vit-hum-001, lan-exp-001 + lan-cmp-004; all deep non-health): model resolves (sha), 3/3 `generate:deep-thinking`, 0 errors, 1 ≤ reasoning ≤ 522, non-empty answers; **record load time, peak RSS, decode tok/s and total time vs H's smoke (RSS 7.5 GB, 61–83 s ttft)**: FAIL-INFRA if RSS > 12 GB, swap > 8 GB, or p50 total > 3× H's (the IQ3 CPU kernels are slower; a slower-but-smarter result still informs the device plan, so the time clause is a stop only above 3×).
2. L1 slice random20-v02 s42 (Haiku N=4, 40) vs H's Haiku slice rows; rules above + near-miss rule.
3. v0.2 full 110 s42: Opus N=4 (220) vs L2-H-1seed (no Haiku full control for H exists; TV optional): direction = CONTINUE if Δ > 0 or CI low > −0.01.
4. V-para s42 + s43 (Opus 204) vs H two seeds (`paired.mjs --common-mode 0.020,0.025`).
Verdict: **LEVER** (V-para two-seed Δ ≥ +0.03, CI low > 0) / **SMALL** / **NO**; "not decided at MDE" when |Δ| < 0.03 with the CI through 0. Timing reported alongside, never gated below 3×. One generation per seed and stage.

## Stop rules and budget
Mini: disk ≥ 25 GiB after the download (Q2 deleted 00:40; MODELS.md keeps its sha and URL for re-download), RSS ≤ 12 GB, swap ≤ 8 GB, heavy lock, one MoE server, detector untouched; smoke ≤ 20 min, slice ≤ 1.5 h, v0.2 full ≤ 6 h, V-para ≤ 4 h per seed. Judge: Haiku ≤ 40 (+ 40); Opus ≤ 40 + 220 + 204 (week cap 600; 80 used).

## Outputs and exposure
`arms/quantceil/QUANTCEIL.md`, `aggregates/`, blind traces/judgments under `blind/<set>/runs-quantceil/`. One EXPOSURES row per set and stage; MODELS.md + DISK-LOG rows for the swap.
