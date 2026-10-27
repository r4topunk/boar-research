# DEVICE-DAY RUNSHEET 2026-10-22, re-cut 10-21 18:xx against RC1 (lens B of HYP-ROUND6; one ordered table)

TL;DR: the RC on the Pixel 8a is RC1 (team.sopa.aoair 2.0.0-rc1, versionCode 4, release, apk sha 2ef43258; only Qwen2.5-1.5B installed, 0 packs). Its own catalog (snapshot 5f8cc8f4) lists qwen3-4b (2.50 GB) and wiki-vital5 (164 MB), so two Wi-Fi windows by r4to make the 4B rows (speed, layers/warning, pressure) and one pack row runnable on RC1 without the app maintainer. Day order is fixed by thermal rules: Codex ladder on the laptop → Wi-Fi window 1 (4B) → H3 speed (≤ 31.0 C) → H2 layers + warning (ungated) → Wi-Fi window 2 (wiki-vital5) → H5 → H4 pressure last (≤ 34.0 C per cycle). **Phone minutes: 117 for the five rows + setup (152 if A1 has not run before window 1)**, inside the 3 h budget. Every new row has a prediction file frozen today (shas below). 0 LLM today; the Codex ladder uses r4to's [usage detail removed].

Facts that set the plan (checked 10-21 18:xx, 0 LLM):
- Snapshot catalog app/src/main/assets/boar-data/catalog.json (sha 18406c60): qwen3-4b-instruct-2507-q4km 2,497,281,120 B (sha 3605803b…); wiki-vital5 sqlite-pack 163,647,488 B (sha d3b87d56…; RC1's Knowledge screen shows 156 MB = MiB, RC1-PACKS). No qwen3-1.7b, no gemma-4-e2b (only gemma-4-e4b), no boar-packs. **UNKNOWN: whether the installed RC1 catalog equals the snapshot: check the Model Catalog screen in setup (row 0b).** RC1-PACKS read the Knowledge catalog (vital5 present), not the Model Catalog.
- DeviceEvalRunner.kt (snapshot) l.164 maxTokens from personalities.json defaultId "detailed" (1,024); l.203 style = defaultId except ShortAnswer (health, small talk → Succinct); l.190 loads with EngineTweaks() default (MMAP). So every RC1 eval-hook row is Detailed/1024 at default load; H3 is judged on decode tok/s + TTFT, not answer p50. "Run Boar Run" (MMAP_MLOCK) is reachable only by hand in the chat UI.
- Warning-line string ("Not found in this phone's offline library…may be wrong:") has 0 hits in the snapshot's code and assets.
- Criteria re-checked unchanged: CV5-LADDER-CODEX 89f2b173 (frozen file for row 0; no new prediction file), DD1022 ba800fc1. SHA256SUMS.dd1022 20/20 OK after appending 3 new requests. Codex ladder out/ empty (not started).

## Day order (phone minutes = install/download + run + cool-down)

| # | run id | app / model | request (sha8) | items | min | decides | criterion / prediction (sha8) | gate | who | prerequisites only the app maintainer can supply | fallback if the RC does not change / kill |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | CODEX ladder (laptop, start first) | n/a | ruler/codex-ladder run.sh (408 calls = 4 rungs × 51 × 2) | 4×51×2 | 0 (15 attn) | claim v5 S1 two-family; R4 column | CV5-LADDER-CODEX (89f2b173, unchanged 10-21 18:xx) | — | r4to starts, coord scores (cv5_ladder_codex.py) | none | not run by **10-23 18:00** → S1 single-family |
| 0b | setup: re-check RC1 + catalog read | RC1 as installed | rc_eval.py check | — | 5 | which §0 state (A2: N1, N5, C4) | — | — | r4to | — | record apk sha, Model Catalog (4B listed?), Knowledge catalog (vital5 listed?); photo of both screens |
| 1s | A1 rc-v01-51-15b (only if not already run; must precede window 1) | RC1, 1.5B | rc-v01-51-15b (A1 writes it) | 51 | 35 (cond) | §0 S00 number | arms/rc1-pixel/RC1-SHIPPED-criterion.md (A1, frozen before its run) | ≤ 31.0 C | r4to | none | not started by 10-22 18:00 → NOT RUN; S00 says "not measured on the ruler set" |
| W1 | Wi-Fi window 1: Model Catalog → Qwen3 4B → Download | RC1 | — | — | 10 | runnability of H3/H2/H4 on the 4B | — | — | r4to (Wi-Fi ON, then airplane ON) | none (in RC1's own catalog per snapshot) | 4B not listed → H3 NOT RUNNABLE, H2/H4 on the 1.5B (see their files) |
| H3 | rc-speed9-4b | RC1, catalog 4B | rc-speed9-4b (c7aec328) | 1+9 | 25 | NOTE-1 engine vs style; claim C4 sentence | RC1-SPEED4B-prediction.md (701dc157) | ≤ 31.0 C, status 0 | r4to | Succinct default / style field (would revive the Succinct pair) | this run is the fallback; ENGINE-GAP → NOTE-1 addendum |
| H2a | rc-layer10-4b (rc-layer10-15b if no 4B) | RC1 | rc-layer10-4b (66cda732) / rc-layer10-15b (729345af) | 10 | 13 (5 on 1.5B) | NOTE-1 port list; R4 label | RC1-LAYERWARN-prediction.md (bb7bbed8) + DD1022 §2 | ungated, temp recorded | r4to | release notes of the layers in RC (optional) | ≥ 4/5 matches → rows struck from NOTE-1 |
| H2b | rc-warn10-4b | RC1, catalog 4B | rc-warn10-4b (9e77566d) | 10 | 12 | NOTE-2 premise on RC1 | RC1-LAYERWARN-prediction.md (bb7bbed8) + N2 (8a9cdc9e) | ungated | r4to | none | no 4B → run on the 1.5B, labelled "small-model prompt" |
| W2 | Wi-Fi window 2: Knowledge → Wikipedia Vital Articles → Download | RC1 | — | — | 3 | runnability of H5 | — | — | r4to | none | vital5 not listed → H5 NOT RUNNABLE |
| H5 | rc-vital9-15b (pack left installed for H4) | RC1, 1.5B + wiki-vital5 | rc-vital9-15b (bf155205) | 1+9 | 9 | NOTE-5 premise: packs vs 0.7 gate (1/9 → k/9) | RC1-VITAL5-prediction.md (92eb4ade) | ≤ 31.0 C | r4to | none for vital5; NOTE-5 entries for any boar-pack run | GATE-BINDS → NOTE-5 gate line |
| H4 | rc-press-4b-c1..c3, then the manual "Run Boar Run" cycle (r4to's OK on the day; first to cut) | RC1, catalog 4B | rc-press-4b-c1/c2/c3 (e4b22f35 / c69c9a47 / 0e8387fa) | 3×3 + 3 typed | 37 (27 + 10) | gates table 8 GB row; NOTE-1 memory amendment | RC1-PRESS-prediction.md (60c6f86c) + DD1022 §5 | ≤ 34.0 C per cycle | r4to | NOTE-1 1.7B entry (revives rc-press-17b) | no 4B → 3 cycles on the 1.5B, preset dropped |
| R | restore: force-stop background apps; switch back to Auto; leave RC1 installed | — | — | — | 3 | — | — | — | r4to | — | — |
| F | filler only if the RC rows end early: E1-PAR A2 (bench app `cur`) | bench app | e1par-a2 | 1+10 | 12 (opt) | drift control | DDdoc | ≤ 31.0 C | r4to | — | skip freely |

**Totals:** 0b 5 + W1 10 + H3 25 + H2 25 + W2 3 + H5 9 + H4 37 + R 3 = **117 phone min**; + A1 35 if it has not run = **152**; + filler 12 = 164. Cut order if time runs short: F → preset half of H4 (−10) → H2a divergent descriptive part (no time saved, skip Haiku) → H5.

## Status of the old rows (detail in the superseded table below)
- **Done:** rc-speed9-15b (substitute for row 1; RC1-SPEED, RC1-PARITY), swa5 (KILLED, G1-SWA5 addendum), E1-PAR A / B (PAYS) / D (measured) / E (KILL) (DEVICE-E1PAR.md), DD-WARN-RC on rc-speed9-15b (line 0/3).
- **Moot until NOTE-1 ships (1.7B in an RC catalog):** row 2 rc-speed9-17b, row 5 rc-press-17b-c1..c3, row 15 rc-aunion10-*-17b. **Moot (Gemma E2B not in RC1's catalog; snapshot lists only gemma-4-e4b):** row 7 T1. **Moot (bench app, no phone minutes earned):** E1-PAR C, A2 (filler only), dd-layer10-bench4b, REPACK16.
- **Blocked until NOTE-5 (our packs in the catalog) or a debuggable RC / .sqlite picker:** any boar-packs run on RC (rc-aunion10-base-*, rc-aunion10-*; RC1-PACKS NOT RUNNABLE).
- Row 6 N2-RC readout runs on whatever rc dirs exist (coord, 0 min).

## Commands (fish; `$G` and cwd as in DEVICE-DAY §Before you start)
```fish
fish_add_path ~/Library/Android/sdk/platform-tools
cd <workspace>/handoff/pixel8-2026-10-20/bench
set G <workspace>/rnd/research/coordinator/arms/device-day-1022
# 0 (laptop, bash)
cd <workspace>/rnd/research/coordinator/ruler/codex-ladder; codex login status; bash run.sh pilot; bash run.sh all; bash run.sh status
# 0b
shasum -a 256 -c SHA256SUMS.dd1022; python3 rc_eval.py check; adb shell dumpsys battery | grep -E 'level|charge counter|temperature'
# W1: Wi-Fi ON, RC1 menu -> Model Catalog -> Qwen3 4B -> Download; record size/sha; airplane ON
# H3
python3 $G/thermal_gate.py rc-speed9-4b 310; python3 rc_eval.py run rc-speed9-4b
python3 -I $G/dd_check.py speed results/rc-speed9-4b/rows.jsonl results/q4ba73-a/rows.jsonl
# H2 (ungated; rc-layer10-15b if the 4B is absent)
python3 rc_eval.py run rc-layer10-4b; python3 -I $G/dd_check.py layer results/rc-layer10-4b/rows.jsonl
python3 rc_eval.py run rc-warn10-4b
cd <workspace>/rnd/research/coordinator/arms/note2-transfer/tools; python3 -I note2_apply.py --ref q4ba73-a --rc <workspace>/handoff/pixel8-2026-10-20/bench/results/rc-warn10-4b; cd -
# W2: Wi-Fi ON, Knowledge -> BOAR Knowledge -> Wikipedia Vital Articles -> Download; airplane ON
# H5
python3 $G/thermal_gate.py rc-vital9-15b 310; python3 rc_eval.py run rc-vital9-15b; grep -n "packs" results/rc-vital9-15b/logcat.txt
# H4 (per cycle: Wi-Fi ON for bg_set, airplane ON before the run; meminfo every 5 s)
python3 $G/thermal_gate.py press-4b-c1 340; bash $G/bg_set.sh press-4b-c1; python3 rc_eval.py run rc-press-4b-c1   # c2, c3
python3 -I $G/dd_check.py press results/rc-press-4b-c1 results/rc-press-4b-c2 results/rc-press-4b-c3
# R
for p in com.android.chrome app.vanadium.browser com.google.android.apps.maps com.google.android.youtube app.grapheneos.camera; adb shell am force-stop $p; end
```

## Pre-flight (10-21 18:xx, coordinator, 0 LLM; re-run 0b's lines tomorrow)
- [x] SHA256SUMS.dd1022: 20/20 OK (17 old + rc-warn10-4b, rc-layer10-15b, rc-vital9-15b). ruler/ids/dd1022-warn10.ids written (sha 80703225; README row added).
- [x] Prediction files sha'd: RC1-SPEED4B 701dc157, RC1-LAYERWARN bb7bbed8, RC1-VITAL5 92eb4ade, RC1-PRESS 60c6f86c (arms/device-day-1022/*.sha256).
- [x] CV5-LADDER-CODEX 89f2b173 and DD1022 ba800fc1 unchanged; Codex ladder not started (out/ empty).
- [x] Snapshot facts (catalog ids/sizes, DeviceEvalRunner l.164/190/203, warning-line grep) checked as listed above.
- [ ] 0b: installed RC1 Model Catalog lists Qwen3 4B; Knowledge catalog lists Wikipedia Vital Articles (RC1-PACKS saw it 10-21).
- [ ] 0b: phone free (no other session driving adb; E1-PAR was blocked 26 min on 10-21 by another session).
- [ ] Wi-Fi windows: r4to's network; ≥ 3 GB free on the phone for the 4B + vital5.
- [ ] dd_check.py press is untested on rc_eval output (fails on bench dirs by design; first real test is H4 c1).
- [ ] A1 status: if rc-v01-51-15b has not run, it goes before W1 (it needs RC1 exactly as shipped).
- Battery/meminfo/decode-trend logging per the 10-21 web-log additions (kept below in the superseded section) applies to every row.

---

## Superseded 10-21 17:5x (the pre-RC1 plan; kept for the record)
### DEVICE-DAY RUNSHEET 2026-10-22 (one ordered table; source = DEVICE-DAY-2026-10-22.md, not a new plan) (old title)

TL;DR: with the RC, the must block (S1a, S1b, L2, PRESS-4B) takes about 80 phone min. A 180-min day adds T1, SWA5 and the E1-PAR core (A, B, E, A2). C, D and AUNION drop. Without the RC: E1-PAR (all 6 arms) + SWA5 ≈ 95 min. Every row has a frozen criterion committed. Pre-flight passed on 2026-10-21 at 14:4x (§Pre-flight). 0 LLM calls today; the Codex ladder uses r4to's [usage detail removed], not Claude.
Deviation from DEVICE-DAY: PRESS moves to the end of the must block, not the end of the day. The doc's own rule ("only 30 min left after step 2 → step 5 first") is applied up front because r4to's time is uncertain. Every row after PRESS is either ungated (markers/identity) or behind thermal_gate.py, and the background apps are force-stopped first. SWA5 runs before E1-PAR so that A2's reinstall doubles as the end-of-day restore (saves one 3-min install).

APK tags: `rc` = maintainer RC (UNKNOWN sha; record it at install) · `cur` = gemma2 284abdde (installed now) · `ps` = parsearch fc1c855a · `bc256` = blockcache256 74dbb664 · `bc64` = blockcache64 0a4e370e · `dd2` = parsearch-dd2 57c70477 (same tree 8ad2c4b0 as `ps`; not a substitute: the criteria name the sha).
Criteria: DD1022 = arms/device-day-1022/DD1022-criterion.md (ba800fc1) · CV5 = ruler/CV5-LADDER-CODEX-criterion.md (89f2b173) · SWA5 = arms/g1-swa5/G1-SWA5-criterion.md (b89f1f1a) · BC64 = arms/blockcache/BLOCKCACHE64-criterion.md (ee39a755) · BC = arms/blockcache/BLOCKCACHE-criterion.md (dd4e4615) · N2 = arms/note2-transfer/NOTE2-TRANSFER-criterion.md (8a9cdc9e) · DDdoc = DEVICE-DAY §E1-PAR text (commits 1eae8371 / aa81a76d, no standalone sha; see Conflicts).

### Case RC arrives (min = install + run + cool-down; phone minutes only)

| # | run id | APK | request | items | min | decides | criterion | cool | who | kill / skip if time runs out |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | CODEX ladder (laptop) | n/a | ruler/codex-ladder (408 calls) | 4×51×2 | 0 (15 attn) | page S1 two-family, R4 column | CV5 | no | r4to starts, coord scores | not run by 10-23 18:00 → S1 single-family |
| 0b | setup: RC install + check + in-app downloads, Succinct | rc | — | — | 30 (not counted) | — | — | — | r4to | no `request64` → §F manual sheets |
| 1 | S1a rc-speed9-4b | rc | rc-speed9-4b | 1+9 | 20 | claim ruler speed row; NOTE-1 | DD1022 | ≤31.0 C | r4to | RC 4B >2× bench or LMK → FAIL row; never skip **10-21 16:0x device runner: NOT RUNNABLE, the RC on the phone (team.sopa.aoair 2.0.0-rc1, versionCode 4, release, apk sha 2ef43258) has only qwen2.5-1.5b installed; substitute rc-speed9-15b (measurement only) in results/rc-speed9-15b, readout arms/rc1-pixel/RC1-SPEED.md.** |
| 2 | S1b rc-speed9-17b | rc | rc-speed9-17b | 1+9 | 15 | NOTE-1 speed sentence | DD1022 | ≤31.0 C | r4to | no 1.7B in RC catalog → arm closed, 0 min **10-21 15:56 DONE: request failed "qwen3-1.7b matches no installed model" (installed: qwen2.5-1.5b only) -> 1.7B arm closed for this APK.** |
| 3 | L2 rc-layer10-4b (style back to shipped default first) | rc | rc-layer10-4b | 10 | 18 | NOTE-1 port list; R4 label | DD1022 | no (record) | r4to | never skip (best value/min) |
| 4 | PRESS-4B c1..c3 | rc | rc-press-4b-c1..c3 | 3×3 | 27 | NOTE-1 8 GB; claim R4 8 GB row | DD1022 | ≤34.0 C each cycle | r4to | cycles not started stay NOT RUN; 1 cycle ≠ verdict |
| 5 | PRESS-17B c1..c3 (only if ≥1 4B cycle killed) | rc | rc-press-17b-c1..c3 | 3×3 | 18 (cond) | NOTE-1 amendment | DD1022 | ≤34.0 C | r4to | 4B 0/3 killed → skip (verdict needs no 1.7B) |
| 6 | N2-RC readout (rows 1-3, 7) | — | note2_apply.py --rc | — | 0 | NOTE-2 premise | N2 (RC clause) | — | coord | runs on whatever dirs exist |
| — | **must-finish cut (≈ 80 min; 98 if row 5 fires)** | | | | | | | | | |
| 7 | T1 rc-t1a-gemma + rc-t1b-gemma (force-stop bg apps first) | rc | rc-t1a-gemma, rc-t1b-gemma | 10+10 | 25 | NOTE-3 send/withdraw | DD1022 | no (record) | r4to | Gemma not loadable by 18:00 → NOT RUN, NOTE-3 parked |
| 8 | SWA5 swa5-g-default, -g-full, -q17-default | dd2 | swa5-*.request.json | 3×(1+10) | 20 (3 install) | NOTE-3 wording | SWA5 | no (record temp) | r4to | never stop/resume mid-request (INVALID); skip whole step, not one arm **10-21 16:22-16:31 DONE: KILLED (0 markers, identity VOID); arms/g1-swa5/G1-SWA5.md addendum.** |
| 9 | E1-PAR A (criterion + readout ready; 10-21 attempt NOT RUN: phone busy with another session's device tests) | cur | e1par-a | 1+10 | 17 (3 install) | baseline for B/E | E1PAR (5fb9f070) | ≤31.0 C | r4to | — **10-21 16:41 DONE (search 3.89 s, answer 10.32 s); DEVICE-E1PAR.md.** |
| 10 | E1-PAR C (2 packs → corpus-off, back after) | cur | e1par-c | 1+10 | 12 | catalog default (kit lever) | DDdoc | ≤31.0 C | r4to | drop 2nd (after D) |
| 11 | E1-PAR B | ps | e1par-b | 1+10 | 12 | maintainer note E1 (Promise.all) | E1PAR (5fb9f070) | ≤31.0 C | r4to | titles ≠ A → void; PSS > A+0.3 GB/LMK → stop **10-21 16:43 DONE: PAYS (-1.96 s search, -2.93 s answer).** |
| 12 | E1-PAR D (ceiling) | bc256 | e1par-d | 1+10 | 12 | measurement only (H-A3 closed) | BC + DDdoc | ≤31.0 C | r4to | drop 1st **10-21 16:59 DONE: measured, -0.75 s vs B.** |
| 13 | E1-PAR E | bc64 | e1par-e | 1+10 | 12 | maintainer note ADOPT/KILL | BC64 | ≤31.0 C | r4to | stop on LMK or PSS > A+0.3 GB **10-21 16:53 DONE: KILL (0.71 x B; PSS +0.045 GB).** |
| 14 | E1-PAR A2 (= restore of BOAR Bench) | cur | e1par-a2 | 1+10 | 12 | drift control | DDdoc | ≤31.0 C | r4to | A2–A search p50 >15 % → rerun A + failed arm once **10-21: not run; cur APK reinstalled 17:01 as the restore.** |
| — | **nice-to-have ends here at ≈ 180 min (rows 7-9, 11, 13, 14)** | | | | | | | | | |
| 15 | AUNION base + push + aunion10 (debuggable RC only) | rc | rc-aunion10-base-17b, rc-aunion10-17b | 10+10 | 30 | persona map; NOTE-1 §4 | DD1022 | ≤34.0 C | r4to | release RC → NOT RUNNABLE (log; §G ask is r4to's call) |
| 16 | restore RC side (DEVICE-DAY §Restore) | — | — | — | 5 | — | — | — | r4to | — |

Totals, RC case: must 80 (98 with row 5). Must + T1 + SWA5 + E1-PAR core (A, B, E, A2 = 53) = 178. Everything = 239 (+18). Without a 1.7B in the RC: −15.
### Case no RC (rows 1-7, 15 NOT RUN; log each one in QUEUE as NOT RUN, no RC)
Order: 0 CODEX → E1-PAR A, C, B, D, E, A2 (rows 9-14, doc order, cool phone at start, A needs no install) → SWA5 (dd2) → reinstall `cur`. Min: 66 + 20 + 3 ≈ 90.
Must-finish (≈ 60): A, B, E, A2, SWA5. Nice-to-have: C, D, then the optional `dd-layer10-bench4b` (it is a control and only means something next to RC rows, so skip it).

### Commands (copied from DEVICE-DAY; fish; `$G` and cwd as in its §Before you start)
```fish
fish_add_path ~/Library/Android/sdk/platform-tools
cd <workspace>/handoff/pixel8-2026-10-20/bench
set G <workspace>/rnd/research/coordinator/arms/device-day-1022
set BA <workspace>/bench-app/build
# 0 (laptop, bash)
cd <workspace>/rnd/research/coordinator/ruler/codex-ladder; codex login status; bash run.sh pilot; bash run.sh all; bash run.sh status
# 0b
adb install -r <path-to-his-RC.apk>; python3 rc_eval.py check; python3 rc_eval.py run rc-speed9-4b --dry-run
# 1-2
python3 $G/thermal_gate.py rc-speed9-4b 310; python3 rc_eval.py run rc-speed9-4b
python3 $G/thermal_gate.py rc-speed9-17b 310; python3 rc_eval.py run rc-speed9-17b
python3 -I $G/dd_check.py speed results/rc-speed9-4b/rows.jsonl results/q4ba73-a/rows.jsonl
python3 -I $G/dd_check.py speed results/rc-speed9-17b/rows.jsonl results/q17b73-a/rows.jsonl
# 3
python3 rc_eval.py run rc-layer10-4b; python3 -I $G/dd_check.py layer results/rc-layer10-4b/rows.jsonl
# 4-5 (per cycle; Wi-Fi ON for bg_set, then airplane ON before the run)
python3 $G/thermal_gate.py press-4b-c1 340; bash $G/bg_set.sh press-4b-c1; python3 rc_eval.py run rc-press-4b-c1   # c2, c3; then rc-press-17b-c*
python3 -I $G/dd_check.py press results/rc-press-4b-c1 results/rc-press-4b-c2 results/rc-press-4b-c3
for p in com.android.chrome app.vanadium.browser com.google.android.apps.maps com.google.android.youtube app.grapheneos.camera; adb shell am force-stop $p; end
# 6 (coordinator)
cd <workspace>/rnd/research/coordinator/arms/note2-transfer/tools; python3 -I note2_apply.py --rc <results/rc-* dirs that exist>
# 7
python3 rc_eval.py run rc-t1a-gemma; python3 rc_eval.py run rc-t1b-gemma
python3 -I $G/dd_check.py t1 results/rc-t1a-gemma/rows.jsonl results/rc-t1b-gemma/rows.jsonl
# 8
adb install -r $BA/boar-bench-0cfd4a77-cut7-cmp30off-batchret-parsearch-dd2-nonet-8ad2c4b0fae9.apk
adb shell dumpsys battery | grep temperature; python3 boar_bench.py run swa5-g-default    # same for swa5-g-full, swa5-q17-default
python3 -I <workspace>/rnd/research/coordinator/arms/g1-swa5/tools/compare_swa5.py --json <workspace>/rnd/research/coordinator/arms/g1-swa5/readout.json
# 9-14 (install before A, B, D, E, A2; thermal gate before every arm)
adb install -r $BA/boar-bench-0cfd4a77-cut7-cmp30off-batchret-nonet-gemma2-0ca54d870ba8.apk                 # A, A2 (cur)
adb install -r $BA/boar-bench-0cfd4a77-cut7-cmp30off-batchret-parsearch-nonet-8ad2c4b0fae9.apk              # B
adb install -r $BA/boar-bench-0cfd4a77-cut7-cmp30off-batchret-parsearch-blockcache256-nonet-3bf53253e984.apk # D
adb install -r $BA/boar-bench-0cfd4a77-cut7-cmp30off-batchret-parsearch-blockcache64-nonet-31ba12c473d1.apk  # E
python3 $G/thermal_gate.py e1par-a 310; python3 boar_bench.py run e1par-a   # c, b, d, e, a2 alike
# C only, COMPOSED from the step text ("run-as mv"), not in DEVICE-DAY; check paths with `run-as ... ls files/corpus` first:
adb shell run-as team.sopa.boarbench sh -c 'mkdir -p files/corpus-off; mv files/corpus/boar-visa-en.sqlite files/corpus/boar-medlineplus-en.sqlite files/corpus-off/'
adb shell run-as team.sopa.boarbench sh -c 'mv files/corpus-off/boar-visa-en.sqlite files/corpus-off/boar-medlineplus-en.sqlite files/corpus/'   # right after C
# 15: DEVICE-DAY step 4 block verbatim (push loop + photo of the PackSource label). 16: DEVICE-DAY §Restore verbatim.
```

### Pre-flight (run 2026-10-21 14:4x by the coordinator; re-run 0b's lines tomorrow)
- [x] APK shas: ps fc1c855a, bc64 0a4e370e, bc256 74dbb664, dd2 57c70477, cur 284abdde: all match their .sha256 files.
- [x] SHA256SUMS.dd1022: 17/17 OK. e1par-a/c/b/a2/d/e shas = DEVICE-DAY (a6f7f151 b4b74c85 1d4abc84 529c819f 2d30aff9 337caf24); swa5 bd0727ae / 41556048 / 7db97cdc.
- [x] Criteria shas: DD1022, CV5, SWA5, BC64, BC and N2 all match. Codex packet SHA256SUMS OK. ruler/ids/dd1022-*.ids: 8/8 sha OK, and every rc-*/dd-* request equals its ids file (ordered). swa5.ids = the swa5 requests.
- [x] Baseline rows present (73 rows each): q4ba73-a, q17b73-a, aunion73-a, gemmaa73-a, gemma73-a. All request ids appear in their baseline except epi-1021 and geo-dev-1022 (new layer probes, by design).
- [x] Dry runs that pass: rc_eval.py --help and `run rc-speed9-4b --dry-run` (default pkg team.sopa.aoair); boar_bench.py --help; dd_check speed/layer/t1/aunion on bench rows; thermal_gate.py (copy in scratch; status 0, battery 26.7 C, skin 37.1 C); partime_analyze.py; compare_swa5.py ("MISSING result dirs", expected); cv5_ladder_codex.py (INCOMPLETE, expected); run.sh status (0/102 ×4); note2_apply.py --rc on a scratch copy.
- [!] dd_check.py press failed on bench dirs (no summary.json/device.json). Expected: it reads rc_eval output, so it cannot be tested before row 4.
- [x] Pixel 8a on USB now (adb "device"). codex CLI on PATH.

### Conflicts
1. Same APK in a row: A then C (both `cur`, batched). B/D/E are three different APKs, three installs. dd2 and `ps` share a tree but not a sha, so no merge. SWA5 runs before E1-PAR, so A2's reinstall of `cur` is also the restore: 6 installs (18 min) instead of 7.
2. Missing ids: none. Every request matches its ids file and its baseline (except the two new probes, by design).
3. No standalone frozen criterion: E1-PAR arms A, B, C, D (rules and predictions only in the DEVICE-DAY text, committed in 1eae8371 / aa81a76d, no .sha256). E has BC64. D's H-A3 is already CLOSED in BC. RESOLVED 2026-10-21 for A/B/E/D: arms/e1-partime/E1-PAR-criterion.md (5fb9f070, commit 89a1ec8e; battery gate 30.0 C; C and A2 not covered).
4. RESOLVED 2026-10-21: arms/e1-partime/tools/e1par_readout.py (0 LLM; reproduces the 4.02 / 10.05 basis on aunion73-a). Was: partime_analyze.py hardcodes aunion73-a/q17b73-a and cannot read e1par-* runs. The coordinator needs a 0-LLM readout before rows 9-14 land (search p50, ordered retrievedTitles identity, PSS peak, A2 drift).
5. E1-PAR is listed as "about 20 phone min" but now has 6 arms, 4 installs and 31 C gates: realistic 66-77 min.
6. Arm C has no copyable command (composed above, flagged).
7. N2 RC clause "≤ 3/10": note2_apply.py evaluates one dir at a time, and premise_fails needs ≥ 10 bench-warn ids in one dir. The 9-10-id RC runs can only trip the scaled clause (≤ 30 %).
8. PRESS order deviates from the doc (see top). boar_bench.py prints "engine tree hash not found" for every new APK (TREES lists only cut6/speed). This is cosmetic: check the tree in bench.json.

### Pre-flight additions from the web log (2026-10-21 15:xx; WEB-LOG T5.1, T5.2, T8.3, T6.4)
- **Memory split, not TOTAL PSS only (T5.1):** during every pressure step (DEV-4B-PRESSURE, Gemma, A-union) sample `adb shell dumpsys meminfo <pkg>` every 5 s and keep Private Dirty, Private Clean, Native Heap, the .gguf mmap row and SwapPss (TOTAL PSS stays the gate number). Read a kill against Private Dirty + SwapPss: mmapped GGUF pages are clean file-backed and reclaimable (Android memory docs, lmkd).
- **Load flags recorded now (T5.2, grep 2026-10-21):** bench app engine `LlamaEngine.ts` l.291–292 initLlama `use_mmap: true`, `use_mlock: false`; bench overrides (`src/engineOverrides.ts`) allow `useMlock`, used only by litelat-05-mlock (10-20; its bench.json logs use_mlock true). Maintainer RC (android-native, wt/native-qa 5f8cc8f4): default `LoadMode.MMAP` (EngineTweaks.kt l.97); preset "Run Boar Run" asks `MMAP_MLOCK`, which the code notes Android refuses (0 MB locked, X6, 10-15). Rule: never enable mlock on the 8 GB phone; if the RC is run on a preset, write the preset name in the sheet.
- **Battery (T8.3, 0 extra phone time):** at start and end of every run log `adb shell dumpsys battery | grep -E 'level|charge counter'` (level %, charge counter µAh) next to the thermal line; report µAh per answered question per step.
- **Decode trend (T6.4):** per step report decode tok/s mean of the first third vs the last third of calls next to the p50 (thermal drift; Gemma 10.5 → 7.0 tok/s precedent).


- H6 (optional, after H4; needs the v3 packs on the phone): time one full int8 chunk-vector scan per v3 pack (factbook, firstaid, medlineplus; wikivoyage if built) cold and warm, PSS delta; desktop prior 0.2-0.4 s per query warm for 550k chunks (web tick 44, unverified). 0 judge; feeds G2-FULLKIT phone cost / T_8GB.
  - H6 reading rule (web W81): compare the cold scan time with the storage bound (vec bytes / measured sequential read MB/s) and the warm time with the memory bound; a cold time far above the storage bound means page-cache misses, not compute.

- H7 (optional, only if the app maintainer's full-Wikipedia shards are already on the phone; not part of the 117 min): time a question-stem lookup and a whole-index BM25 on the 18.4 GB shards cold and warm, idle and with the 1.7B loaded; compare with the competitor's Pixel 8 Pro numbers (QUEUE WEB row 10-22 15:34). 0 judge; feeds NOTE-6.
