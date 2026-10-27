# LITE7 v2: DIRECTION-POSITIVE by the frozen rule, read as flat: Δ(ON − OFF) random20 +0.016 (−0.035…+0.066), thin bucket +0.007 (6 up / 5 down); the "3-4 sentences + each figure" swap lengthens the 1.7B (words p50 34.5 → 46) without moving the judge (2026-10-16 01:4x; Haiku 40, Opus 0, 0 paid). v1 stopped at its 0-call gate (G3 trailing-citation artefact), kept below.
TL;DR (v1): by the v1 frozen rule the arm stopped before any judge call. 7 of 8 gates pass. G3 fails 5 vs ≤ 2. All 5 "ends-open" answers end in a complete sentence followed by a citation, ". [n]". The lite3 ends-open rule counts the final "]" as open. There are 0 length-cap hits (output tokens max 114) and 0 truncations. Excluding a trailing "[n]", ends-open is 0. Not a model failure, but the gate was frozen as written, so there is no Δ. A re-freeze (v2, same runs reused) is the coordinator's call.

## v2 (coordinator ruling; criterion `LITE7-criterion-v2.md` sha `6bf666ab…95e0`, frozen before any judge call)
- Change: G3 ignores one trailing "[n]" after sentence punctuation. The 180 ON traces from v1 are reused unchanged. Smoke re-scored for v2: PASS (v1 verdict kept as smoke.verdict.v1.json).
- Gate under v2 (aggregates/gate7-v2.json): **PASS 8/8**, G3 ends-open 0 / 0, cap hits 0; all other rows as in the v1 table below.
- Haiku 5.5-low N=4, both orders, random20 seed 616, 40 calls (9 per-pack preflights OK, spent 40 / cap 40, 0 failures, 98 s). OFF = the LITE5-180 ON rows on the same ids. Estimator l2_agg (B 2000, seed 11).

| comparison (random20) | ratio a / b | Δ raw (CI) | b/w |
|---|---|---|---|
| **ON − OFF** | 0.506 / 0.491 | **+0.016 (−0.035…+0.066)** | 9 / 7 |
| ON − OFF, 16 changed answers | – | +0.008 (−0.052…+0.074) | 7 / 7 |
| ON − 4B X2b | 0.506 / 0.577 | −0.070 (−0.117…−0.023) | 6 / 13 |
| OFF − 4B X2b | 0.491 / 0.577 | −0.086 (−0.133…−0.040) | 4 / 15 |
- Per bucket (mean per-item ratio, declared split): **thin (12) 0.551 → 0.558, +0.007** (6 up / 1 same / 5 down). Rest (8) 0.401 → 0.443, +0.042, but 4 of the 8 are byte-identical deterministic answers that drift +0.057 mean (medlineplus-006 +0.18), which is pure judge noise. So most of the pooled +0.016 is noise on unchanged items. Changed-only, the Δ is +0.008.
- Biggest moves: simplewiki-014 +0.20, travel-005 (not_read) +0.32, travel-009 +0.11; outdoors-015 −0.16, ethereum-015 −0.17, travel-004 (big_error) −0.13, health-se-016 −0.09.
- Length / hedging on the 20: words p50 31 → 44.5, > 2 sentences 2 → 15, hedged 0 → 1; LLM p50 total 6.48 → 6.31 s, ttft 5.45 → 4.66 s (cross-run host noise; prompt +10 tokens, output p50 +16 tokens on the 152).
- **Verdict (frozen rule): DIRECTION-POSITIVE** (Δ > 0 and thin mean up). It does **not** meet the 180 licence (Δ ≥ +0.03 and CI low > 0). Read: the 1.7B now writes at the 4B's length, but the extra sentences do not carry the missing facts; thin moves +0.007. LITE6's "thin" is not a length problem on this model. Next candidates are fact selection (not_read, e.g. a "key fact first" line) or the deep/4B tier. A longer style line is not worth a 360-call run.

## v1 (kept for the record)
v1 title: LITE7: STOPPED at the 0-call gate (G3 ends-open 5 vs OFF 0, cap OFF + 2): the lite-only "3-4 sentences + each figure" style swap lengthens the 1.7B as planned (> 2 sentences 0.17 → 0.70, words p50 34.5 → 46) but G3 fails on a trailing-citation artefact; 0 Haiku (2026-10-16 01:39; Haiku 0, Opus 0, 0 paid)

