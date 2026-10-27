# GATE v2: stage-1 screen for the refuse-by-default product (2026-10-20)

TL;DR: a screen of the CE-unwarned items of the mini control (K0: 30 problems, K1: 21, from MAIN 97 + the 180 pack self-tests, dev only) plus 20 live shown sentinels.
A lever must beat the measured null by a margin: **GO iff net (fixed CE-unwarned minus new CE-unwarned) >= 10 on K0 (>= 9 on K1), false refusals <= 2 (K1: 4) of 20 sentinels, and U on covered items >= -0.059 (K1: -0.071).**
The 4 null runs (a whitespace-only persona patch and seed 43) read net 6, 8 (K0) and 6, 7 (K1): the null alone fixes 23-31 % of the problems, and the old "6 of 27" bar sat at the null.
`screen_gate.py` (v1) is untouched and stays for frozen verdicts. Everything below is measurement-derived; the parameters are post-hoc to the nulls by design (that is what calibration is), and were frozen before any lever ran on these screens.

## 1. What changed vs v1 (audit findings)
| v1 problem | v2 |
|---|---|
| denominator included 4 routing refusals no prompt/sampler/model arm can move (N1, M2) | problems = LIVE items only (control trace generated tokens > 0); dead items cannot be problems or sentinels |
| 4 of 10 K0 sentinels were deterministic-layer answers (facts, calculator, detector) | sentinels = 20 live items the product shows, not CE |
| CE counted refusals/notices and warned memory answers (M1, M4); only 4 of the 27 old problems were what a default-mode user sees | corrected labels (tools/labels.py): decline never CE; CEu = CE and not warned; R = decline or warned = refused in default mode |
| fixed bar 6 with unmeasured null (M3, RT-3) | bar = measured null + margin; stated power |
| no false-refusal metric (abstention levers cannot be priced) | false refusals = sentinels the control shows with judge-correct answer (corr >= 3.0) that the candidate refuses (declined or warned); U on covered items |

## 2. Screens (tools/select_screens.py; selection used only the mini control)
Pool = MAIN 97 + 180 self-tests (277 items, 227 live per pack set). Controls: K0 = lpctl-K0-main + poolctl-K0-st180; K1 = lpctl-K1-main + poolctl-K1-st180 (merged by tools/merge_ctl.py into control/pool-K0.json, pool-K1.json).
| | pool CE | CE-unwarned (live) | CE-warned | declines | PROBLEMS | SENTINELS | ids file sha256 |
|---|---|---|---|---|---|---|---|
| K0 | 81 | 30 | 50 | 30 | 30 | 20 | `891b67e2492678ff5d6ab4809c9cdac12c1ff3f76fe3f1bb3f2fdd675750e940` (pool/screen2-K0.ids) |
| K1 | 76 | 21 | 54 | 28 | 21 | 20 | `2d45ca8332bde848e82d84c95243acdcfca6bfb941e13d4f41ab21e88f008602` (pool/screen2-K1.ids) |
The unwarned CE share of the pool is only 11 % (K0) / 8 % (K1): in the new product most low-correctness answers are already refused by the warning rule. Problems come from 11 units (K0: 8 are ethereum-se, 4 travel-se, 4 v01).

## 3. Nulls (arms/null-cal/arms/<arm>/, run_pool.sh, Haiku 5.5-low judge.v1-low N = 4 both orders; control = deterministic mini control)
Null A = null-ws.patch (double spaces in the succinct persona; persona.sha256 28202320 vs control 5e0de1c7; seed 42). Null B = null-s43.patch (be/server.ts sends seed 43; text differs from the control on 27-47 live items). Sanity checks all passed (traces n/n, 0 error rows, 0 dead items changed).
| run | problems | fixed_u (by refusal) | new CEu | **net** | false refusals /20 | sentinels worse /20 (not gated) | U_cov delta [95 % CI] | changed answers |
|---|---|---|---|---|---|---|---|---|
| K0 ws | 30 | 9 (3) | 3 | **6** | 0 | 6 | -0.032 [-0.063, -0.004] | 45/50 |
| K0 s43 | 30 | 10 (2) | 2 | **8** | 1 | 7 | -0.039 [-0.076, -0.006] | 47/50 |
| K1 ws | 21 | 6 (2) | 0 | **6** | 2 | 1 | -0.052 [-0.105, -0.006] | 34/41 |
| K1 s43 | 21 | 7 (1) | 0 | **7** | 3 | 4 | -0.041 [-0.101, +0.011] | 41/41 |
Old K0 screen (NULLCAL-criterion.md, 27 problems of which 23 control CE, 4 dead): null-ws fixed 3, 0 sentinels worse, v1 NO-GO; null-s43 fixed 4, 2 sentinels worse (v1 sentinel rule failed), NO-GO. Default-mode view of those same runs: 1 of the 4 CE-unwarned problems fixed in each (25 %), 1 new CEu each; show-anyway view: 3-4 of 19 reachable CE fixed (16-21 %).
Transfer of the old runs: they cannot set the bar (4 default-mode problems), but they match the new rates (25 % on n = 8 vs 23-31 % on n = 102 problem-runs) and show that the show-anyway (warned) CE fixes by noise are 16-21 %, so a future show-anyway gate needs its own calibration; the null rate is not a K0-screen artefact. Judge test-retest (SCREENS.md): identical texts re-judged flip CE on 2 of 37 (5 %) and correctness on 13 of 37, so the judge explains at most 1-2 of the 6-10 null fixes per run; the rest is sampling plus regression to the mean of selecting items that were CE in one control draw.
Selection effects the nulls absorb: problems regress up (fixes), sentinels (selected at the top of the scale) regress down (every null has a negative U_cov delta, -0.03 to -0.05, and 1-7 of 20 sentinels "worse"). Hence sentinel-worse counts are reported only, and U_cov is gated relative to the null.

