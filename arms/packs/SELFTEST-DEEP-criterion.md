# SELFTEST-DEEP: deep tier H on the 9 public pack self-tests, with vs without the pack (frozen 2026-10-13, measurement, no verdict rule)

## Tags
Tags: none

## Question
How much does each published pack lift the recommended deep tier H (cut 6 + Qwen3.6-35B-A3B UD-Q2_K_XL + thinking 512 = dt512) on its own 20 public self-test items, and how does H-with-pack compare with the 4B claim build with the pack (SELFTEST-SCORES.md)? Used for the cards' "Quality (self-test)" lines only.

## Fixed inputs
- Arm **H**: mini tree be-0cfd4a77-dt512 (patch 3f355999…, dt512 patch f9a1979b…, adapter 7a0282ae…), settings {"quickFirst":true,"alwaysComplete":true,"deepModelId":"qwen3.6-35b-a3b-ud-q2kxl"}, seed 42, noplaces, runner stdeep-remote-run.sh (= dt512-remote-run.sh + BOAR_EVAL_PACK_DIRS).
- With pack = claim kit (boar-crypto, boar-wikivoyage-en) + the pack; without = claim kit. Requests = the 4B self-test requests rewritten by arm.sh mkreq (runId st-<pack>-dt512[-nopack]-s42).
- Reference: 4B with-pack rows st-<pack>-cut7-s42 (Haiku 5.5-low). Public self-tests only, no blind or held-out data.

## Power
expected_delta: 0.03 (source: SELFTEST-SCORES.md 4B pooled with-vs-without +0.032; DEEPNORAG packs on the deep tier ~+0.045)
n: 180 pooled (20 per pack)
seeds: 1
mde: ~0.02 pooled raw (4B pooled CI half-width 0.017); per pack ~0.05 (descriptive only)
slice: none (full 180; measurement)
l1_futility: none (Haiku is the only judge; measurement, no verdict)
split: per pack (declared: the 9 packs)

## Stages and rules
1. Smoke: 2 items with pack (deep-thinking fired, non-empty answers, pack passages in kept). Infra only.
2. 18 runs × 20, sequential on the mini. Gen checks: errors 0, non-empty, deep-thinking on all.
3. Haiku 5.5-low N=4 both orders per set; floor_metrics raw / above_min + CI; paired Δ per pack and pooled (per-item bootstrap, B 2000, seed 11). No verdict rule; numbers reported as measured.
