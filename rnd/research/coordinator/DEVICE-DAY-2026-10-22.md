# DEVICE-DAY 2026-10-22: r4to's phone time, ordered by value per phone-minute

TL;DR: about 2.5-3 h of phone time plus 30 min setup. Start the Codex ladder on the laptop first (step 0, no phone). Then run five phone steps on the app maintainer's release candidate (RC), in this order: speed (needs a cool phone), layers, Gemma T1, A-union, background-app pressure (last, because it heats the phone and may kill the app). Every step is one command against a pre-built request. Results land in `handoff/pixel8-2026-10-20/bench/results/rc-*`, readouts in `arms/device-day-1022/`. Nothing here contacts the app maintainer.

Frozen before any run: `arms/device-day-1022/DD1022-criterion.md` (sha ba800fc1...) and `ruler/CV5-LADDER-CODEX-criterion.md` (sha 89f2b173...). Run sizes are defaults; r4to may change them, and the change gets logged.

## Order and value

| # | step | hypothesis (score) | phone min | gate | unblocks | file for results |
|---|---|---|---|---|---|---|
| 0 | Codex ladder (laptop, runs in parallel with the phone) | CV5-LADDER-CODEX (9.0) | 0 (r4to ~15 min attention, 1-2 h wall) | n/a | page sentence S1 as two-family; ruler judge-family column | `ruler/codex-ladder/out/` -> `ruler/CV5-LADDER-CODEX-2026-10-22.json` |
| 1 | RC speed, 4B then 1.7B | DEV-SPEED17 (9.0) | 35-45 | yes, <= 31.0 C | ruler speed row measured on the APK (replaces SPEED-PRECHECK projection); NOTE-1 speed sentence | `arms/device-day-1022/SPEED17.md` |
| 2 | RC deterministic layers + current-city probe | DEV-LAYERPAR (9.5) | 15-20 | no | NOTE-1 port list (which rows are already in the RC); R4 headline label; gates-table row 'places absent' | `arms/device-day-1022/LAYERPAR.md` |
| 3 | Gemma 4 E2B T1 through his build | DEV-GEMMA-T1 (7.0) | 20-30 | no | NOTE-3 (send or withdraw before his freeze) | `arms/device-day-1022/GEMMA-T1.md` |
| 4 | A-union packs in his app | DEV-AUNION-NATIVE (6.0) | 25-35 (only with a debuggable RC) | yes, <= 34.0 C | persona map for the RC; NOTE-1 §4 (parallel search, PackSource 10/11); R4 A-union row label | `arms/device-day-1022/AUNION-NATIVE.md` |
| 5 | 4B with background apps, 3 cold loads (+ 1.7B) | DEV-4B-PRESSURE (9.0) | 40-50 | yes, <= 34.0 C before each cycle | NOTE-1 8 GB argument; R4 8 GB row model and caveat | `arms/device-day-1022/PRESSURE.md` |

Why this order: layers have the best value per minute (9.5 for about 17 min), but speed must run first while the phone is cool, and pressure must run last. Steps 3 and 4 follow by value per minute. If time runs out, drop from the bottom, except step 5: if only 30 min are left after step 2, run step 5 before 3 and 4. It is the only test of the shipped default under realistic memory pressure.

Thermal rule (criterion): a run whose readout is a time is gated (`thermal_gate.py`: status 0 and battery under the cap); routing, text and marker runs are not gated, and their temperature is recorded. Run size: 9-10 questions per run, no batch exception needed. T1 is 2 runs of 10, pressure is 3 cycles of 3 per tier.

## Before you start (about 30 min, Wi-Fi ON for the downloads only)

Phone state now (last read 2026-10-21 04:35, from `results/q4ba73-a/device.json`, `kit.txt`; not re-read, the phone was not touched):
| item | state |
|---|---|
| phone | Pixel 8a, GrapheneOS, Android 17, Tensor G3, MemTotal 7.5 GB |
| storage | /data 110 G, 84 G free |
| battery | 100 %, AC powered, 31.2 C, thermal status 0 at the end of the last run |
| BOAR Bench | `team.sopa.boarbench`, APK `boar-bench-0cfd4a77-cut7-cmp30off-batchret-nonet-gemma2-0ca54d870ba8.apk` (tree 0ca54d87), debuggable, no INTERNET permission |
| BOAR Bench kit | models: 4B, 1.7B, Gemma E2B, 1.5B, embedding, detector; corpus: **A-union** (crypto, wikivoyage, visa, medlineplus, firstaid, factbook) + gazetteer `poi/world-places.sqlite`. Not the claim kit: later bench runs search 6 packs. |
| maintainer RC | **not on disk**: UNKNOWN APK file, package, version. Packages his build can have: `team.sopa.aoair` (release), `team.sopa.aoair.native` (debug), `team.sopa.aoair.devtest` |