## 4. The rule (parameters in tools/screen_gate_v2.py PARAMS)
| clause | K0 | K1 | derivation |
|---|---|---|---|
| net = fixed CEu - new CEu >= | 10 (33 % of 30) | 9 (43 % of 21) | max null net (8 / 7) + 2 (about 1 binomial sd, about 2 empirical sd) |
| false refusals (sentinels newly refused) <= | 2 | 4 | max null (1 / 3) + 1 |
| U_cov delta >= | -0.059 | -0.071 | min null (-0.039 / -0.052) - 0.02 |
A GO only authorises stage 2 (MAIN 97 with the corrected CE metric, paired bootstrap, per-arm criterion); it is not an adoption. Run: `OUT_BASE=<dir> SCREEN_JSON=null-cal/pool/screen2-<K>.json bash null-cal/tools/run_pool.sh <arm> <K0|K1> null-cal/pool/screen2-<K>.ids <patch|.env|none>` (prints the gate; `python3 -I null-cal/tools/screen_gate_v2.py <agg> null-cal/control/pool-<K>.json null-cal/pool/screen2-<K>.json`).
All 4 nulls read NO-GO under the rule (6, 8 < 10; 6, 7 < 9), as they must.

## 5. Power (tools/gate_power.py, output gate_power.out)
Null net per set has 2 draws only, so two noise models bracket the answer: binomial (every item equally flippable; upper bound on variance) and normal with the empirical sd 1.12 (2 df; optimistic).
- **False GO under the null: K0 1-14 %, K1 4-17 %** (empirical vs binomial). Quote about 15 % as the conservative figure; a GO costs one MAIN stage-2 run, a false NO ends a lever.
- **Power** (lever fixes an extra share d of the problems the null does not fix): K0 d = 20 % (+4.6 net) 78 % binomial / 97 % empirical; d = 30 % 95 %; K1 d = 20 % (+2.9 net) 65 % / 79 %, d = 30 % 85 %. 80 % power (binomial) needs an extra +5.8 net fixes on K0 (42 % of the problems fixed in total) and +4.3 on K1 (52 %).
- Net effect smaller than about +3 per screen (about 10 % of the problems) is not detectable: a NO at stage 1 means "below +4 to +6 net fixes", not "no effect". Today's 4-fix arms on the old screens (fixed 4 of 23, null 3-4) are consistent with zero and would not have been resolvable.
- Not covered: the nulls change decoding only (persona whitespace, seed); a lever that changes the prompt content may also change variance. Sentinel quality loss below the U_cov margin (0.02) is not detectable at n 20.

## 6. Limits and options
- Only 4 null runs; the bar is max + margin, not an estimate of a quantile. Re-calibrate (add a third null per set, e.g. seed 44) before using the gate for a decision that matters; 2 more runs cost about 170 calls.
- Problem selection from a single control draw inflates the null. A stable-problem screen (items CE-unwarned in two independent control draws, selected on fresh seeds) would lower the null rate and the bar; not done here (the existing s43 runs would be reused circularly).
- 21-30 problems is the whole dev pool (MAIN 97 + 180 self-tests); a larger screen needs new dev items (v0.4 and blind/ are off limits).
- False-refusal proxy is judge corr >= 3.0 on a control answer the product shows; the judge never saw the sources.
- The warned flag depends on sampling (null runs add 3-4 warned answers out of 41-50), which is why false refusals under the null are 0-3 of 20 on this screen.
- Haiku-low CE labels are unvalidated against Opus at this CE rate (M5); not addressed here.

## 7. Spend and files
Haiku calls: old-screen nulls 106; pool controls 360 (K0 st180) + 360 (K1 st180) + 194 (K1 MAIN control) = 914; new-screen nulls 334 (68-94 per run). Total this task 1354 (the brief's cap of 300 covered the two old-screen nulls only; the new screens, requested by the coordinator, needed the controls). 0 Opus, 0 paid.
Files (arms/null-cal/): NULLCAL-criterion.md, NULLCAL2-criterion.md (+ .sha256), null-ws.patch, null-s43.patch, pool/screen2-K{0,1}.{ids,json}, control/pool-K{0,1}.json, tools/{run_pool.sh, mkreq_pool.py, labels.py, merge_ctl.py, select_screens.py, screen_gate_v2.py, gate_power.py, null_report.py (old screen)}, arms/ (new nulls), null-ws/ and null-s43/ (old-screen nulls; aggregates there record arms/<arm>/ paths from the run).
