# C2-REPLICA-FIDELITY criterion (round 7, ruler/hypotheses-round7-2026-10-21.json; frozen 2026-10-21 before any Opus call on N-D or N-S)

## Question
Does the desktop replica of RC1's default pipeline (S3 arm N-D: maintainer engine snapshot 5f8cc8f4 on the JVM, Qwen2.5-1.5B Q4_K_M,
Detailed, KB-only, 0.7 gate, native sampling, seed 42, mini llama-server b11010) reproduce the phone's A1 result (RC1 on the Pixel 8a,
Opus U floor-adj 0.143) under the same Opus judge? If yes, S3's attribution (persona dominant) is restated under Opus with N-S (same
pipeline, Succinct) as the stand-in for an RC run with Succinct. Cross-host by design (Pixel vs mini): label 'replica', never 'same-host'.

## Inputs (existing; 0 generation)
- N-D: traces/native-N-D-v01-s42.traces.jsonl (51/51 non-empty). N-S: traces/native-N-S-v01-s42.traces.jsonl (51/51 non-empty).
- Ids: cv5-51.ids = ruler/cv5-ladder/in/set.json ids = rc1-pixel/a1/in/v01-51.ids (checked set-equal). Dev set; no blind/, rnd/veil, v0.4.
- RC1 rows: rc1-pixel/a1/judgments/rc1-shipped.opus.judgments.jsonl (A1, 102 Opus judge.v1, both orders). Comparison rungs: CV5-LADDER-OPUS
  rows (1.5B closed-book L0, 1.7B K0 L1, Gemma E2B L2, 4B cut 7 Pixel L3), loaded exactly as rc1-pixel/tools/a1_analyze.py does.

## Judge (exactly as A1)
judge.v1 bytes (boar-eval harness/judge.mjs default opus), bench boar-eval/bench/v0.1 frozen refs, both orders, seed 7, --gap-ms 0,
N = 4 shards via arms/deepthink/tools/shard_judge.sh model opus, JUDGE_FLOOR_ERRORED=1 (tools/c2_judge.sh). New output files
judgments/native-N-{D,S}-v01-s42.opus.judgments.jsonl (the S3 Haiku files are untouched). Order: N-D first (102 calls); N-S (102)
only if N-D passes FIDELITY. DECLINE2STAGE stage 1 by the 0-call labels.is_decline stand-in, as A1.
calls_cap: Haiku 0 / Opus 210

## Analysis (tools/c2_analyze.py; estimator copied unchanged from a1_analyze.py)
s, r per item = mean of 3 dims over both orders; U = sum(s-1)/sum(r-1); raw = sum(s)/sum(r); U_D2S; win/tie/loss; per 100 correct
(corr >= 4) / CE (corr <= 1.5) / decline; item-cluster bootstrap B 2000, numpy default_rng(11), 2.5/97.5 pct, pairs on the same draws.
Per-item Spearman rho of s (N-D vs RC1), average ranks for ties. N-D output tokens p50 (runs/s3-gen.jsonl tokens_predicted) vs RC1's 384.

## Decision (frozen)
- INVALID if fewer than 49/51 non-empty N-D texts or any id lacks both orders.
- FIDELITY PASS iff |U(N-D) - U(RC1)| <= 0.05 AND Spearman rho(s) >= 0.6 AND the paired N-D - RC1 CI includes 0 (the hypothesis'
  kill clause). Else FIDELITY FAIL (= hypothesis KILLED: the page keeps 0.14 as 'one phone run, cause not reproduced off-device').
- Secondary flags (reported, not part of PASS): EQUIVALENT iff the paired CI lies inside [-0.05, +0.05]; CE-REPRODUCED iff N-D CE per
  100 >= 55 (RC1 68.6). The word 'equivalent' is used only under EQUIVALENT.
- Attribution (only if PASS; N-S judged): N-S - N-D on U floor-adj and raw with paired CI. PERSONA-CONFIRMED iff the U CI low > 0.
  Reported next to S3's Haiku raw +0.077 (+0.038...+0.120): 'consistent' iff the Opus raw CI contains +0.077. Also N-S - RC1 paired
  (Succinct stand-in vs the phone) and the per-100 CE / correct change N-S - N-D.

## Prediction
U(N-D) about 0.13-0.15 (Haiku floor-adj 0.129 vs Haiku's usual compression; same texts' style as RC1: 392 vs 384 tokens p50), |delta| <= 0.03,
CE per 100 about 60-70. Spearman is the risky clause: two independent samplings of a weak model on near-floor items; expected 0.4-0.7.
If PASS: N-S - N-D under Opus about +0.10 floor-adj (Opus spreads gaps more than Haiku), CI low > 0; CE per 100 drops by about 30.

## Known limits
One run each, one seed, n 51 dev; cross-host (phone app vs desktop harness, llama.cpp CPU embeddings vs his JNI build); the app routed
dng-005 to Succinct on the phone (the harness persona fallback decides on the desktop); is_decline stand-in for stage 1.