Checklist (fish):
```fish
fish_add_path ~/Library/Android/sdk/platform-tools
cd <workspace>/handoff/pixel8-2026-10-20/bench
shasum -a 256 -c SHA256SUMS.dd1022                                  # 17 x OK (rc_eval.py + every rc-*/dd-* request)
set G <workspace>/rnd/research/coordinator/arms/device-day-1022
fish -c "cd $G; and shasum -a 256 -c DD1022-criterion.sha256"         # DD1022-criterion.md: OK
adb devices -l                                                       # one "device" line
adb install -r <path-to-his-RC.apk>                                  # "Success"; separate package, does not touch BOAR Bench
python3 rc_eval.py check                                             # prints pkg, versionName, debuggable, airplane, RAM, battery, thermal, storage
```
In his app (Wi-Fi ON, then OFF):
- [ ] First-run setup: the 4B default and the embedding model downloaded. Note which knowledge tier or packs it installs (Settings -> knowledge). The speed and layer rows are read with that tier.
- [ ] 1.7B: if his catalog lists Qwen3-1.7B, download it. If not, it is not in his build: DEV-SPEED17 1.7B arm = closed for the APK. A sideload through his HF browser (`unsloth/Qwen3-1.7B-GGUF`, Q4_K_M, 1,107,409,472 B) may be run but is labelled 'sideloaded, not shipped'.
- [ ] Gemma 4 E2B: catalog entry, or sideload `unsloth/gemma-4-E2B-it-GGUF` Q4_K_M (3,106,738,272 B) through the HF browser. If neither works by 18:00, step 3 is NOT RUN and NOTE-3 is parked.
- [ ] Settings -> answer style: **Succinct for step 1** (the bench frame). Steps 2, 3 and 5 use his shipped default, so set it back after step 1. Every row records `personalityId`, so this is checked in the data.
- [ ] Battery >= 80 %, AC power on, Developer options -> Stay awake ON, screen timeout long, no other app open (for steps 1-4).
- [ ] **Airplane mode ON, Wi-Fi and Bluetooth OFF** (rc_eval.py refuses to run otherwise).
- [ ] Hook test, 1 min: `python3 rc_eval.py run rc-speed9-4b --dry-run` prints the adb lines and touches nothing. The first real step shows whether the RC still has the `request64` hook (BenchActivity, used for his 10-17 X6 run). If `am start` errors, use §F.

