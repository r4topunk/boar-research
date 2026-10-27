# RC1-SPEED4B prediction (H3; frozen 2026-10-21 18:xx before any 4B run on RC1; re-bases DD1022 §1 for the 4B arm)

Source: ruler/hypotheses-round6-2026-10-21.json DD2-RC1-SPEED4B (lens B). 0 judge. Scorer: dd_check.py speed (this folder).

## Why a new file
DD1022 §1 was frozen for Succinct against succinct bench refs. RC1's eval hook cannot run Succinct: DeviceEvalRunner.kt (snapshot wt/native-qa
5f8cc8f4) l.164 takes maxTokens from personalities.json defaultId = "detailed" (Auto 1,024), l.203 takes the style from defaultId (health and
small-talk prompts switch to Succinct via ShortAnswer), and l.190 loads with EngineTweaks() default (MMAP), not the user's preset. So answer
p50 is a style-length number here; the decisive readouts are **decode tok/s and TTFT**. Answer p50 vs the bench 23.0 s is reported with the
caveat "Detailed/1024 vs bench succinct/512".

## Run
- App/APK: team.sopa.aoair 2.0.0-rc1 (apk sha 2ef43258..., as installed 10-21), model qwen3-4b-instruct-2507-q4km downloaded in Wi-Fi window 1
  from RC1's own Model Catalog (snapshot catalog: 2,497,281,120 B, sha256 3605803b...; record the on-device size, sha and catalog version).
- Request rc-speed9-4b (SHA256SUMS.dd1022, c7aec328...), ids ruler/ids/dd1022-speed9.ids (warmup + 9: lan-rsn-004, lan-cmp-005, lan-rsn-006,
  lan-rsn-005, lan-cmp-002, lan-cmp-004, lan-hlt-003, lan-exp-003, lan-exp-005). Bench reference results/q4ba73-a (same 9 ids).
- Gate: thermal_gate.py rc-speed9-4b 310 (status 0, battery <= 31.0 C). Airplane ON after the download. Log battery level + charge counter
  before/after; report decode mean of the first third vs the last third of the 9 calls.
- Phone minutes: ~10 download (inside Wi-Fi window 1) + ~15 run + up to 10 cool-down = 25 (download counted in the window row).

## Prediction (n = 9, warmup excluded)
decode p50 5.0-7.0 tok/s; TTFT p50 <= 3 s; tokens p50 350-480; answer p50 55-95 s; 0 LMK; 9/9 rows success.

## Readout (mechanical)
- **ENGINE-OK**: decode p50 >= 4.5 tok/s AND TTFT p50 <= 5 s AND 0 LMK. Then the T_8GB native gap on the shipped default is style length,
  not the engine; DD1022 §1's answer-p50 clause is printed as "FAIL by length (Detailed/1024)" and does not trigger the NOTE-1 engine addendum.
  The prediction's band (decode within +/-20 % of the bench 4B's 5.6 = 4.48-6.72, TTFT <= 3 s, answer 55-95 s) is printed hit/miss beside it.
- **ENGINE-GAP** (kill): decode p50 < 4.5 tok/s OR TTFT p50 > 5 s (prompts <= 80 tokens) OR any LMK line naming team.sopa.aoair -> NOTE-1 gets
  an engine/load addendum and "all tiers usable" is withdrawn for the APK.
- < 8/9 rows: PARTIAL, no verdict.

## Not runnable / fallback
- qwen3-4b absent from the installed RC1 catalog, or the download fails -> NOT RUNNABLE; the R4 8 GB row = RC1 1.5B (RC1-SPEED, 25.2 s p50,
  internal) labelled "out-of-box install"; 0 extra minutes.
- If the RC does not change before 10-22, this run is itself the fallback (no 1.7B needed).

## Only the app maintainer can supply (none needed for this run)
A Succinct default or a style field in request64 (revives the Succinct pair); the NOTE-1 1.7B entry (revives rc-speed9-17b).
