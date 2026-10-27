# DG-SA criterion (FROZEN 2026-10-21 22:xx, before any SA generation; parent DG-criterion.md sha 92d3340a, unchanged)

Question: does putting the model's own SELECT pick FIRST in the normal multi-source prompt (augmenter) beat the same-host K1 control, where the replacer arms (S/SB/SC) were NO-GO because the one-chunk context made the 1.7B stop citing (`[n]`) and the engine's grounding layer released the answers as warned/refused?

## Arm SA (fixed)
- Same as arm S in everything (select grammar, menu = raw candidates cap 12 by score, <= 3 sentences per chunk, NO_EVIDENCE alternative, seed 42, -t 4, llama-server b11010, Qwen3-1.7B Q4_K_M, reasoning off / enable_thinking false, default repack, LITEDECLINE_OFF=5, tree be-0cfd4a77-cut7-litepacks, sampler 0.7/40/0.95/0.05, -np 1) EXCEPT the source rewrite in the answer.ts hook:
  `sources = pick ? [pick, ...sources.filter(c => c.chunkId !== pick.chunkId)] : sources`
  i.e. the selected chunk becomes source [1], the engine's other kept sources follow unchanged and in order; NO_EVIDENCE leaves the engine's sources untouched (no closed-book fallback in SA; the SELECT result is only a reordering/promotion, and a pick from the keep-dropped list adds that chunk to the context).
- Patch: `tools/dg-sa.patch` = `tools/dg.patch` (sha c81ba53106c16d49…, unchanged, S/SB/SC/C1 behaviour untouched) + 5 changed lines (arm list x3, `augment: DG_ARM === "SA"`, the sources line). sha256 of dg-sa.patch: 439fce743f9b39f1a165572268735e3ce6176f84368a0e30f278a459fccfc090. `tools/run_dg.sh` gained arm SA and env DG_PATCH (default dg.patch).
- Validity check before judging: the SA patch with DG_ARM=S on the 5 smoke ids gives byte-identical answers to the stored S smoke traces (S behaviour unchanged); deterministic layers byte-identical to the control (0 tolerance, sanity_dg.py).

## Gate (stage 1, same as DG-STAGE1)
- Screen = null-cal/pool/screen2-K1.ids (41 ids = 21 problems + 20 sentinels, sha 2d45ca83…), control = null-cal/control/pool-K1.json, `null-cal/tools/screen_gate_v2.py` with its K1 params: GO iff net >= 9, false refusals <= 4 of 20, U_cov delta >= -0.071.
- Judge: Haiku 5.5-low judge.v1, N 4 shards, both orders, only answers whose text differs from the control (identical texts reuse the control's rows). Preflight without CRITERION (no calls_cap line; cap tracked in runs/logs/CALLS.md).
- Kill before judging (DG-criterion rule 4): > 5 % empty or repetition-loop answers; mean totalMs > 4x control; any deterministic-layer diff.
- Stage 2 (SA GO only): MAIN 97 paired DeltaU vs the mini K1 baseline, item bootstrap B 2000 seed 11, CE-unwarned counts, splits by fact-in-pack.ids (47 ids) and S1; PASS-SCREEN iff DeltaU >= +0.02 with CI low > -0.01 (DG-criterion rule 2); that unlocks an Opus confirm launched by the coordinator (not run here).
- Caps: Haiku <= 150 for this variant (running total in runs/logs/CALLS.md, overall cap 700, now 232), Opus 0, paid 0, phone 0. Dev items only, no blind / rnd/veil / bench v0.4.
- Reported, no rule: changed answers, NO_EVIDENCE count and agreement with the S1 label, picks from keep-dropped, citation rate vs control on the items the control cited (screen 41 and MAIN 97), mean output tokens, totalMs ratio, warned answers.

## Prediction (written before any SA run)
Net 6-9 (around the null to just at the 9 bar): the prompt stays multi-source, so the S failure (lost citations -> warned release) should disappear; the possible gain comes from promoted/added picks. False refusals <= 3 of 20 because citations are preserved. U_cov delta inside the margin (>= -0.071). The honest expectation is a small effect: a promoted source [1] mostly changes which chunk the 1.7B leans on, which is 1 of the 4-6 chunks it already sees, so NO-GO at net 6-8 is the modal outcome.
