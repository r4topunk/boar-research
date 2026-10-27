# DD1022 criterion: the five phone readouts of the 2026-10-22 device day (frozen 2026-10-21 before any phone run)

Source: hypotheses-round3-2026-10-21.json (DEV-SPEED17, DEV-LAYERPAR, DEV-GEMMA-T1, DEV-AUNION-NATIVE, DEV-4B-PRESSURE); thresholds and kill
clauses are the hypothesis texts, restated here so the readout is mechanical. Scorer: dd_check.py (this folder). 0 judge calls decide anything.
Device: Pixel 8a (GrapheneOS, 7.5 GB), airplane mode, Wi-Fi/BT off, AC power, the app maintainer's RC in front, driven by
handoff/pixel8-2026-10-20/bench/rc_eval.py (request64 hook) or, if the hook is missing, by hand (DEVICE-DAY §F; same rules, n as typed).
Ids: ruler/ids/dd1022-*.ids (shas alongside). Requests: handoff/pixel8-2026-10-20/bench/SHA256SUMS.dd1022.

## Thermal rule
A run whose readout is a time (SPEED, AUNION retrieval, PRESSURE) starts only after thermal_gate.py passes: status 0 and battery <= 31.0 C for
SPEED, <= 34.0 C for AUNION and PRESSURE. Runs whose readout is routing, text or markers (LAYER, T1) are not gated; temperature is recorded.

## 1. DEV-SPEED17 (rc-speed9-4b, rc-speed9-17b; style Succinct, recorded per row)
Reference rows, same 9 ids, same phone: 4B q4ba73-a (answer p50 23.0 s, TTFT 10.9 s, decode 5.6 tok/s), 1.7B q17b73-a (9.6 s, 5.5 s, 9.0 tok/s).
PASS: RC answer p50 <= 1.5x bench and 0 LMK; MARGINAL: 1.5-2x and 0 LMK; FAIL: > 2x or any LMK line naming the package.
Kill: RC 4B > 2x or any LMK -> the ruler speed row prints measured FAIL/MARGINAL for the RC, the 'all tiers usable' sentence is withdrawn for the
APK, NOTE-1 gets an addendum. No 1.7B in the RC by end of day -> the 1.7B arm is closed for the APK and the R4 8 GB row is the 4B, labelled.
RC 1.7B not >= 2x faster (answer p50) than RC 4B -> NOTE-1's speed rationale is dropped. A sideloaded 1.7B (HF browser) is reported as
'sideloaded, not shipped' and does not satisfy 'in his build'.

## 2. DEV-LAYERPAR (rc-layer10-4b; shipped default style)
Layer ids vs cut 7 Pixel rows (final-cut7-v01): trv-002 (port row 1 facts r9), vit-sci-003 (row 4 arithmetic), saf-004 (row 6 card),
vit-hlt-002 (row 11 health path); match = 0 generated tokens AND normalised text identical (dd_check.py norm). epi-1021 (row 13) counts as a
5th match only if answered with 0 tokens and 'thigh'. >= 4/5 match -> those rows are struck from NOTE-1 as 'already in RC', arm closes.
<= 2/5 -> NOTE-1 leads with the missing layers; R4 labels the headline row 'RC without layers X, Y'. geo-dev-1022 answer class
(refuse / generic / place-list): anything but refuse/generic -> TILE-PATH reopens and RV4's 'scores 0' assumption is dropped.
The 4 divergent answers (lan-cmp-003, lan-exp-007, vit-sci-002, lan-rsn-004) are descriptive only (optional Haiku judge.v1, ~16 calls); never a parity verdict.

## 3. DEV-GEMMA-T1 (rc-t1a-gemma + rc-t1b-gemma = divergent-v01, 20 prompts; his default style)
FAIL (NOTE-3 withdrawn for this release, no retry before 10-25): any thinking marker in any output (dd_check.py MARK regex: <think>,
<|channel|>, <channel|>, 'thought', 'Thinking Process', a reasoning preamble), or > 1 of 20 outputs at maxTokens - 1 or more, or any LMK.
Under Succinct also > 1 output above 120 tokens (2x our engine p90 of 60 on these ids, gemma73-a). Gemma not loadable in his build by
18:00 -> NOTE-3 parked post-freeze, not sent.

## 4. DEV-AUNION-NATIVE (rc-aunion10-base-17b then rc-aunion10-17b; 4B variants if no 1.7B; needs a debuggable RC)
After pushing the 6 A-union packs to files/corpus (sha-checked on device): FAIL if the set cannot be installed, or retrieved titles map to
<= 3 of the 6 packs on these 10 ids, or PackSource labels are wrong on >= 3 rows -> persona map not proposed for the RC; the R4 A-union row is
'bench, not the APK'; NOTE-1 section 4 becomes a bug report. Not recommended for 8 GB this release if retrieval p50 rises > +5 s or PSS > +0.3 GB
vs the no-pack base run. Expected (bench): +2.4 s retrieval, PSS flat. Release build (no run-as): NOT RUNNABLE, logged, 3-line ask drafted for r4to.

## 5. DEV-4B-PRESSURE (bg_set.sh, then rc-press-4b-c1..c3; rc-press-17b-c1..c3 if the 1.7B is present)
Kill event = an LMK/lmkd line naming the package, the process gone for >= 3 consecutive 10 s polls, or fewer rows than questions.
4B 0/3 killed and PSS peak <= 5.0 GB -> hypothesis killed ('the 4B fits 8 GB with background apps, 3/3, Pixel 8a' goes in the gates table).
>= 1/3 4B killed while the 1.7B passes -> NOTE-1 amendment (r4to OK); R4 8 GB row uses the 1.7B or carries 'killed in k/3 cold loads with
background apps'. Both tiers killed -> phone limit, not an argument.