## Frozen inputs
- Criterion `LITE7-criterion.md` sha `5c9b0852…2e91` (Ruleset 30), frozen before the 180 run and before any judge call. smoke.verdict.json PASS for this sha (4 LLM ON smoke traces, mean prompt 829.5 ≤ budget 834.5, identity PASS, marker lite:style 4/4, projected 0.29 h). crit_check rc 0.
- Patch `tools/lite7.patch` sha `6ef9c0db…0653` (diff vs the X2b tree: src/routing/answer.ts deps.liteStyle + 4 constants + reason code `lite:style`; be/adapter-lite5.ts → be/adapter-lite7.ts + the `LITE_STYLE=1` line, sha 9da2d01a…). Tree kiln-local/be-0cfd4a77-cut7-lite7 (X2b tree copy, ARM cut7+lite7, node_modules symlinked, 17 MB). tsc clean, src/routing vitest 603/603 on a scratch copy of wt/cut7 + this src (runs/tsc.txt, runs/vitest-routing.txt).
- Lines (lite model, non-health only): system "…2-3 short, direct sentences or a brief paragraph, no preamble." → "Answer in 3-4 short, direct sentences, no preamble."; reminder "Keep it short: 2-3 sentences." → "Use 3-4 short sentences; include each specific figure, name or step the passages give for what was asked." The X2b append budget is still measured on the house lines, so the kept lists equal OFF's.
- Smoke (5 items, ON + OFF): OFF with the switch unset = LITE5-180 ON traces 5/5 (answer text, promptTokens, kept); the ON/OFF prompt dumps differ only in the 2 style lines; prompt growth **+10 tokens** (limit +15).
- OFF = LITE5-180 ON (1.7B + X2b) traces, reused. ON = 180 regenerated on the MacBook (seed 42, --reasoning off, per pack, 26 min, 0 busy-wait).

## 0-call gate (tools/gate7.py, 180; aggregates/gate7.json): FAIL
| gate | OFF | ON | rule | pass |
|---|---|---|---|---|
| G0 infra | – | 0 errors / empty / reasoning / `<think>` | all 0 | yes |
| G1 > 2 sentences (of 180) | 0.167 | **0.700** | ≥ 0.45 | yes |
| G2 words p50 (180) | 34.5 | **46** | 42–60 | yes |
| G3 ends-open / cap hits | 0 / – | **5** / 0 | ≤ OFF + 2 and 0 | **no** |
| G4 hedged (152 LLM, LITE4 regex) | 1 | 3 | ≤ OFF + 2 | yes |
| G5 deterministic byte-identical; lite:style 152 LLM / 0 det | – | 28/28; 152 / 0 | all | yes |
| G6 prompt tokens p50 (152 LLM) / max growth | 876 | 886 / +10 | ≤ +15 | yes |
| G7 kept + headpass codes = OFF | – | 180/180 | ≥ 178 | yes |
- G3 ids: medlineplus-en-004, -009, bitcoin-se-012, ethereum-se-013, health-se-007. Each is a whole sentence ending ". [n]". The new length invites one more citation after the period; the house style never produced it (OFF 0).
- Length / cost (152 LLM items): sentences p50 2 → 3; output tokens p50 46 → 62 (max 76 → 114); answers changed 150/152; p50 total 6.36 → 7.40 s, ttft 4.90 → 5.99 s (desktop, cross-run; the prompt grew only +10 tokens, so part of the ttft shift is run-to-run host noise).

## Verdict
**STOPPED (0-call gate FAIL, G3) → no Δ, Haiku 0.** The mechanism does what LITE6 planned: on every length gate it now sits at the 4B's profile (4B: 0.556 / 52 words). Whether the judge pays for that length is still unmeasured, and so is LITE6's big_error risk. Option (not taken: a new freeze is not this agent's call): **LITE7 v2** = the same patch and the same 180 traces, with G3 re-stated as "ends-open after stripping a trailing [n] citation" (here 0, from aggregates/lite7.json, descriptive). Then random20 seed 616 Haiku 40 vs the LITE5-180 ON rows. (Taken as v2 above.)

UNKNOWN: whether the 5 trailing citations change the judge's view (likely not, they are cited sentences); the ttft delta's split between +16 output tokens and host noise; phone cost of ≈ +16 output tokens (≤ +2 s at ≥ 8 tok/s decode, assumed).

## Files
`LITE7-criterion.md` + `LITE7-criterion-v2.md` (+ .sha256s), `smoke.verdict.json` (v2) + `smoke.verdict.v1.json`, `arm-st-L7.conf`, `arm-st-L7-v2.conf`; `tools/{lite7.patch(.sha256), mkreq_lite7.py, run_lite7_gen.sh, gen_lite7.sh, gate7.py, smoke_check.py, judge_lite7.sh, agg_lite7.py}`; `runs/smoke/` (5-item ON/OFF traces + prompt dumps + smoke-check.json), `runs/180/` (9 ON requests + traces + logs, gen_lite7.log), `runs/{tsc,vitest-routing}.txt`; `aggregates/{gate7.json (v1 FAIL), gate7-v2.json, checkpoint7.json, lite7.json (v1 stop), lite7-v2.json}`; judgments `runs/180/lite7-r20-on-*.judgments.haiku55-low.jsonl` (40 rows), judge_lite7.log. Public self-tests only; blind/ and rnd/veil/ were not read, so there is no EXPOSURES row. No llama-server left running (the :8094 detector was untouched). MacBook free 6 GiB.
