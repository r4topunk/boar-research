# DG-STAGE1 (2026-10-21 21:2x-21:50): GATE v2 K1 screen for the four DECODE-GROUND arms

TL;DR: **all four arms NO-GO** (S net 5, SB net 6, SC net 5, C1 net 4; bar 9). No stage 2. The SELECT arms "fix" problems mostly by turning them into warned (default-mode refused) answers, and they lose citations: 8/20 (S), 6/20 (SB), 7/20 (SC) false refusals vs max 4, and U_cov Δ −0.165…−0.204 vs min −0.071. C1 (CAD on the kept context) is the cleanest arm (3/20 false refusals, answers kept, U_cov −0.076, just under the −0.071 line) but net 4. Haiku used: 232 of 700 (Opus 0, paid 0, phone 0). Criterion `DG-criterion.md` sha 92d3340a… verified unchanged before every run (run_pool_dg.sh checks it).

## Deviations from the brief (read first)
1. **Screen file.** `lp-screens/screen-K1.ids` (sha c7ea13c3…) is the OLD v1 screen (27 problems + 10 sentinels, all inside MAIN 97) and is not what GATE v2 uses. The GATE v2 K1 screen is `null-cal/pool/screen2-K1.ids` (41 ids = 21 problems + 20 sentinels, sha 2d45ca83…, json `screen2-K1.json`), which matches the "21 problems + 20 sentinels" of the brief and of the criterion. I used it (what `launch_screens.sh` / gemma4-e2b did). `screen_gate_v2.py` asserts the candidate aggregate covers every screen id.
2. **Extra generation.** Only 11 of the 41 screen ids are in MAIN 97 (30 are 180 self-tests). So each arm was generated again on all 41 ids (mini, same patch/env as the MAIN run, `tools/run_pool_dg.sh` = `null-cal/tools/run_pool.sh` with the generation step swapped for `tools/run_dg.sh`). Overlap check against the MAIN-97 runs, byte-identical answer text: S 11/11, SB 11/11, SCp01 7/11, C1p01 7/11 (the two-slot CAD jobs are not bit-reproducible across job composition; the screen-run traces are what was judged).
3. **Control.** The gate pairs against `null-cal/control/pool-K1.json` (merged mini K1 control: lp-screens/control lpctl-K1-main + null-cal/control poolctl-K1-st180; the only control that has judge rows for the 180 self-tests, and the one gemma4-e2b used). Against the mini baseline `litepacks/traces/mini/lp-K1-{cm,v01}-s42.mini` the control differs on **2 of 97 MAIN items (lan-exp-007, st-qa-money-se-005); neither is in the screen**, so the screen control is identical to the mini baseline on all 11 MAIN screen ids (0 differing).
4. **Preflight cap.** `DG-criterion.md` has no `calls_cap:` line, so `CRITERION` was not passed to the judge preflight (it would refuse); the cap is tracked by hand in `runs/logs/CALLS.md`.
5. **Child rule.** S is NO-GO with net 5 (≤ 5), but SC's smoke changed 3 of 5 vs S (not < 3), so SC was not skipped; SB and C1 were run as ordered.

