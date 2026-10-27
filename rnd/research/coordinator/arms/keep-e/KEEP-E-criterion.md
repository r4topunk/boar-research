# KEEP-E criterion (frozen 2026-10-21 before any replay, generation or judge call of this arm)

## Question
KEEP-K1 found that on 17/100 MAIN rows the lexical retrieve() list is empty, so the X2b head-pass/dense append block is skipped although
dense candidates are attached. Variant E runs the append path when raw is empty but dense candidates exist (same D 2, cap 4, budget 600,
health filter). Replay (K1): 14 MAIN rows change, +8 % prompt tokens, 2 S3 fact items reached (vit-hum-003, vit-sci-001).
Does E raise judged usefulness on MAIN 97 without new unwarned confident errors or new refusals?

## Arm
- Tree: copy of kiln-local/be-0cfd4a77-cut7-litepacks (answer.ts 0d1ac07d..., the LITEPACKS baseline tree) named
  be-0cfd4a77-cut7-litepacks-keepe; one env-gated change (KEEP_E=1): the append-block condition `retrievedRaw.length` becomes
  `retrievedRaw.length || (KEEP_E && denseCandidatesOf(retrievedRaw)?.candidates.length)`. KEEP_E unset = byte-identical behaviour.
  Diff in tools/. Not the routingr1 copy, not boar-app, no llama.cpp change.
- Step A replay (0 LLM): stub llama-server + LITEPACKS adapter (LITEDECLINE_OFF=5), detector :8094 already up (never started/stopped),
  MacBook, arms/retfloor/req/MAIN.requests.jsonl, KEEP_E unset vs 1. Changed row = dumped prompt differs. Expected 14 (ids above in K1
  keep-replay.json variant E). Reported either way.
- Step B generation: changed MAIN rows only, with KEEP_E=1 and also with KEEP_E unset (host-parity control, 0 judge calls), on the Mac mini:
  Qwen3-1.7B Q4_K_M, --reasoning off, seed 42, K1 kit (crypto ae9fbd2c, wikivoyage ff8595e3, simplewiki v3proto 99bcec30), LITEPACKS
  adapter and settings, requests = the LITEPACKS K1 request rows of those ids (arms/litepacks/runs/req). Disk >= 25 GiB; one llama-server
  on an OS-assigned port; never Docker/ollama/:8094. Fallback MacBook, recorded as a deviation.
- Baseline: LITEPACKS K1 seed 42 traces (arms/litepacks/traces/lp-K1-{cm,v01}-s42.traces.jsonl) and their Haiku judgments (K0 rows reused
  for byte-identical answers, as routing-r1/tools/analyze.py). The mini base-control texts are compared with these; a mismatch is
  reported (the paired comparison stays vs the LITEPACKS baseline, as in ROUTING-R1).

## Judge
- judge.v1-low: Haiku 5.5-low, N = 4 shards, both orders, arms/deepthink/tools/shard_judge.sh; references: bench/v0.1 for vit-*,
  bench/selftest/qa-cooking-se and qa-money-se for st-qa-*. Only E answers whose text differs from the baseline are judged; identical
  answers reuse the baseline rows.
- DECLINE2STAGE stage 1 (ruler/tools/decline2stage_stage1.mjs, prompt sha ec45ba40...): one call per E answer judged above and per
  baseline answer of those rows that has no stage-1 label by text sha in ruler/decline2stage/out/stage1.jsonl. "no" sets s := 0.
- calls_cap: Haiku 60 / Opus 0 / paid 0. Judge calls 2 per row, stage-1 1-2 per row. If changed rows need more than 60 calls, rows are
  judged in order S3 items first (vit-hum-003, vit-sci-001, st-qa-money-se-012), then id order, until the cap; unjudged rows count as
  delta 0 and are named.

## Metrics (per changed row, vs baseline)
- s = mean of the 3 judge dims over both orders; corr = correctness mean of both orders; s_D2S = 0 if stage 1 says not attempted or the
  engine declined (LITEPACKS is_decl2 / ENGINE_DECLINE as routing-r1/analyze.py), else s.
- refusal = decl2(text) or stage-1 "no".
- net U = sum over changed rows (s_D2S_new - s_D2S_base) / sum s_ref over MAIN 97 (LITEPACKS K1 rows, 451.17), with one exception: a row
  where the baseline answer had corr <= 2.5 and the new answer is a refusal counts delta 0 (neutral, RETV1ORC caveat: a refusal that
  replaces a wrong answer is not a fix).
- new CE-unwarned = new answer not a refusal, not starting with the CMP30OFF warning line, corr <= 1.5, and the baseline answer was not
  CE-unwarned.
- new refusal on a previously answered row = baseline not a refusal and new answer a refusal.
- tokens = engine approxTokens of the dumped prompts (replay), mean over MAIN and over changed rows, % vs base.

## Decision rule (stated before running)
PASS iff net U >= +0.010 AND new CE-unwarned = 0 AND new refusals on previously answered rows = 0. Otherwise KILL.
A PASS is a screen result (Haiku 5.5-low, one seed, n ~14, compresses gaps, flips ~5 % of items); it queues an Opus confirmation, not an
engine change. Dev sets only (v0.1 public + qa-cooking/qa-money self-tests). No bench/v0.4, no blind/, no rnd/veil, no Opus, no paid API,
no phone, no llama.cpp change, no maintainer contact, no push.

END FROZEN
