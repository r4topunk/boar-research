# VITAL-ONOFF-DEV (2026-10-23): wiki-vital5 on vs off in the app maintainer's native pipeline, 1.5B Detailed, 51 dev ids

TL;DR: **NEUTRAL by the frozen rule.** Pack on minus pack off = **+0.026 raw (+0.001…+0.051)**, floor-adj +0.031 (−0.001…+0.064), better/worse 16/9 of 32 divergent items. The CI clears 0 by a hair, but one health item becomes a new confident error (lan-hlt-001: kept "Healthy diet", correctness 3.0 → 1.5), so the GAIN clause fails. Do not call the pack a "gain" toward the app maintainer. One seed, Haiku, dev ids.

## Criterion
VITAL-ONOFF-criterion.md, sha256 583a6a4d0a4ae701d862c47fdb30dc33de08bfbf191d8975f3425254c0653bb8, frozen (read-only) before any generation or judge call.

## Commands
- Harness (MacBook, 0 LLM): embed + tokenizer llama-server b11010 on 8181/8182 as tools/run.sh; then `native-parity-harness --questions work/questions-cv5-51.jsonl ... --label kbvital5 --packs work/dl/wiki-vital5.sqlite --cutoffs 0.7 --personas detailed --out work/out/vo-kbvital5-15b.jsonl` (default --model-bytes = 1.5B, small-model texts). Prompts → work/vo-prompts.jsonl (kept titles per item).
- Generation (mini, kiln lock mini-long held): llama-server b11010 CPU `-c 4096 -t 2 -np 1 --port 8197`, Qwen2.5-1.5B Q4_K_M sha 1adf0b11, `python3 -I s3_gen.py vo-prompts.jsonl vo-gen.jsonl 8197` (tools/s3_gen.py unchanged: native Sampling defaults, seed 42). Copy in runs/vo-gen.jsonl.
- Judge: `bash tools/vo_judge.sh` (divergence vs runs/s3-gen.jsonl N-D → runs/vo-divergent.ids; traces/native-N-DV-v01-s42.traces.jsonl; preflight OK; shard_judge.sh Haiku 5.5-low judge.v1-low N 4 both orders → judgments/native-N-DV-v01-s42.judgments.jsonl).
- Aggregate: `python3 -I tools/vo_agg.py` → aggregates/vital-onoff.json.

## Results (51 CV5 ids; non-divergent ids inherit the N-D rows)
| | N-D (kb only, step 3) | N-DV (kb + wiki-vital5) |
|---|---|---|
| ≥ 1 source kept | 1/51 | 32/51 |
| prompt tokens p50 | 276 | 458 |
| raw (CI) | 0.312 (0.288–0.339) | 0.338 (0.307–0.373) |
| floor-adj (CI) | 0.129 (0.098–0.163) | 0.161 (0.121–0.206) |
| win/tie/loss vs reference | 0/0/51 | 0/0/51 |
| output tokens p50 / at cap | 392 / 0 | 392 / 0 |
| confident errors per 100 (LITEPACKS rule) | 66.7 (34) | 64.7 (33) |
- Divergent items: **32** = exactly the 32 kept-source items; the 19 identical prompts gave byte-identical answers on the mini (determinism check). Haiku calls 64 (cap 110), Opus 0, paid 0.
- Paired N-DV − N-D: all 51 +0.026 (+0.001…+0.051); divergent 32 only +0.041 (+0.002…+0.080).
- Health items (4, all keep vital chunks): lan-hlt-001 new CE (s 2.33 → 1.83); vit-hlt-003 leaves CE (1.17 → 1.83); lan-hlt-002 / -003 not CE either side.
- Predictions vs outcome: kept-on 32 (predicted 32, hit); divergent 32 (32 ± 3, hit); sign positive (hit), size +0.026 inside the predicted +0.00…+0.04, but the CI did not straddle 0 as predicted (low +0.001).

## Verdict: NEUTRAL
CI low > 0, but a new confident error on a health item (lan-hlt-001) → not GAIN under the rule; CI high > 0 → not HARM.

## Maintainer-note sentence
"On 51 of our dev questions with your RC1 default (1.5B, Detailed), adding wiki-vital5 keeps a source on 32 questions instead of 1 and moves the judged score by +0.026 (CI +0.001…+0.051, one seed, Haiku judge): a small edge, not a clear gain, and one health answer became confidently wrong with a Vital passage in context, so we would not present Vital as a quality gain yet."

## Caveats
- 1.5B (his RC1 model), not the 1.7B main engine; his pipeline through our desktop harness (device parity bounds the drift) + mini CPU generation.
- One seed (42); Haiku 5.5-low compresses gaps; dev ids (CV5 51 of v0.1), not v0.4; n 51, CI low at +0.001 is fragile.
- CE rule borrowed from LITEPACKS (step 3 had none); CE counts are Haiku-judged, ≈ 2/3 of answers in both arms.
- The PR #86 issue (Vital keyword hits bypass the 0.70 gate and outrank personal files) is not measured here: no personal files in this set.