## Stage 0 sanity (MAIN 97, 0 LLM; `tools/sanity_dg.py`, `aggregates/sanity-main-<arm>.json`)
Baseline = merged mini K1 control. 22 of 97 items are on the deterministic path (FACTS / calculator / first-aid card / chat refusals: control outputTokens 0 or no generate code); 75 are live.
| arm | rows | non-empty | loops | det-path diff | changed vs ctl (of 75 live) | NO_EVIDENCE | selected in dropped / in kept | mean out tok (ctl 36.41) | mean totalMs (ctl 3105) | ratio | CJK answers (ctl 1) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S | 97/97 | 97 | 0 | 0 | 62 (61 vs mini baseline) | 16 | 9 / 36 | 34.87 | 3645 | 1.17 | 1 |
| SB (b 4.0) | 97/97 | 97 | 0 | 0 | 62 (61) | 16 | 9 / 36 | 34.67 | 3643 | 1.17 | 1 |
| SC (CAD 1.0, plaus 0.1) | 97/97 | 97 | 0 | 0 | 62 (61) | 16 | 9 / 36 | 34.96 | 4241 | 1.37 | 1 |
| C1 (CAD on kept) | 97/97 | 97 | 0 | 0 | 61 (60) | 0 | 0 / 0 | 35.05 | 3906 | 1.26 | 1 |
Kill rules (>5 % empty/loop, totalMs > 4x): none hit. totalMs ratios are against the control traces generated earlier (the smoke's same-idle-host B gave S 1.35, SB 1.39, SC 1.6, C1 1.1); the select call averages 2.6 s on the 61 rows that have candidates. Screen-run sanity (41 ids) also passed for all four (ratios 1.54 S, 1.54 SB, 1.61 SC, 1.09 C1; inflated by 2-3 concurrent mini jobs).
NO_EVIDENCE vs the RAG-FUNNEL K1 label (reported only): 16 NO_EVIDENCE on MAIN (21 % of live), 12 of them are S1 items (no usable fact in any installed pack) = 75 % precision; of the 45 S1 items, 10 are on the deterministic path and 24 have a SELECT menu (the other 11 have no candidates), so recall is 12/24 (50 %) among S1 items with a menu: the other 12 still get a selected chunk. SB and SC reuse S's SELECT call (same 16 NO_EVIDENCE).

## Stage 1: GATE v2 K1 (net >= 9, false refusals <= 4/20, U_cov Δ >= −0.071; Haiku 5.5-low judge.v1, N 4, both orders, only answers differing from the control: 29 per arm = 58 calls)
| arm | gate line (screen_gate_v2.py output) |
|---|---|
| S | `screen2 K1: problems 21 \| fixed_u 8 (by refusal 7) \| new CEu 3 \| net 5 (bar 9) \| false refusals 8/20 (max 4) \| sentinels worse 4 (report only) \| U_cov -0.2035 [-0.2804, -0.129] (min -0.071) \| changed 29 \| dead changed 0 -> NO-GO` |
| SB | `screen2 K1: problems 21 \| fixed_u 7 (by refusal 5) \| new CEu 1 \| net 6 (bar 9) \| false refusals 6/20 (max 4) \| sentinels worse 5 (report only) \| U_cov -0.1651 [-0.2423, -0.0942] (min -0.071) \| changed 29 \| dead changed 0 -> NO-GO` |
| SC | `screen2 K1: problems 21 \| fixed_u 7 (by refusal 5) \| new CEu 2 \| net 5 (bar 9) \| false refusals 7/20 (max 4) \| sentinels worse 4 (report only) \| U_cov -0.1773 [-0.2547, -0.1048] (min -0.071) \| changed 29 \| dead changed 0 -> NO-GO` |
| C1 | `screen2 K1: problems 21 \| fixed_u 6 (by refusal 2) \| new CEu 2 \| net 4 (bar 9) \| false refusals 3/20 (max 4) \| sentinels worse 3 (report only) \| U_cov -0.0760 [-0.1398, -0.0198] (min -0.071) \| changed 29 \| dead changed 0 -> NO-GO` |

Extras (`aggregates/stage1-summary.json`, `screens/<arm>/aggregates/*.gate2.json`)
| arm | CE-unwarned ctl -> cand (41 screen items) | warned answers (ctl 0) | of which "uncited with sources" | answers with a surviving citation (ctl 28/41) | NO_EVIDENCE on screen (problems) | selected in dropped | paired U Δ all 41 [CI] | CJK |
|---|---|---|---|---|---|---|---|---|
| S | 21 -> 16 | 15 | 12 | 11 | 5 (3) | 2 | −0.058 [−0.102, −0.019] | 0 |
| SB | 21 -> 15 | 11 | 8 | 15 | 5 (3) | 2 | −0.058 [−0.102, −0.019] | 0 |
| SC | 21 -> 16 | 12 | 9 | 14 | 5 (3) | 2 | −0.062 [−0.102, −0.027] | 0 |
| C1 | 21 -> 17 | 5 | 5 | 23 | 0 | 0 | −0.028 [−0.071, +0.008] | 0 |
Mean correctness on the screen (ctl -> S): problems 1.14 -> 1.33, sentinels 4.15 -> 2.98 (SB 3.03). Sentinels worse in S: lan-cmp-003 (5.0 -> 1.0), st-boar-simplewiki-en-007 (5.0 -> 1.5), st-boar-medlineplus-en-007, st-boar-medlineplus-en-019; false-refusal sentinels in S: st-boar-medlineplus-en-020, lan-exp-003, st-qa-outdoors-se-008, st-boar-simplewiki-en-003, st-qa-outdoors-se-014, st-boar-factbook-010, st-qa-bitcoin-se-015, st-qa-bitcoin-se-013.

Reading (facts from the traces; interpretation is mine):
- The SELECT arms are NOT mainly "fixing" by better reading: 7 of 8 (S) / 5 of 7 (SB, SC) fixed problems are refusals, i.e. the answer now carries the "Not found in this phone's offline library" line.
- Only 3 of the 15 warned S answers are NO_EVIDENCE fallbacks; 12 are answers built on a selected chunk that lost every `[n]` citation, so the engine's grounding layer releases them as "compact-decline-released-uncited-with-sources" (control cited 15/15 on the same items). In two cases the selected chunk came from the keep step's dropped list (e.g. st-qa-outdoors-se-008: `off-topic-dropped-1` + `citations:removed-1`), where the post-hoc guard still treats it as off-topic. This looks like an integration effect (one-chunk context + citation/grounding post-processing), not a decoding result; any follow-up needs the SELECT context to carry what the guard expects. Not tested here (no patch edits made).
- C1 is the only arm with the control's citation behaviour (23/41 vs 28/41) and few warnings; its 6 fixes include 4 real answer changes, and U_cov −0.076 sits 0.005 below the line with the net at 4. By the frozen rule it is NO-GO.
- The sentinels lose the most under SELECT (4.15 -> ~3.0): one chunk replaces the kept multi-chunk context.
- Haiku-low labels, n = 21 problems / 20 sentinels, one seed: a NO-GO means below the +4..+6 net floor of GATE-V2 §5, not "no effect". Prediction in the criterion (S net 6-9, SC highest) was not met: SC 5, SB 6, S 5, C1 4.

## Stage 2
Not run: no GO arm (criterion rule 2).

## Commands (all from `arms/decode-ground`; MacBook for the judge, mini for generation; no pushes, nothing committed)
```
python3 -I tools/sanity_dg.py runs/traces/dg-<S|SBb4|SCp01|C1p01>-K1-main-s42.traces.jsonl ../lp-screens/main-97.ids aggregates/sanity-main-<run>.json
IDS=../null-cal/pool/screen2-K1.ids      # absolute path used
nohup bash tools/run_pool_dg.sh S     S  K1 $IDS > screens/logs/S.log
DG_BIAS=4.0 nohup bash tools/run_pool_dg.sh SB    SB K1 $IDS > screens/logs/SB.log
DG_PLAUS=0.1 nohup bash tools/run_pool_dg.sh SCp01 SC K1 $IDS > screens/logs/SCp01.log
DG_PLAUS=0.1 nohup bash tools/run_pool_dg.sh C1p01 C1 K1 $IDS > screens/logs/C1p01.log
python3 -I tools/stage1_extras.py          # -> aggregates/stage1-summary.json
```
run_pool_dg.sh = criterion-sha check -> `../null-cal/tools/mkreq_pool.py` requests -> `tools/run_dg.sh` (mini) -> `tools/sanity_dg.py` (stops on det-path diff / kill rule) -> `deepthink/tools/shard_judge.sh` (haiku, N 4, `--preflight` without criterion) per unit on changed ids only -> `lp-screens/tools/agg_run.py --control null-cal/control/pool-K1.json` -> `null-cal/tools/screen_gate_v2.py`.

## Calls and files
Haiku 232 (4 x 58; ledger `runs/logs/CALLS.md`), Opus 0, paid 0, phone 0. Mini: 4 x 41-item jobs (+ the coordinator's chain MAIN runs). No blind, rnd/veil or bench/v0.4 read.
Files: `screens/<S|SB|SCp01|C1p01>/{runs/req,runs/logs,traces,judgments,aggregates}` (gate: `aggregates/dg-<arm>-screen2-K1-s42.gate2.{txt,json}`), `screens/logs/*.log`, `aggregates/sanity-main-*.json`, `aggregates/stage1-summary.json`, `tools/{run_pool_dg.sh,sanity_dg.py,stage1_extras.py}`, `runs/logs/CALLS.md`.

---
# SA follow-up (2026-10-21 21:5x-22:1x): SELECT as augmenter (arm SA)

TL;DR: **SA NO-GO** (net 6, bar 9; false refusals 0/20; U_cov Δ −0.0445, inside the −0.071 margin). The coordinator's diagnosis holds: promoting the pick to source [1] inside the normal multi-source prompt restores citations and removes the false refusals (S 8/20 -> SA 0/20; screen citations 11 -> 24 of the control's 28), but the net gain is only 6 (S 5, SB 6). The SELECT idea, measured cleanly, adds about one point over S and stays under the null-cal bar. No stage 2. Haiku 44 (total 276 of 700; SA cap 150), Opus 0, paid 0, phone 0.
Criterion: `DG-SA-criterion.md` (sha 19956cfe…, file `DG-SA-criterion.sha256`), frozen before any SA generation. Prediction (net 6-9, false refusals <= 3, U_cov in margin; modal outcome NO-GO at net 6-8): met on all three numbers.

Arm: `sources = pick ? [pick, ...sources.filter(c => c.chunkId !== pick.chunkId)] : sources` (NO_EVIDENCE leaves the engine's sources untouched). Patch `tools/dg-sa.patch` sha256 439fce743f9b39f1a165572268735e3ce6176f84368a0e30f278a459fccfc090 = `tools/dg.patch` (c81ba531…, untouched) + 5 changed lines (arm lists, `augment: DG_ARM === "SA"`, the sources line). `tools/run_dg.sh` accepts arm SA and env `DG_PATCH` (default dg.patch).
Validity: S smoke re-run under dg-sa.patch = 5/5 byte-identical answers and reasonCodes vs the stored S smoke (S unchanged); SA smoke 5/5 non-empty, 0 loops, citations present where S lost them (st-qa-money-se-001: `[2]` Credit history, vit-hum-004: `[2]`; lan-cmp-004 and vit-hum-001 stay uncited-and-warned exactly like B). MAIN 97: 97/97 rows, 0 empty, 0 loops, 22 deterministic items byte-identical to the control (0 diff), screen/MAIN overlap 11/11 identical answers, CJK 1 (= control 1).

| arm | gate line (screen_gate_v2.py output) |
|---|---|
| SA | `screen2 K1: problems 21 \| fixed_u 8 (by refusal 4) \| new CEu 2 \| net 6 (bar 9) \| false refusals 0/20 (max 4) \| sentinels worse 3 (report only) \| U_cov -0.0445 [-0.0976, 0.0018] (min -0.071) \| changed 22 \| dead changed 0 -> NO-GO` |

Fixed (8): lan-cmp-005, st-boar-factbook-001, -007, -011, st-qa-travel-se-012, -018, vit-cry-006, vit-hum-004 (4 by refusal, 4 real answer changes). New CEu (2): lan-cmp-003, st-boar-factbook-013 (both correctness 5.0 -> 1.0). Sentinels worse: lan-cmp-003, st-boar-factbook-013, st-boar-simplewiki-en-007 (5.0 -> 2.0). Mean correctness problems 1.14 -> 1.45, sentinels 4.15 -> 3.60 (S: 1.33 / 2.98). Paired U Δ all 41 −0.0164 [−0.0664, +0.0261] (S −0.058); CE 21 -> 18 (all-answers) / CE-unwarned on problems 21 -> 15; warned answers 4 (ctl 0; S 15); changed answers 22 of 41 (S 29).

Citation table (answers with a surviving `[n]` citation; `tools/sa_extras.py` -> `aggregates/sa-summary.json`)
| set | control cited | S | SA | SA on the items the control cited |
|---|---|---|---|---|
| screen 41 | 28 | 11 | 24 | 24/28 |
| MAIN 97 | 23 | 16 (10 of the 23) | 22 (18 of the 23) | 18/23 |
MAIN: S lost the citation on 13 of the control's 23 cited items; SA kept it on 9 of those 13 (5 of the 23 still lose it, 4 items are cited that the control did not cite).

Extras (MAIN 97 unless noted; `aggregates/sanity-main-SA.json`)
| changed answers vs control (of 75 live) | NO_EVIDENCE | NO_EVIDENCE in S1 label | picks from keep-dropped / kept | pick-bearing answers identical to control | mean out tokens (ctl 36.41) | mean totalMs (ctl 3105) | ratio |
|---|---|---|---|---|---|---|---|
| 38 (37 vs mini baseline; S 62) | 16 (same menu as S) | 12 (75 %) | 9 / 36 | 24 of 61 | 35.70 | 5960 | 1.92 (inflated: ran concurrently with the screen job; select call mean 3.1 s) |
Screen run: 0 empty, 0 loops, ratio 2.20 (3 concurrent mini jobs), mean out tokens 42.85 (ctl 44.05), picks from keep-dropped 2, NO_EVIDENCE 5.

Reading (facts from traces; interpretation is mine):
- The false refusals and the ~U_cov loss of S/SB/SC were the one-chunk integration effect: with the multi-source prompt kept they go to 0/20 and −0.045.
- What is left is the effect of the pick itself: 8 fixes vs 2 regressions on 21 problems (half of the fixes are refusals), 3 sentinels worse; 24 of the 61 pick-bearing MAIN answers come out identical to the control, so promoting a chunk the model already saw moves few answers. At n = 21 + 20 and Haiku-low labels the +6 sits inside the +4..+6 net floor of GATE-V2 §5, i.e. indistinguishable from the null.
- A gain would have to come from the 9 MAIN picks outside the kept set (2 on the screen); that is too few to carry a net of 9 here.

Stage 2: not run (criterion rule 2: GO arms only).

Commands: `export DG_PATCH=$PWD/tools/dg-sa.patch; python3 -I ../lp-screens/tools/mkreq.py K1 ../lp-screens/main-97.ids dg-SA-K1-main-s42 cut7-headpass-x2+litepacks+dg-SA runs/req/dg-SA-K1-main-s42.requests.jsonl; bash tools/run_dg.sh SA runs/req/dg-SA-K1-main-s42.requests.jsonl dg-SA-K1-main-s42; bash tools/run_pool_dg.sh SA SA K1 <null-cal/pool/screen2-K1.ids>; python3 -I tools/sanity_dg.py ...; python3 -I tools/sa_extras.py`.
Files: `DG-SA-criterion.{md,sha256}`, `tools/{dg-sa.patch,sa_extras.py}`, `runs/traces/dg-SA-K1-main-s42.traces.jsonl`, `runs/traces/dg-{SA,Spar}-smoke5-s42.traces.jsonl`, `screens/SA/{traces,judgments,aggregates}` (gate: `aggregates/dg-SA-screen2-K1-s42.gate2.{txt,json}`), `aggregates/{sanity-main-SA,sa-summary}.json`, `runs/logs/CALLS.md`.
