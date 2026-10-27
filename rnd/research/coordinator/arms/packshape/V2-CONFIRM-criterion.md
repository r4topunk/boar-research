# FACTBOOK-V2-CONFIRM criterion (frozen 2026-10-23 before any judge call; never edited after)

Question: does the shaped boar-factbook pack (kiln-local/shape-packs/shaped/boar-factbook.sqlite, sha256 981f7b4b..., PACKSHAPE criterion 89f565ca) beat the original pack at claim grade (Opus judge.v1) on the 20 factbook self-tests?

## Inputs (no new generation)
| arm | traces | sha256 | ids |
|---|---|---|---|
| BASE (original pack, PACKPROOF ON, seed 42, MacBook) | arms/packproof/gen/on-k13/traces.jsonl | f3a398a8 | the 20 st-boar-factbook-001..020 rows of 140 |
| S42 (shaped, seed 42, mini) | arms/packshape/gen/on-k13s/traces.jsonl | 095528d4 | 20 |
| S43 (shaped, seed 43, mini) | arms/packshape/gen/on-k13s43/traces.jsonl | a5681d84 | 20 |
Bench frame: boar-eval/bench/selftest/boar-factbook (questions 8f5c7cde, refs de460a68; agent-written gold, dev only).

## Judge (Opus only; no Haiku, no paid API, no phone)
`arms/deepthink/tools/shard_judge.sh <traces> v2confirm/<ARM>.judgments.jsonl <bench> v2confirm/ids.txt fbv2-opus-<ARM> 4 opus` (sha 20e02e21): judge.mjs judge.v1, model opus, seed 7, both orders (boarA/boarB), N 4 shards. 3 arms x 20 ids x 2 orders = 120 calls; cap 130 (shard reruns count). Fresh rows for all 60 answers (no pool reuse). A shard that stops is resumed, never skipped; if the cap is hit before 120 ok rows: verdict INCOMPLETE.

## Metrics (tools in v2confirm/agg.py, 0 calls; definitions as coverage-map/sefix/ans-tools/agg_opus_cm.py)
- Per unit: s = mean over the two orders of mean(correctness, completeness, usefulness) of the BOAR side; r = same for the reference side; corr = mean correctness over orders.
- U = sum(s - 1) / sum(r - 1) over items. Paired dU = U(arm) - U(BASE) on the same 20 ids, per seed (S42, S43).
- Pooled: per item, s and r averaged over S42 and S43 (one shaped value per item), dU_pooled = U(pooled) - U(BASE).
- CI: item bootstrap B 2000, numpy default_rng(11), percentile 2.5/97.5, paired draws.
- better/tie/worse per item: s(arm) - s(BASE) > 0.25 / |.| <= 0.25 / < -0.25 (pooled uses the averaged s).
- CE (confident error) = corr <= 1.5 and not declined (null-cal/tools/labels.py is_decline); reported per 100 and as CE-unwarned. correct = corr >= 4 and not declined.
- New confident error = an (item, seed) unit that is CE in S42 or S43 while the same item is not CE in BASE.

## Decision
- **CONFIRMED** if dU_pooled CI low > 0 AND new confident errors = 0.
- else **NOT-CONFIRMED** (reported with the per-seed deltas and the new-CE items).
Default-eligible status is not decided here: it follows the PACKPROOF rule (Haiku correct-any ON >= 0.60), which the Haiku pooled 0.50 does not reach; the Opus correct/100 is reported as a sensitivity only.

## Predictions (before the run)
P1 dU_pooled > 0 with CI low > 0 (Haiku +0.25 correct-any). P2 per seed both > 0. P3 at least one new CE (013 and 010 flipped right to wrong under Haiku), so the frozen CE clause may fail even if U rises.
