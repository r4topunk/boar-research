# GEMMA-OPUS-MAIN criterion (frozen 2026-10-21 before any Opus call of this pass)

## Question
Under the Opus judge, is Gemma 4 E2B (engine sampler, K0) better than Qwen3-1.7B (K0) on MAIN 97 by the GEMMA4 stage-2 margin?
Context: under Haiku 5.5-low the seed-42 pair is dU +0.028 (+0.006...+0.052), stage-2 FAIL by 0.002 on the frozen +0.03 rule (GEMMA4-criterion.md
section 4); pooled two seeds +0.029 (+0.009...+0.048) (CONFIRM.md, no verdict). CV5-PER100-OPUS gave Gemma +5.2 correct-shown per 100 over the 1.7B;
CV5-LADDER-OPUS gave Gemma +0.011 (-0.033...+0.056) over the 1.7B on the v0.1 51. This pass is a new pre-registration; it does not reopen the
Haiku stage-2 verdict, which stays FAIL under Haiku.

## Arms (existing traces, no generation; dev set MAIN 97 = arms/lp-screens/main-97.ids)
- Primary pair (seed 42): control = 1.7B lpctl-K0-main-s42 (arms/lp-screens/control/traces), candidate = Gemma 4 E2B stage-2 engine sampler
  K0 s42 (arms/gemma4-e2b/stage2/traces/gemma4-e2b-eng-K0-main-s42.traces.jsonl).
- Secondary pair (seed 43, report only): c43 vs g43 (arms/gemma4-e2b-confirm/runs/{c43,g43}/traces). Run only if the whole unit list fits the cap.

## Judge
- judge.v1 bytes, Opus (arms/deepthink/tools/shard_judge.sh ... 4 opus = node harness/judge.mjs --judge-model opus, --gap-ms 0, --seed 7),
  both orders, N = 4 shards, one pass per ruler/gemma-opus-main/in/<arm>-<unit>.ids file (ruler/tools/gemma_opus_run.sh), on that arm's traces.
- Unit = unique (item id, answer text): judge.mjs sees only question, reference and answer text, so identical text across arms and seeds is judged
  once. Reuse: every existing Opus judge.v1 row pair (ok, both orders, seed 7, the unit's refsSha256/questionsSha256) on the identical unit,
  indexed by ruler/tools/cv5_opus_pool.py (sources: CV5-LADDER-OPUS, CV5-PER100-OPUS, CE-OPUS-CHECK, WARN-OPUS, packs self-tests, kiln runs).
- Unit list frozen in ruler/gemma-opus-main/in/set.json by ruler/tools/gemma_opus_prep.py (0 calls, run before this file was hashed):
  315 units, 134 reused, 181 new (s42 39, s43 142), planned 362 calls.
- **calls_cap: Opus 400** (this pass). Haiku 0, paid API 0, generation 0, phone 0, mini 0. Order: seed-42 files first, then seed-43 files.
  A stopped shard (STOP file) is fixed and rerun, never skipped; every unit needs both orders before analysis.

## Analysis (ruler/tools/gemma_opus_analyze.py, committed with this file; definitions = gemma4-e2b-confirm/tools/confirm_report.py)
- Per item: s, sref = mean of the 3 judge dims averaged over both orders (boar, ref sides); corr = correctness averaged over orders.
  Labels = arms/null-cal/tools/labels.py on the Opus corr (decline, warned, CE corr <= 1.5, CEu = CE and not warned, R = decline or warned).
- U = sum(s, s := 0 for trace-declined) / sum(sref); dU = U(Gemma) - U(1.7B) on the 97 paired ids; CI = item bootstrap, random.Random(11),
  B 2000, sorted[50] / sorted[1949] (as confirm_report.py).
- Also reported (no decision weight): CE-unwarned count and rate (both arms), CE any, declines, warned, refused R, default-mode U (R := 0) with dU CI,
  U on items both answer (both shown, refused := 0) with dU CI, U on control-covered (confirm_report.py "covered"), changed-text count,
  Spearman of per-item s Opus vs Haiku (per arm, Haiku = the existing agg_run aggregates), Opus/Haiku CE and correct (corr >= 4) agreement,
  Opus - Haiku U offset per arm; seed-43 pair and pooled two-seed (confirm_report.py pooled definitions) if run.
- Phone speed trade printed next to the result (not a clause): Pixel 8a, 73 questions, same session: answer p50 1.7B 4.2 s vs Gemma 11.8 s
  (arms/gemma4-e2b/phone/GEMMA4-PHONE.md).

## Decision (seed-42 pair only, Opus)
- **GO** iff dU >= +0.03 and CI low > 0. Otherwise **NULL** (no GO). The CE-unwarned rate change is reported, not a clause.
- Sentence chosen mechanically: GO -> "Under Opus, Gemma 4 E2B is +X U over the 1.7B on MAIN 97 (CI a...b), 1 seed"; NULL -> "Under Opus, Gemma 4 E2B
  is not separated from the 1.7B on MAIN 97 by the +0.03 rule (dU +X, CI a...b, 1 seed)". Seed-43 and pooled numbers are printed as report-only.

## Known limits (stated before the run)
One seed decides; n 97 dev ids (v0.1 57 + two Stack Exchange self-test units 20 + 20); the Opus pass sees the warning line in warned texts;
reused rows came from earlier Opus passes on the identical (item, text, frame); the per-100 and ladder Opus passes already exposed many of these units.
