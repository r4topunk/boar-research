# QUANTCEIL — UD-IQ3_XXS (13.2 GB) vs UD-Q2_K_XL (12.3 GB) as the deep thinking tier's model, same dt512 configuration (2026-10-12; criterion `QUANTCEIL-criterion.md` sha 0c4a8896…, addendum 1 = pre-declared bucket read-out)

**Verdict: NO — not detected at MDE 0.03 (V-para, 51 ids, two seeds, Opus).** Two-seed V-para: Q raw **0.557 (0.526–0.585)**, floor-adj **0.441 (0.403–0.477)** vs H 0.553 / 0.436; paired Δ **+0.004 (−0.024…+0.033)** item-bootstrap, wider with the common-mode run term (σ_run 0.020); seeds split: s42 +0.030 (0.000…+0.062), s43 −0.022 (−0.055…+0.008); h2h 22/9/20 and 20/11/20; wins 0/51 both. v0.2 (110, s42, Opus): Q 0.616 / 0.519 vs H 0.608 / 0.508, Δ +0.008 (−0.010…+0.028). The 3-bit quant does not move the deep tier at the bounty bar; a gain ≥ +0.03 raw is excluded on both sets.

**Mechanism: confirmed on v0.2, not on V-para.** Pre-declared split by LOSSMAP bucket of H: v0.2 *wrong* items +0.087 (+0.035…+0.150, n 23), *absent* −0.013, hedged 0.000 → the 3-bit quant repairs recalled-but-wrong facts and loses a little elsewhere (flips), net ≈ 0. V-para pooled two seeds: *wrong* +0.018 (−0.015…+0.053, n 26), *absent* −0.009; s42 *wrong* +0.079, s43 *wrong* −0.014. The per-seed swing on V-para (r 0.5–0.7, SEEDVAR) is larger than the quant effect.

| stage | set | n | judge | Q | H | Δ (CI) | h2h | cost |
|---|---|---|---|---|---|---|---|---|
| smoke | v0.1 | 3 | — | PASS: RSS 7.6–7.7 GB (= Q2), swap 1.2 GB, load 16.6 s, decode 7.6–9.6 tok/s (Q2 ≈ 12), total ×1.3–1.4 | | | | mini 6 min |
| slice random20-v02 | v0.2 | 20 | Haiku N=4 | 0.602 | 0.571 | +0.032 (−0.004…+0.074) | 8/7/5 | 40 Haiku |
| same ids | v0.2 | 20 | Opus N=4 | 0.673 | 0.649 | +0.024 (−0.015…+0.065) | 10/4/6 | 40 Opus |
| full s42 | v0.2 | 110 | Opus N=4 | 0.616 / fa 0.519 | 0.608 / 0.508 | +0.008 (−0.010…+0.028) | 41/32/37 | 220 Opus |
| s42 | V-para | 51 | Opus N=4 | 0.563 / fa 0.449 | 0.533 / 0.412 | +0.030 (0.000…+0.062) | 22/9/20 | 102 Opus |
| s43 | V-para | 51 | Opus N=4 | 0.550 | 0.572 | −0.022 (−0.055…+0.008) | 20/11/20 | 102 Opus |
| **two seeds** | V-para | 51 | Opus | **0.557 (0.526–0.585) / fa 0.441** | 0.553 / 0.436 | **+0.004 (−0.024…+0.033)** | — | — |
Ladder V-para floor-adj (two seeds): K 0.261 → H 0.436 → Q 0.441; bar 0.50; win-rate 0 everywhere.

Costs: IQ3 CPU kernels ≈ ×1.35 wall on the mini (decode ×0.7, prefill similar); RSS unchanged. Device: 13.2 GB still exceeds a 12 GB phone without expert paging; no reason to prefer it.
Reading for the backlog (LOOP-PROGRAM §5.6 direction check): the deep tier's remaining loss is not a precision artefact of the 2-bit quant; model-knowledge levers available on this hardware are exhausted (quant: this arm; family: MoE screens; thinking: DT512 curve). With kit-content levers closed this cycle too (VITALADD, NOTES35), the honest state stands: formal raw rule met by H, floor-adjusted V-para target (0.50) not reachable with any measured lever on ≤ 12 GB. Next: SYNTHDEEP (B7, comparison cells: compare task ratio 0.47, 4/7 primary *wrong*) — a task-specific prompt/pinning lever; and the parked powered tests only if budget is idle.
Method: dt512 tree unchanged; `be-repo-quantceil/` = boar-eval 16c4493 runner files (adapter catalog entry `qwen3.6-35b-a3b-ud-iq3xxs`, sha 9c964e65…) beside the mini's own protocol.ts; runner `quantceil-remote-run.sh`; requests = H's with the deepModelId swapped; places kit-vexact on V-para. The v0.2 full run had light concurrent load (timing contaminated; quality unaffected, seeded). Exposure: v0.2 smoke 3 + slice 20 + full 110 generations, Haiku 40, Opus 40 + 220; V-para 58 × 2 generations, Opus 204. Literature: `LIT-QUANTCEIL.md` (side session, 11 sources).