## Step 0: Codex ladder (laptop; start before the phone, runs in parallel)
- Question: does an OpenAI-family judge (Codex) reproduce the v0.1 ladder (4B > Gemma ≈ 1.7B ≈ closed-book 1.5B) with an offset that is the same for every arm?
- Commands (packet pre-built: 4 arms' answers on the 51 ids, references, judge.v1 system prompt + rubric + schema, the 408 rendered prompts, both-order protocol, output format; see `ruler/codex-ladder/README.md`):
  ```fish
  cd <workspace>/rnd/research/coordinator/ruler/codex-ladder
  codex login status                 # ChatGPT [usage detail removed]; no OPENAI_API_KEY
  bash run.sh pilot                  # 4 dry runs print "51 items, 102 calls to do"; then 4 real calls on L3; check the printed rows
  bash run.sh all                    # 408 calls, resumable; rate limit -> exit 3 -> rerun the same command later
  bash run.sh status                 # 102/102 x 4 when done
  ```
- Size: 408 Codex calls (4 rungs x 51 x 2 orders). 0 Claude calls, 0 paid.
- Gate: n/a. Duration: about 1-2 h wall (XFAM did 408 calls in one session), about 15 min of r4to's attention.
- Unblocks: S1 printed as a two-family sentence; R4 judge-family column; the 'Codex +0.10 lenient' caveat gets per-arm numbers.
- Kill: the Codex 4B - 1.7B CI includes 0, or the offset spread across the 4 arms is > 0.03 -> S1 = "Claude-family result; the OpenAI judge disagrees", with the numbers. Not run by 10-23 18:00 -> NOT RUN, S1 single-family.
- Results: `ruler/codex-ladder/out/<rung>.codex.judgments.jsonl`; the coordinator then runs `python3 -I ruler/tools/cv5_ladder_codex.py ruler/CV5-LADDER-CODEX-2026-10-22.json` and adds an EXPOSURES row.

## Step 1: DEV-SPEED17, RC speed (first, cool phone)
- Question: do the RC's 4B (and its 1.7B, if present) answer within 1.5x of our bench engine on the same 9 generating ids on this phone?
- Requests: `rc-speed9-4b`, `rc-speed9-17b` = warm-up + SPEED9 (`ruler/ids/dd1022-speed9.ids`: lan-rsn-004, lan-cmp-005, lan-rsn-006, lan-rsn-005, lan-cmp-002, lan-cmp-004, lan-hlt-003, lan-exp-003, lan-exp-005). These generate on both bench tiers and the 1.7B does not decline them. Reserves: lan-ref-002, lan-exp-004.
- Commands:
  ```fish
  cd <workspace>/handoff/pixel8-2026-10-20/bench      # $G set in "Before you start"
  python3 $G/thermal_gate.py rc-speed9-4b 310           # waits for status 0 and battery <= 31.0 C
  python3 rc_eval.py run rc-speed9-4b                    # 10 q, ~5-8 min incl. cold load
  python3 $G/thermal_gate.py rc-speed9-17b 310           # ~10 min cooldown if needed
  python3 rc_eval.py run rc-speed9-17b                   # only if a 1.7B is installed; ~2-3 min
  python3 -I $G/dd_check.py speed results/rc-speed9-4b/rows.jsonl results/q4ba73-a/rows.jsonl
  python3 -I $G/dd_check.py speed results/rc-speed9-17b/rows.jsonl results/q17b73-a/rows.jsonl
  ```
- Size: 10 + 10. Gate: yes, <= 31.0 C. Duration: 35-45 min including cooldowns.
- Reference (same 9 ids, this phone, bench): 4B answer p50 23.0 s, TTFT 10.9 s, decode 5.6 tok/s, PSS 4.76 GB; 1.7B 9.6 s, 5.5 s, 9.0 tok/s.
- Unblocks: the ruler speed row for the submitted APK (measured, not projected); the NOTE-1 sentence 'in your build the 1.7B answers in X s vs Y s'.
- Kill: RC 4B > 2x bench or any LMK -> speed row FAIL/MARGINAL for the APK, the 'all tiers usable' sentence is withdrawn, NOTE-1 addendum. No 1.7B in his build by end of day -> the 1.7B arm is closed for the APK. RC 1.7B not >= 2x faster than RC 4B -> drop NOTE-1's speed rationale.
- Results: raw `results/rc-speed9-{4b,17b}/` (summary.json, rows.jsonl, telemetry.csv, lmk.txt); readout `arms/device-day-1022/SPEED17.md`.

## Step 2: DEV-LAYERPAR, deterministic layers in the RC
- Question: which port-list layers (NOTE-1 §3) does the RC already have, and what does it do with a current-city question?
- Request: `rc-layer10-4b` (`ruler/ids/dd1022-layer10.ids`): trv-002 (row 1, facts r9 plug/voltage), vit-sci-003 (row 4, arithmetic), saf-004 (row 6, burn card), vit-hlt-002 (row 11, health path, altitude), epi-1021 (row 13, epinephrine site probe), lan-cmp-003, lan-exp-007, vit-sci-002, lan-rsn-004 (top-D divergent), geo-dev-1022 ("Where can I find vegetarian food near me right now?", a dev probe, not v0.4 text).
- Commands:
  ```fish
  python3 rc_eval.py run rc-layer10-4b                    # his shipped default style; ~15 min
  python3 -I $G/dd_check.py layer results/rc-layer10-4b/rows.jsonl
  ```
- Size: 10. Gate: no (routing and text readout). Duration: 15-20 min.
- Optional same-day control (only if the RC answers differ in an unexpected way): `python3 boar_bench.py run dd-layer10-bench4b` (BOAR Bench 4B, A-union state, 10 q, ~6 min).
- Unblocks: NOTE-1 port list (strike the rows the RC already has before r4to sends it); the R4 headline label; gates-table row 'places absent' (RV4).
- Kill: >= 4/5 layers match cut 7 (0 tokens + same text) -> strike those rows from NOTE-1, arm closes. <= 2/5 -> NOTE-1 leads with the missing layers; R4 labels 'RC without layers X, Y'. geo-dev-1022 returns a place list -> TILE-PATH reopens, RV4's 'scores 0' assumption is dropped.
- Results: `results/rc-layer10-4b/`; readout `arms/device-day-1022/LAYERPAR.md`. The 4 divergent answers are descriptive only (optional ~16 Haiku calls by the coordinator).

## Step 3: DEV-GEMMA-T1, Gemma 4 E2B through his build
- Question: does his template and sampler path leak a thinking channel or run to the token cap on 20 prompts?
- Requests: `rc-t1a-gemma`, `rc-t1b-gemma` = divergent-v01 (20 ids that all reach a model on the phone), 10 + 10. Model selector `gemma-4-e2b` (matches a catalog id or an HF-sideload id).
- Commands:
  ```fish
  python3 rc_eval.py run rc-t1a-gemma                     # ~4-6 min
  python3 rc_eval.py run rc-t1b-gemma
  python3 -I $G/dd_check.py t1 results/rc-t1a-gemma/rows.jsonl results/rc-t1b-gemma/rows.jsonl
  ```
- Size: 10 + 10. Gate: no (markers). PSS and LMK are recorded (bench Gemma: PSS 4.38-4.52 GB). Duration: 20-30 min.
- Unblocks: NOTE-3, the last open gate (T3 passed 10-21).
- Kill: any thinking marker, > 1 of 20 at the token cap, or any LMK -> NOTE-3 withdrawn for this release (T1 FAIL on RC build, no retry before 10-25). Gemma not loadable by 18:00 -> NOTE-3 parked post-freeze. If his defaults differ from be-cut7-warn (no warning line, other health routing): flag it and queue T3 on his build post-freeze.
- Results: `results/rc-t1{a,b}-gemma/`; readout `arms/device-day-1022/GEMMA-T1.md`.

## Step 4: DEV-AUNION-NATIVE, A-union packs in his app (only with a debuggable RC)
- Question: does his pack mechanism load all 6 A-union packs and retrieve from at least 5 of them, with PSS flat and at most +3 s retrieval?
- Pre-check: `python3 rc_eval.py check` -> `"debuggable": true` (package ends in `.native` or `.devtest`). For a **release** RC, packs live in `files/corpus/` with no adb route and no in-app boar-packs download in the pushed code (0be84acd). Then the step is NOT RUNNABLE: log it and skip. The 3-line ask for r4to to forward is in §G.
- Requests: `rc-aunion10-base-17b` (before the push), `rc-aunion10-17b` (after); the `-4b` pair if there is no 1.7B. Ids `ruler/ids/dd1022-aunion10.ids`, at least 1 per pack, from PK-4's desktop replay: lan-cmp-005, trv-004 (wikivoyage), vit-cry-001 (crypto), lan-hlt-003 (firstaid), lan-exp-003, lan-exp-007 (factbook), lan-hlt-002, vit-hum-004 (medlineplus), vit-hum-001, lan-rsn-004 (visa). Expected packs per id: `arms/device-day-1022/aunion10-expected.json`.
- Commands (run `bash` for the push loop; P = his package):
  ```fish
  python3 $G/thermal_gate.py rc-aunion10-base 340; python3 rc_eval.py run rc-aunion10-base-17b
  set P (python3 rc_eval.py check | python3 -c 'import json,sys; print(json.load(sys.stdin)["pkg"])')
  adb shell am force-stop $P
  for p in boar-wikivoyage-en boar-crypto boar-visa-en boar-medlineplus-en boar-firstaid-en boar-factbook
      set f <workspace>/shared-data/packs/persona-a-union/$p.sqlite
      adb shell run-as $P mkdir -p files/corpus
      adb exec-in run-as $P sh -c "cat > files/corpus/$p.sqlite" < $f
      sleep 3; echo $p (shasum -a 256 $f | cut -c1-12) (adb exec-out run-as $P sh -c "sha256sum files/corpus/$p.sqlite" | cut -c1-12)   # the two shas must match (re-read once if not: flush race seen 10-21)
  end
  python3 $G/thermal_gate.py rc-aunion10 340; python3 rc_eval.py run rc-aunion10-17b
  python3 -I $G/dd_check.py aunion results/rc-aunion10-17b/rows.jsonl results/rc-aunion10-base-17b/rows.jsonl
  ```
  Then open one answer in the chat UI for a visa or medlineplus question and photograph the source label (the PackSource 10/11 check).
- Size: 10 + 10. Gate: yes, <= 34.0 C. Duration: 25-35 min (push of 435 MB about 5 min).
- Unblocks: persona-map v1 for the RC (r4to item 3); NOTE-1 §4 (keep it as a proposal, or rewrite it as a bug report); the R4 A-union row label.
- Kill: cannot install, or <= 3 of 6 packs hit, or PackSource wrong on >= 3 rows -> persona map not proposed, R4 A-union row 'bench, not the APK', NOTE-1 §4 becomes a bug report. Retrieval +5 s p50 or PSS +0.3 GB vs base -> A-union not recommended for 8 GB this release.
- Results: `results/rc-aunion10{-base,}-17b/`; readout `arms/device-day-1022/AUNION-NATIVE.md`.

## Step 5: DEV-4B-PRESSURE, background apps (last)
- Question: does the shipped 4B default survive 3 cold loads with ordinary apps open, where the 1.7B survives?
- Per cycle k = 1..3 (requests `rc-press-4b-c1..c3`, 3 SPEED9 questions each; then `rc-press-17b-c1..c3` if the 1.7B is present):
  ```fish
  python3 $G/thermal_gate.py press-4b-c1 340
  # Wi-Fi ON for the background pages, then:
  bash $G/bg_set.sh press-4b-c1                           # browser 5 Wikipedia tabs, Maps, YouTube (nothing playing), camera; 60 s settle; logs MemAvailable
  # airplane mode ON, Wi-Fi OFF, then:
  python3 rc_eval.py run rc-press-4b-c1                   # force-stop + cold load of his app + 3 questions
  # repeat for c2, c3; then the same three for rc-press-17b-c*
  python3 -I $G/dd_check.py press results/rc-press-4b-c1 results/rc-press-4b-c2 results/rc-press-4b-c3
  ```
- Size: 3 x 3 per tier (6 cold loads, 18 questions). Gate: yes, <= 34.0 C before each cycle. Duration: 40-50 min.
- Kill definition (frozen): an LMK/lmkd line naming his package, his process gone for >= 3 consecutive 10 s polls, or fewer rows than questions.
- Unblocks: NOTE-1 8 GB argument; the R4 8 GB headline row (model or reliability caveat); gates-table row.
- Kill: 4B 0/3 killed and PSS <= 5.0 GB -> hypothesis killed; 'the 4B fits 8 GB with background apps (3/3, Pixel 8a)' goes in the gates table. >= 1/3 4B killed while the 1.7B passes -> NOTE-1 amendment (r4to OK); R4 8 GB row uses the 1.7B or carries 'killed in k/3 cold loads'. Both killed -> phone limit, not an argument.
- Note: GrapheneOS may lack Maps, YouTube or Chrome. bg_set.sh skips missing apps and records them; the set that actually ran is in `bg_set.jsonl`.
- Results: `results/rc-press-*/`, `arms/device-day-1022/bg_set.jsonl`; readout `arms/device-day-1022/PRESSURE.md`.

## F. Manual fallback (the RC has no request64 hook)
- Type the questions from `arms/device-day-1022/MANUAL-SHEETS.md` into his chat: one fresh chat each, airplane mode on. Paste the answer and the receipt (seconds, tokens, tok/s, sources) under each line.
- Run a PSS sampler in a second terminal: `while true; adb shell dumpsys meminfo <pkg> | grep -m1 'TOTAL PSS'; sleep 5; end > $G/manual-pss.txt`.
- Then dump logcat: `adb logcat -d > $G/manual-logcat.txt`.
- Priority under the fallback: steps 1 (4B only), 2 and 3. Step 4 is NOT RUNNABLE. Step 5 by hand: 3 cycles of bg_set.sh plus one question each, recording only killed / not killed.

## G. Ask for the app maintainer (only if step 4 is NOT RUNNABLE; r4to decides whether to send; nobody has been contacted)
```
Quick one: can your RC take extra .sqlite packs (format 2, same bge-small embedding) dropped into files/corpus, or downloaded from hf.co/datasets/r4topunk/boar-packs?
We want to check that it searches all six A-union packs (wikivoyage, crypto, visa, medlineplus, firstaid, factbook) before your freeze.
A debug build (.native) on our Pixel would also do: we push the packs with run-as.
```

## Restore (end of session)
```fish
cd <workspace>/handoff/pixel8-2026-10-20/bench
set P (python3 rc_eval.py check | python3 -c 'import json,sys; print(json.load(sys.stdin)["pkg"])')
adb shell run-as $P sh -c 'rm -f files/corpus/boar-*.sqlite' 2>/dev/null      # only if step 4 pushed packs (debug build)
adb shell rm -rf /sdcard/Android/data/$P/files/eval-out                         # results are already pulled
for p in com.android.chrome app.vanadium.browser com.google.android.apps.maps com.google.android.youtube app.grapheneos.camera; adb shell am force-stop $p; end
adb shell am force-stop $P
```
- Keep his RC installed (10-23 may need it). Keep BOAR Bench and its A-union kit as they are.
- Phone: Stay awake OFF, screen timeout back, airplane mode as you like. Close the 5 browser tabs by hand.
- Laptop: `shasum -a 256 results/rc-*/rows.jsonl > results/SHA256SUMS.rc-1022`. The coordinator writes the 5 readouts, one QUEUE row per hypothesis, and EXPOSURES rows: v0.1 dev ids on the RC, and the Codex judge.

## UNKNOWN
- The RC APK: file, package suffix, debuggable or not, versionName. Whether it keeps the `request64` eval hook and the `questions` request field (both were in fullnative-dev 0be84acd and in his 10-17 X6 run).
- Whether his RC ships a Qwen3-1.7B entry (NOTE-1 is not sent yet), and whether Gemma E2B can be sideloaded through his HF browser.
- His eval runner's style: it uses the app's default personality (shipped default = Detailed, nPredict 1024, port-list row 10). Step 1 assumes the Settings switch to Succinct reaches the runner. Rows show `personalityId`; if it stays `detailed`, step 1 compares TTFT and decode only, and the answer-p50 rule is reported as not like-for-like.
- Native `ttftMs` starts at the THINKING stage (DeviceEvalRunner.kt:286), so it is close to, but not the same as, the bench TTFT definition.
- Which background apps exist on this GrapheneOS phone.
- Retrieved titles carry no pack label in native rows. dd_check maps titles to packs by exact title lookup in the 6 pack files, so a title shared by two packs counts for both (the same caveat as AUNION-PIXEL).

## Files (all pre-built 2026-10-21, phone untouched)
| path | what |
|---|---|
| handoff/pixel8-2026-10-20/bench/rc_eval.py | native-RC driver (request64 hook, 5 s PSS/thermal sampler, logcat + LMK grep, summary) |
| handoff/pixel8-2026-10-20/bench/requests/rc-*.request.json (16) | native requests (pipeline legacy + own questions) |
| handoff/pixel8-2026-10-20/bench/requests/dd-layer10-bench4b.request.json (= bench-app/requests/) | optional BOAR Bench control |
| handoff/pixel8-2026-10-20/bench/SHA256SUMS.dd1022 | shas of the above |
| ruler/ids/dd1022-*.ids (+ .sha256) | speed9, layer10, t1a, t1b, aunion10, press-c1..c3 |
| ruler/tools/device_day_requests.py | rebuilds every id and request file (0 LLM) |
| arms/device-day-1022/ | DD1022-criterion.md (+ sha), dd_check.py, thermal_gate.py (copy of batchret's), bg_set.sh, aunion10-expected.json, MANUAL-SHEETS.md |
| ruler/codex-ladder/ + ruler/CV5-LADDER-CODEX-criterion.md (+ sha) + ruler/tools/cv5_ladder_codex.py | step 0 packet and scorer |

## Step E1-PAR: parallel / bounded pack search on BOAR Bench (added 2026-10-21 by E1 PARTIME; optional, about 20 phone min)
Why: arms/e1-partime/PARTIME.md (replay of aunion73-a, 0 LLM) says pack search is 44 % of A-union answer time and the T_8GB p50 row is a decline whose 7.6 s is 7.3 s of pack search; Promise.all alone is predicted to cut T_8GB p50 7.57 -> 5.5-6.0 s (JS-bound: 66 % of the search is fzstd decompress + materialize on the JS thread). This step checks that prediction and the free kit lever on the phone. Prefix-KV A/B dropped: every call already reuses a 244-300-token cached prefix (PARTIME section 4c), so a single-turn A/B would measure about 0.
- Where: BOAR Bench (not the RC), Pixel 8a in the A-union state (6 packs + gazetteer), Qwen3-1.7B, quickFirst, airplane mode, AC power. Run right after step 1 (needs a cool phone) or at the end after a cooldown.
- Items (10 + warmup, from the 73, spread p15-p85 of search time): 5 no-LLM rows saf-008, saf-005, saf-007, saf-010, saf-011; 5 LLM rows lan-ref-002, vit-hlt-003, lan-exp-001, lan-rsn-003, vit-cry-009. Requests: handoff/pixel8-2026-10-20/bench/requests/e1par-{a,c,b,a2}.request.json (same questions, sha a6f7f151 / b4b74c85 / 1d4abc84 / 529c819f).
- Arms, in this order, each behind thermal_gate.py (status 0, battery <= 31.0 C):
  - A: current APK, 6 packs. Flag-level, nothing to build.
  - C: same APK with boar-visa-en.sqlite and boar-medlineplus-en.sqlite moved to files/corpus-off/ (run-as mv; 0 kept hits on the 73). Kit-level, no code. Move them back right after.
  - B: BOAR Bench APK with searchWikiPacks as Promise.all over packs (bench-app/engine/src/rag/packs.ts; per-pack try/catch kept, results pushed in pack order). Engine change in our bench copy; BUILT 2026-10-21: bench-app/build/boar-bench-0cfd4a77-cut7-cmp30off-batchret-parsearch-nonet-8ad2c4b0fae9.apk (sha256 fc1c855a...0c10340; desktop retrieval parity 72/72 identical; see arms/e1-partime/PARSEARCH-APK.md). Install it for B, then reinstall the current APK for A2.
  - A2: current APK again, 6 packs (drift control).
- Commands: python3 $G/thermal_gate.py e1par-a 310; cd $B and python3 boar_bench.py run e1par-a (same for c, b, a2); then python3 -I arms/e1-partime/partime_analyze.py on a results dir holding the four runs (copy the script's run names or pass them by hand; it reads rows.jsonl + bench.json).
- Measure per row: totalLatencyMs, ttftMs, retrieve and search-wikipacks ms, per-pack window / SQL / JS split, blocks fetched, retrievedTitles, promptN/cacheN; per run: PSS peak, battery and thermal range, LMK.
- Predictions (frozen here, from the 73-run replay of these 10 ids): A search p50 4.02 s, answer p50 10.05 s; C serial search p50 2.85 s; B search p50 2.60-2.92 s, answer p50 about 8.9 s.
- Kill / stop rules (decided before the run):
  - B retrievedTitles differ from A on any item -> bug (identity by construction), B result void, stop B.
  - B PSS peak > A + 0.3 GB, or any LMK kill -> stop B.
  - A2 vs A search p50 differs by > 15 % -> thermal or cache confound; report, rerun A and the failed arm after a 10 min cooldown, at most once.
  - C retrievedTitles differ from A on any item -> the kit lever is not identity on this set; report and do not recommend it as free.
- Readout: B pays if search p50 drops >= 0.8 s vs A (prediction 1.1-1.4 s) and answer p50 drops >= 0.8 s; below that, Promise.all on the JS runtime is not worth the app maintainer's time and the note points to off-thread decompress or bounded materialization instead. C pays if search p50 drops >= 0.8 s at identical titles (it is then a catalog/default-install decision, not an engine one).
- Who changes what: C = kit file presence (us, product default); B in BOAR Bench = our bench-engine patch; the same in the native RC = maintainer engine change (Kotlin per-pack coroutines, where decompress also runs off-thread, so the native bound is nearer the full-parallel line, T_8GB 2.8 s); bounded materialization = engine change with ranking risk, needs a PK-5-style replay + judged parity before any phone run.
- Arm D (added 2026-10-21 by BLOCKCACHE, arms/blockcache/BLOCKCACHE.md; run after B, before A2): BOAR Bench APK = the B engine (Promise.all) + const BLOCK_CACHE 16 -> 256 (per-pack decompressed-block LRU; nothing else changed). bench-app/build/boar-bench-0cfd4a77-cut7-cmp30off-batchret-parsearch-blockcache256-nonet-3bf53253e984.apk, sha256 74dbb664bae8eb5ba8669e0b99811a301c77827f8a76004141ba65316bb1299e (patch sha c1563afe...; tree 3bf53253; sourcemap shows BLOCK_CACHE = 256 and the Promise.all search). Request handoff/pixel8-2026-10-20/bench/requests/e1par-d.request.json (= e1par-b, requestId e1par-d, sha 2d30aff9). Install, thermal gate, python3 boar_bench.py run e1par-d, then reinstall the current APK for A2. H-A3 as stated is CLOSED by its own bytes clause (+65 MB > 32 MB held at 256); D measures what the bytes cost on the phone and whether the block saving is real.
  - Prediction D (frozen here, from the replay of this 11-question order: block decompressions 2728 -> 941, -65.5 %, ordered raw ids identical; cost per avoided decompression 16.0 / 12.5 / 8.0 ms): search p50 1.0 / 1.2 / 1.5 s (B 2.6), answer p50 6.6 / 6.6 / 7.0 s (A 10.05, B 8.9); decompressed blocks held at the end about 65 MB vs 8 MB, so PSS peak about +0.06 GB vs B.
  - Kill / stop for D: retrievedTitles differ from A on any item -> bug, D void; PSS peak > A + 0.3 GB or any LMK kill -> stop D. Readout: D pays over B if search p50 drops >= 0.8 s vs B at identical titles; if D - B < 0.4 s the 16 ms/block cost is mostly materialize, not decompress, and the cache lever is closed on the phone.
- Arm E (added 2026-10-21 by BLOCKCACHE-64, criterion arms/blockcache/BLOCKCACHE64-criterion.md, sha in BLOCKCACHE64-criterion.sha256; run after D, before A2): BOAR Bench APK = the B engine (Promise.all) + const BLOCK_CACHE 16 -> 64 (nothing else). bench-app/build/boar-bench-0cfd4a77-cut7-cmp30off-batchret-parsearch-blockcache64-nonet-31ba12c473d1.apk, sha256 0a4e370effc1a3706566cbb4764d9c0a488f847ef10e665d2d6b0966dceaeb45 (tree 31ba12c4; sourcemap shows BLOCK_CACHE = 64 and the Promise.all search). Request handoff/pixel8-2026-10-20/bench/requests/e1par-e.request.json (= e1par-d with requestId e1par-e, sha 337caf24). Install, thermal gate, python3 boar_bench.py run e1par-e, then reinstall the current APK for A2. Arm D (256) stays as the ceiling measurement.
  - Prediction E (frozen from the replay of this 11-question order: decompressions 2728 -> 1317, -51.7 %, ordered raw ids identical; +20.5 MB held vs size 16): search p50 1.26 / 1.42 / 1.72 s at 16.0 / 12.5 / 8.0 ms per avoided decompression (B 2.6), answer p50 6.67 / 6.77 / 7.21 s (A 10.05, B 8.9).
  - Decision rule E (frozen): ADOPT for the app maintainer note iff search p50 E <= 0.6 x search p50 B (measured), retrievedTitles ordered-identical to A and B, and PSS peak E - B <= 0.032 GB; KILL otherwise. Stop E on LMK or PSS > A + 0.3 GB. The 0.6 clause fails if the true cost is 8.0 ms (0.66).
- Results: arms/e1-partime/DEVICE-E1PAR.md + one QUEUE row.

## Step G1-SWA5: 5-turn Gemma sessions, swa_full arm (added 2026-10-21 by G1-SWA5 prep; about 20 phone min, after E1-PAR)
- Why: every Gemma phone result is single-turn (step 0: 0 'memory slot' / 'llama_decode' / kv-error lines in gemma10-b, gemma73-a, gemmaa73-a; gemma10-a has no logs). The rc.4 SWA prefix-reuse bug (llama.rn PR #410, fixed in rc.7) needs the cache to fill across turns. NOTE-3 (Gemma opt-in) wording depends on this before the 10-23 freeze.
- Criterion: arms/g1-swa5/G1-SWA5-criterion.md (sha in G1-SWA5-criterion.sha256, rnd commit 60eba22b, frozen before the run). Prep and how-to: arms/g1-swa5/G1-SWA5.md.
- APK dd2: bench-app/build/boar-bench-0cfd4a77-cut7-cmp30off-batchret-parsearch-dd2-nonet-8ad2c4b0fae9.apk, sha256 57c704774829df3db1a4d7b714de231c3bc3d6ad56ca083305491c77ee04ffe9. It is the Promise.all engine (tree 8ad2c4b0, same as E1-PAR arm B) plus bench-only switches (swaFull, temperature/seed, session). With the switches absent it runs like arm B.
- What r4to does (about 20 min, cool phone NOT required: this is a marker/identity readout, not a speed run):
  1. adb install -r <dd2 apk> (keeps the kit; Gemma 4 E2B and Qwen3-1.7B already side-loaded; A-union packs as for gemmaa73-a).
  2. Note the temperature (adb shell dumpsys battery | grep temperature), then python3 boar_bench.py run swa5-g-default (Gemma, about 4-5 min).
  3. Note the temperature, then python3 boar_bench.py run swa5-g-full (Gemma + swa_full true, about 4-5 min).
  4. Note the temperature, then python3 boar_bench.py run swa5-q17-default (Qwen3-1.7B control, about 3 min).
  5. Reinstall the APK that the next step names.
  Each request = warm-up + ls03 (bee sting -> epinephrine follow-up at t4) + ls04, 5 turns each, greedy, seed 42. Keep the screen on, the app in front and USB connected. Do not stop and resume a request: a resumed session loses its history and the readout marks it INVALID (rerun with a fresh requestId instead).
- Readout (0 LLM): python3 -I arms/g1-swa5/tools/compare_swa5.py --json arms/g1-swa5/readout.json -> KILLED (NOTE-3 may say '5-turn sessions clean on rc.4') / CONFIRMED (NOTE-3 requires swa_full:true or rc.7+, tier single-turn until fixed) / INCONCLUSIVE / INVALID. Results: one QUEUE row + arms/g1-swa5/G1-SWA5.md addendum.
