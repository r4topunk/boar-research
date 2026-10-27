# A1-RC1-SHIPPED-U criterion (round 6, ruler/hypotheses-round6-2026-10-21.json; frozen 2026-10-21 before any phone run and any judge call)

## Statement (verbatim from the hypothesis)
RC1 as installed (Qwen2.5-1.5B, Detailed, maxTokens 1024, Standard KB only, 0 packs) on the CV5 frame (51 v0.1 dev ids) scores U_Opus within
+-0.05 of the desktop closed-book 1.5B rung (0.261), and at least 0.05 below the 1.7B K0 rung (0.351). Retrieval fires on <= 5/51 rows.

## System and run
- App team.sopa.aoair 2.0.0-rc1 (versionCode 4, release, apk sha256 2ef432584fed6adab41b00833884694d0cc53e311a830695b160bf3847c14f17) on the Pixel 8a,
  as installed: only qwen2.5-1.5b-instruct-q4km, the eval hook's own style (Detailed, maxTokens 1024), Standard KB only, 0 packs. Nothing installed,
  uninstalled or changed on the phone; style not changed.
- Request rc-cv5-51-15b (handoff/pixel8-2026-10-20/bench/requests/rc-cv5-51-15b.request.json, sha256 d37c33b7e1897c23...): native format as
  rc-speed9-15b (pipeline legacy, models [qwen2.5-1.5b-instruct-q4km]), warmup-000 first (not scored), then the 51 ids with the v0.1 question text
  (checked byte-equal to bench/v0.1/questions.public.jsonl). Run: rc_eval.py run rc-cv5-51-15b (request64 hook), one run, one seed (app default).
- Ids: the RV2 primary 51 = ruler/cv5-ladder/in/set.json ids (= arms/gemma4-e2b/phone/judge/v01-57.ids minus FLOOR's 6 nonmodel_path_items);
  arms/rc1-pixel/a1/in/v01-51.ids sha256 a31567c1c36eb0d2.... Dev set; no blind/, rnd/veil, v0.4.
- Traces: tools/a1_traces.py (rows -> EvalTrace; outcome != success or empty answer -> error, floor-scored 1/1/1 by judge.mjs --floor-errored, 0 calls).
- Not a speed run: no thermal gate (deviation from the hypothesis' 31.0 C gate, by the task). Battery temperature and thermal status recorded before
  and after; telemetry every 5 s.

## Judge (as CV5-LADDER-OPUS)
- judge.v1 bytes: boar-eval harness/judge.mjs sha256 bda1aeb5fe196b72..., scorers/vendor/eval-lib/judge-core.mjs sha256 521f7ad33a130e1a...
  (both unchanged since 2026-10-15, i.e. the bytes CV5 used); refs = bench/v0.1 frozen refs, refsSha256 bd235bb9811f6d1a..., questionsSha256 568b3ececd8afe5c....
- Opus (judge.mjs default), both orders, seed 7, --gap-ms 0, N = 4 shards via arms/deepthink/tools/shard_judge.sh model opus, JUDGE_FLOOR_ERRORED=1
  (tools/a1_judge.sh). No reuse (new texts). calls: planned 102, cap 120 including retries; if a pass would exceed 102 new calls it stops at 102.
  Haiku 0, paid API 0, desktop generation 0.
- DECLINE2STAGE (ruling R1): the stage-1 zero is applied with the 0-call labels.is_decline stand-in (arms/null-cal/tools/labels.py), exactly as
  DECLINE2STAGE (d) did for unclassified ladder texts, because this task has 0 Haiku. Comparison rows: CV5-LADDER-OPUS rows, same frame.

## Analysis (tools/a1_analyze.py, committed with this file)
- s, r = mean of the 3 dimensions averaged over both orders; U = sum(s-1)/sum(r-1) (floor-adjusted, as CV5); raw = sum(s)/sum(r);
  U_net = (U-0.058)/0.942 (sensitivity row); U_D2S = U with s = 1 on detected non-answers.
- Item-cluster bootstrap B 2000, numpy default_rng(11), 2.5/97.5 pct, pairs on the same draws (as cv5_ladder.py). Paired against the CV5 Opus rungs
  on the same 51 ids: 1.7B K0 s42 (L1), 1.5B closed-book (L0), Gemma E2B (L2), 4B cut 7 Pixel (L3).
- Win/tie/loss vs the reference: winner boar in both orders = win, ref in both = loss, else tie. Per 100: correct (corr >= 4), CE (corr <= 1.5),
  decline (is_decline), partial; non-declines only for correct/CE.

## Comparison rows (CV5-LADDER-OPUS-2026-10-21.json, Opus judge.v1, v0.1 51, one seed)
| rung | U (CI) | U_D2S |
|---|---|---|
| L0 Qwen2.5-1.5B closed-book (desktop, K0 frame) | 0.261 (0.189-0.342) | 0.258 |
| L1 1.7B K0 s42 (desktop) | 0.351 (0.279-0.437) | 0.351 |
| L3 4B cut 7 Pixel 8a | 0.460 (0.387-0.537) | 0.460 |

## Decision (frozen; kill rules verbatim from the hypothesis)
- PARTIAL: fewer than 45/51 answered rows (success, non-empty), or any LMK line -> no claim number; the page keeps variant B 'submitted app unmeasured on the ruler'.
- PROXY-HOLDS iff |U_RC1 - 0.261| <= 0.05. BELOW-ENGINE iff U_L1 - U_RC1 >= +0.05 with paired CI low > 0 (RV2 rule); 'below on the point' if >= 0.05 with CI covering 0.
- SUPPORTED iff PROXY-HOLDS and BELOW-ENGINE and retrieval <= 5/51; KILLED iff not PROXY-HOLDS; else MIXED.
- Retrieval > 10/51 -> the 'effectively closed-book' wording is dropped and the result is called 'KB-assisted'.
- Decision on U (judge.v1) because the anchors are judge.v1 numbers; U_D2S printed beside; if a flag differs between the two, both are reported and the claim uses U_D2S (R1).
- Label: 'default install' (the RC1 catalog can download the 4B), not 'only model'. Every number names Opus judge.v1, v0.1 dev 51, one run.

## Prediction
U_RC1 about 0.26 (0.21-0.31): retrieval on <= 5/51 (RC1-PARITY 1/9) and LENGTH-SLOPE puts the 1.5B Opus length slope <= 0, so Detailed does not lift it.
1.7B - RC1 about +0.09, CI likely touching 0 (MDE about 0.10 at n 51). Win-rate 0/51. CE per 100 similar to the closed-book rung.

## Known limits
One run, one seed, n 51 dev ids; RC1 answers in Detailed/1024 vs the comparison rungs' styles; desktop rungs vs phone; is_decline stand-in for stage 1.
