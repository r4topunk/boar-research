# DEVICE-E1PAR: E1-PAR arms A, B, E (+ optional D) on the Pixel 8a, 2026-10-21 16:41-17:01 (device runner; 0 LLM, 0 judge)

TL;DR: B (Promise.all pack search) PAYS: search p50 3.89 -> 1.93 s (-1.96 s), answer p50 10.32 -> 7.39 s (-2.93 s), titles identical 10/10, PSS +0.009 GB. E (B + BLOCK_CACHE 64) KILL by the frozen rule: search p50 1.37 s = 0.71 x B (rule <= 0.6) and PSS +0.045 GB vs B (rule <= 0.032); identity holds. D (cache 256, measurement only): search 1.18 s, -0.75 s vs B (between 0.4 and 0.8: not PAYS-OVER-B, cache lever not closed). Bench-engine page measurements (GOAL: the submission is the native app, where search is 1-2 % of answer time).

Criterion: E1-PAR-criterion.md (5fb9f070). Readout: tools/e1par_readout.py -> DEVICE-E1PAR-readout.json. Raw: handoff/pixel8-2026-10-20/bench/results/e1par-{a,b,e,d}/ (rows, bench.json, telemetry, logcat, e1par-thermal.json).

| arm | APK sha / tree | search p50 / p90 s | answer p50 / p90 s | block rows | PSS peak GB | battery C before-after | LMK | titles = A |
|---|---|---|---|---|---|---|---|---|
| A serial | 284abdde / 0ca54d87 | 3.891 / 5.117 (pred 4.02) | 10.322 / 12.218 (pred 10.05) | 1949 | 3.125 | 29.8-30.0 | 0 | - |
| B Promise.all | fc1c855a / 8ad2c4b0 | 1.927 / 2.662 (pred 2.60-2.92) | 7.389 / 12.748 (pred 8.9) | 1949 | 3.133 | 30.0-31.1 | 0 | 10/10 |
| E B + cache 64 | 0a4e370e / 31ba12c4 | 1.368 / 1.699 (pred 1.26-1.72) | 5.050 / 11.176 (pred 6.67-7.21) | 1407 | 3.178 | 29.8-29.9 | 0 | 10/10 |
| D B + cache 256 | 74dbb664 / 3bf53253 | 1.175 / 1.518 (pred 1.0-1.5) | 5.048 / 11.380 (pred 6.6-7.0) | 988 | 3.202 | 29.9-29.9 | 0 | 10/10 |

Verdicts (frozen clauses): B PAYS (search drop 1.96 >= 0.8, answer drop 2.93 >= 0.8). E KILL (clause 1 ratio 0.71 > 0.6; clause 3 PSS +0.045 > 0.032; clause 2 identity true); B - E = 0.56 s >= 0.4, so the cache lever is not closed on the phone, it just misses the frozen 0.6 ratio. D MEASURED: B - D 0.75 s, ratio 0.61, PSS +0.069 GB vs B.
Reading: B beat its own prediction (search -1.96 s vs -1.1 to -1.4 s predicted); E's search p50 sits inside its predicted band (1.26-1.72), but because B came in lower than predicted the ratio clause fails. PSS is a 5 s sample (lower bound). Thermal status 0 on every arm; every arm started at battery <= 30.0 C (A waited 562 s, B 1 s, E 499 s, D 250 s).
Deviations: no A2 drift control and no arm C (criterion scope). BOAR Bench was found NOT installed at session start (see G1-SWA5 addendum): the A-union kit was rebuilt from local files with every pack and the gazetteer sha-matched on device before these runs; the dd2 SWA5 runs (3 x 11 questions) ran on the same phone between 16:22 and 16:31, before A. A ran on a freshly installed cur APK (no earlier run in that install). After D the cur APK (284abdde) was reinstalled; it is the BOAR Bench APK left on the phone.
