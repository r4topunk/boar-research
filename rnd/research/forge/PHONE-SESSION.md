# Phone session run sheet: moto g75 (retrieval arms + Probe B + gate probe), adb-driven

TL;DR
- **One app build, run in two modes, carries every retrieval arm:**
  - **D** (debug dev client, JS from Metro = dev mode) and **R** (release-variant JS bundle, debuggable so run-as works).
  - Arms switch per run through the request's `perf` field. No rebuild between arms.
- **Legs:** release-vs-dev base → P-7b packs → +P-8 → +native zstd → +vector cache (2 reps each, on R). Then, back on D: Probe B (4B no-repack) → gate probe leg A (1.5B) → gate probe leg B (4B, **only if Probe B passes**).
- **Total ≈ 4 h 30 without gate leg B, ≈ 5 h 10 with it**: split into two sessions (§0.3).
  - **Session 1**: the perf legs, ≈ 3 h 20; the coordinator proposes it overnight, phone plugged in, screen on.
  - **Session 2**: Probe B + gate legs, ≈ 1 h 10 / 1 h 50.
- **Coordinator decisions** (2026-10-03):
  - Probe B runs with USB plugged (approved; same condition for control and arm).
  - Battery level, temperature and time are logged at every leg start and end, and at every gate block start (`arms/session/mark.sh`).
  - Clearing the 4B from `loadCrashedIds` is approved: a scripted step with before and after dumps (L8).
  - The gate probe uses **B5** for leg A (1.5B) and **B6** for leg B (4B: B5 plus Anvil's `b5-to-b6-gate.patch`, sha `21211329…`), per Anvil's re-pin of 2026-10-03.
  - Gate ordering is Anvil's: **ABAB blocks**, each a cold start + 1 unmeasured warm-up + 5 measured items (L9).
- **Every result is in the rows:** each row's `receipt.retrievalStages` carries the stage times and the flags in effect (`perf`), plus `zstdModule` (native module present). `arms/stages_report.py` turns rows into the stage table.

Driver: the coordinator, over adb from the MacBook (Plumb retired). Shell: fish. Phone: moto g75 5G `ZF5252GC7B`, Android 16, 8 GB. Package `team.sopa.aoair`.

Sources merged here (criteria not restated, only referenced):
- Sonar: `sonar/cards/p7b-pack-block-16k.md` (P-7b), `sonar/cards/p8-pack-sql-batching.md` (P-8).
- Anvil: `anvil/specs/probe-b-no-repack-g75.md` (Probe B), `anvil/specs/probe-gate-prefix-cache.md` + `anvil/specs/probe-gate-items.json` (gate probe).
- Forge: `forge/README.md` (L0), `forge/arms/` (patches, requests, scripts), and §6 below (native zstd and vector cache criteria, frozen here before any run).

## 0. Before the session (not timed)

### 0.1 Artifacts (check every one; stop if any is missing)

| What | Where | Check |
|---|---|---|
| Arm patch v1 (native module + flags + stage timers + P-8 gated + `DEVICE_EVAL_ON` polling) | `forge/arms/forge-arms.patch` | sha256 `2e313598874239295…a107f` |
| Patch v2 on top (JS only: eval questions may carry `history`; needed by the gate items) | `forge/arms/forge-eval-history.patch` | sha256 `d12c5779e770bc5f…3517` |
| Kiln step 0 (desktop identity 72/72, flags off and on; unit suite) | Kiln's report | **PASS (Kiln, 2026-10-02 23:04–23:30)**:
- unit suite 1171/1171;
- base vs flags OFF and base vs flags ON (`vectorCache,sqlBatch,nativeZstd`): sources incl. passage text, `retrieval.raw`/`kept`, route and answer text 72/72 identical, 0 errors (`boar-eval/runs/kiln/forge/`);
- flags arrived: pack SQL calls/q 455.5 → 183;
- vector cache engaged: knowledge-DB calls per item go 3 on the first item (signature + load + lexical), then 2 (signature + lexical; the 5,300-row scan is gone). |
| APK **D** (debug dev client) | `builds/android/boar-0cfd4a77-forge-debug-arm64.apk` | 102,100,811 B, sha256 `19134721e2f64f3a…49f3`. Verified on the MacBook: arm64-v8a only; `libboarzstd.so` exports only the JNI and `boar_zstd_*` symbols |
| APK **R** (release JS, debuggable, `EXPO_PUBLIC_DEVICE_EVAL=1`) | `builds/android/boar-0cfd4a77-forge-release-arm64.apk` | 76,495,327 B, sha256 `e3801ee8f6110e23…d010`. `index.android.bundle` 9.66 MB of Hermes bytecode; same signer as D (cert `fac61745…3b9c`), so `install -r` switches between them. Recipe: `rnd/kiln/recipes/forge-build.sh` |
| Metro tree for D: 0cfd4a77 + v1 + v2, node_modules cloned from Plumb's tree | `wt/forge-arms` (own git, 1 commit `71664bd`) | `git -C wt/forge-arms status --short` → empty |
| P-7b packs, local copy | `builds/packs-p7b/` ← copy from `<volume>/boar/kiln/p7b/16/` | `boar-wikivoyage-en.sqlite` 367,288,320 B sha `9db1aa37…`; `boar-crypto.sqlite` 38,010,880 B sha `d08070bf…` |
| Arm requests (72 items + `perf`) | `forge/arms/requests/and-q15-quick-{base,p8,zstd,vcache}.request.json` | `python3 forge/arms/make_arm_requests.py` reprints the shas |
| Probe requests | `forge/arms/requests/probeb-4b10.request.json`; `gate-{A,B}-items1-5`, `gate-{A,B}-items6-10` (each: warm-up `cs-010-warmup` + 5 items in `probe-gate-items.json` order); `gate-{A,B}-spare` (`cs-054`) | `python3 forge/arms/make_probe_requests.py` reprints the shas; all parse with the arm's own request parser |
| Probe B patch (Anvil's 2 lines, as a patch) | `forge/arms/probe-b.patch` | sha `ad67d9a2…c5a9`; applies alone and on top of B5 (checked) |
| Gate patches (Anvil): **B5** for leg A; leg B adds `anvil/exp/chat-routing/arm/b5-to-b6-gate.patch` (sha `21211329…`, B5 + delta = B6 `17a50083…`, checked byte-identical) | `anvil/exp/chat-routing/arm/b5gate-engine.patch` | sha256 `50609046e22fe14c9e3c5b51a187f077fd46db68727ba4e00c50dd093aee9958` = its SHA256SUMS. Applies on `wt/forge-arms`; with Probe B and v1+v2: tsc clean, vitest 1186/1186 (checked). Desktop references re-pinned to B5 in `probe-gate-items.json` |
| Leg marks + memory poll | `forge/arms/session/mark.sh`, `forge/arms/session/meminfo-poll.sh` | `bash -n` clean |

Why D and R: R gives the real release-mode JS cost, which is what users get and what the L0 scaling predicts. D is the same build in dev mode, comparable to every earlier g75 run. Probe B and the gate probe need Metro edits, so they run on D. **R carries patch v1 only: the gate requests (history) are rejected by R's parser. Run them on D.**

### 0.2 Shell setup (every terminal)

```fish
set -x ANDROID_SERIAL ZF5252GC7B
set BE <workspace>/boar-eval
set FA <workspace>/rnd/research/forge/arms
set D runs/devices/2026-10-03/android          # change the date to the session's; paths are relative to $BE
set PKG team.sopa.aoair
set M $BE/$D/legs.csv                          # leg/block marks: time, label, battery level, temperature, plugged
cd $BE; mkdir -p $D
```

**Every leg starts and ends with a mark** (coordinator decision): `bash $FA/session/mark.sh $M <leg>-start` and `… <leg>-end`. Expected output, one CSV line such as `2026-10-03 01:12:40,L3-start,87,33.4,USB`. Gate blocks get a mark at each block start too (L9/L10).

### 0.3 Time budget (estimates; ✱ = measured basis)

| Leg | What | Time |
|---|---|---|
| S0 | setup, install D, Metro, airplane, kit check | 20 min |
| L1 | base-dev ×2 (D) | 31 min (✱ 13.2 min/rep on 0cfd4a77 dev, + 5 min cool-down) |
| L2 | install R, base-rel ×2 | 30 min (~11 min/rep, an estimate: release JS saves ~1.5–2.5 s/answer) |
| L3 | swap to P-7b packs, p7b ×2 | 35 min |
| L4 | +P-8 ×2 | 27 min |
| L5 | +native zstd ×2 (kill rule first, §6.1) | 25 min |
| L6 | +vector cache ×2 | 25 min |
| L7 | restore the 64 KB packs | 5 min |
| | cool-downs between legs (5 × 5 min) + pulls | 30 min |
| **Session 1 subtotal** | | **≈ 3 h 20** |
| L8 | install D, Probe B (2 cold loads × 10 answers on the 4B) | 35 min (4B ~30–45 s/answer, Anvil's frozen prediction) |
| L9 | gate leg A: 4 blocks (A1 B1 A2 B2) × (1 warm-up + 5 items) on the 1.5B | 30 min (~4 min per block + edits) |
| L10 | gate leg B (only if Probe B PASS): same blocks on the 4B | 40 min (~7 min per block) |
| L11 | teardown | 5 min |
| **Session 2 subtotal** | | **≈ 1 h 10 (without L10) / ≈ 1 h 50 (with L10)** |
| **Total** | | **≈ 4 h 30 / ≈ 5 h 10, flagged: two sessions** |

Cuts if only one short session is possible:
- (a) **1 rep for L4–L6:** −40 min. The stage numbers are per row, so 72 rows usually suffice; the p50 retrieval criteria lose their 2-rep check.
- (b) **Drop L1's second rep:** −18 min. The dev ratio comes from one rep.

## S0. Setup (20 min)

1. **Stop Plumb's Metro**, which still serves `wt/plumb-and-0cfd4a77` on 8081:
   - `pkill -f "plumb-and-0cfd4a77/node_modules/.bin/expo start"`
   - Expected: `lsof -i :8081` is empty.
2. **Phone state:**
   - `adb devices` → `ZF5252GC7B device`.
   - `bash $FA/session/mark.sh $M S0-start` → one CSV line with level and temperature.
   - USB plugged (P1 protocol).
   - Screen-off timeout: `adb shell settings put system screen_off_timeout 1800000`.
3. **Events log for the whole session**, in a separate terminal; it is read for LMK kills in L8–L10:
   ```fish
   adb logcat -b events -v time > $BE/$D/events-session.log
   ```
4. **Install D over the current build**; app data (models, packs) is kept:
   - `adb install -r <workspace>/builds/android/boar-0cfd4a77-forge-debug-arm64.apk` → `Success`.
   - **If `INSTALL_FAILED_UPDATE_INCOMPATIBLE`: STOP.** The signature differs. Uninstalling would wipe ~3.9 GB of models and packs, so ask r4to.
5. **Metro from the arm tree:**
   ```fish
   cd <workspace>/wt/forge-arms; npx expo start --localhost --port 8081 --dev-client
   ```
   In another terminal: `adb reverse tcp:8081 tcp:8081`.
6. **Airplane mode on:**
   - `adb shell cmd connectivity airplane-mode enable`, then `adb shell settings get global airplane_mode_on` → `1`.
   - adb over USB keeps working.
7. **Launch on the dev server:**
   - `adb shell am force-stop $PKG`
   - `adb shell am start -a android.intent.action.VIEW -d "exp+boar-app://expo-development-client/?url=http%3A%2F%2Flocalhost%3A8081" $PKG`
   - If the dev launcher still shows its list, tap the `localhost:8081` entry (`adb shell input tap X Y`, coordinates from a screenshot: `adb exec-out screencap -p > s.png`).
   - Expected: Metro prints `Android Bundled … index.ts`, and the app opens on the chat.
8. **Kit check:**
   - `adb exec-out run-as $PKG ls -l files/corpus files/models`
   - Expected:
     - `boar-wikivoyage-en.sqlite` 351092736 and `boar-crypto.sqlite` 36093952;
     - `qwen2.5-1.5b-instruct-q4km.gguf`;
     - `embedding.gguf`;
     - no `*.sqlite-wal` / `-shm` next to the packs.
   - Note any extra file in `files/corpus` (it would be searched too).

## Session 1: retrieval arms

Every run is one line, from `$BE`. The script writes the request, polls every 15 s and pulls the rows. **Expected output:**

```
✓ request be-and-q15-quick-<tag>-r<N> written (72 questions). BOAR must stay open on the chat (screen on); the app polls every 3 s.
  [00:15] accepted 0/72 …
  [00:30] running 1/72 answer:qwen2.5-1.5b-instruct-q4km / vit-…
  …
✓ 72 rows -> runs/devices/…/be-and-q15-quick-<tag>-r<N>/rows.jsonl (status done 72/72)
```

- **If it fails with "not picked up":** BOAR isn't open on the chat, or (R) the build lacks `EXPO_PUBLIC_DEVICE_EVAL=1`.
- **If Android kills BOAR:** reopen it and rerun the same line. It resumes.

**After every run**, check the stages in the new rows:
- `python3 $FA/stages_report.py $D/be-and-q15-quick-<tag>-r<N>`
- Expected:
  - `n=68` (the 4 items with no retrieval are skipped);
  - the `perf=` line shows the arm's flags;
  - `zstdModule: true` on D and R.

### L1. base-dev ×2 (D, Metro, flags off, 64 KB packs): 31 min

```fish
bash $FA/session/mark.sh $M L1-start
devices/android-run.sh $FA/requests/and-q15-quick-base.request.json 1 --tag fg-base-dev --out $D
sleep 300
devices/android-run.sh $FA/requests/and-q15-quick-base.request.json 2 --tag fg-base-dev --out $D
bash $FA/session/mark.sh $M L1-end
```

Expected:
- 72 rows each, 0 errors, `perf` all false;
- retrieval p50 ≈ 3.2–3.4 s (P1 base on 0cfd4a77: 3.39 / 3.20 s; the stage timers add only a clock read per stage).

### L2. base-rel ×2 (install R): 30 min

1. `bash $FA/session/mark.sh $M L2-start`, then install R:
   - `adb install -r <workspace>/builds/android/boar-0cfd4a77-forge-release-arm64.apk` → `Success`.
   - Then `adb shell am force-stop $PKG; adb shell monkey -p $PKG 1`. R embeds its JS; Metro isn't used.
   - Wait until the chat shows the model loaded.
2. Run:
   ```fish
   devices/android-run.sh $FA/requests/and-q15-quick-base.request.json 1 --tag fg-base-rel --out $D
   sleep 300
   devices/android-run.sh $FA/requests/and-q15-quick-base.request.json 2 --tag fg-base-rel --out $D
   ```
3. **Release-vs-dev and the L0 calibration:**
   - `python3 $FA/stages_report.py $D/be-and-q15-quick-fg-base-rel-r1 $D/be-and-q15-quick-fg-base-rel-r2 --ref $D/be-and-q15-quick-fg-base-dev-r1`
   - The `p50/ref` column is release ÷ dev per stage: the **dev inflation** (L0 lower bound: 1/1.4 ≈ 0.71).
   - The `calibration:` line divides the phone's fzstd p50 by the M1 Hermes L0 p50 (499 ms). This is the **real M1→g75 ratio** that replaces L0's ×2.4.
4. `bash $FA/session/mark.sh $M L2-end`

### L3. P-7b packs ×2 (R): 35 min

1. `bash $FA/session/mark.sh $M L3-start`. **Swap the packs.** No deletion: the 64 KB packs move to `files/packs-64k/`, which the app doesn't search.
   ```fish
   adb shell am force-stop $PKG
   adb shell run-as $PKG mkdir -p files/packs-64k
   adb shell run-as $PKG mv files/corpus/boar-wikivoyage-en.sqlite files/corpus/boar-crypto.sqlite files/packs-64k/
   adb exec-in run-as $PKG sh -c 'cat > files/corpus/boar-wikivoyage-en.sqlite' < <workspace>/builds/packs-p7b/boar-wikivoyage-en.sqlite
   adb exec-in run-as $PKG sh -c 'cat > files/corpus/boar-crypto.sqlite' < <workspace>/builds/packs-p7b/boar-crypto.sqlite
   adb exec-out run-as $PKG sha256sum files/corpus/boar-wikivoyage-en.sqlite files/corpus/boar-crypto.sqlite
   ```
   Expected: `9db1aa378d1dd891…` and `d08070bfef3c1950…`.
   - **The size check is not a problem:** both packs come from the asset provider, not `CORPUS_CATALOG`, so `knowledgePacks()` lists them as local packs with `sizeBytes 0` and skips the size comparison. Kiln's desktop P-7b run used them the same way.
   - **The first run must still show it:** Wikivoyage/crypto sources in rows and `zstdBlocks > 0`.
   - **If `exec-in` fails on this adb:** push to `/data/local/tmp`, then `adb shell "cat /data/local/tmp/X | run-as $PKG sh -c 'cat > files/corpus/X'"`. The temp copies are then phone files: their removal is r4to's per-item OK.
2. Relaunch: `adb shell monkey -p $PKG 1`, then wait for the model to load.
3. Run:
   ```fish
   devices/android-run.sh $FA/requests/and-q15-quick-base.request.json 1 --tag fg-p7b --out $D
   sleep 300
   devices/android-run.sh $FA/requests/and-q15-quick-base.request.json 2 --tag fg-p7b --out $D
   ```
4. **Expected:**
   - zstd stage p50 about half of base-rel's (L0 −50%);
   - `zstdBlocks` per row ~2.9× base (more, smaller blocks).
   - P-7b criterion 1, read in release mode against base-rel back to back: retrieval p50 ≤ 0.8× base.
5. `bash $FA/session/mark.sh $M L3-end`

### L4. +P-8 ×2 (R, `sqlBatch`): 27 min

```fish
bash $FA/session/mark.sh $M L4-start
devices/android-run.sh $FA/requests/and-q15-quick-p8.request.json 1 --tag fg-p8 --out $D
sleep 300
devices/android-run.sh $FA/requests/and-q15-quick-p8.request.json 2 --tag fg-p8 --out $D
python3 $FA/stages_report.py $D/be-and-q15-quick-fg-p8-r1 $D/be-and-q15-quick-fg-p8-r2 --ref $D/be-and-q15-quick-fg-p7b-r1
bash $FA/session/mark.sh $M L4-end
```

Expected:
- `sqlCalls` p50 ≈ 0.4× of L3's (desktop: 476 → 190);
- P-8 criterion 1: retrieval p50 ≤ 0.9× L3;
- per-call cost = Δ(`sqlMs` p50) ÷ Δ(`sqlCalls` p50).

### L5. +native zstd ×2 (R, `nativeZstd`): 25 min

**Kill rule first (§6.1):**
- If L4's `zstdMs` p50 is **< 300 ms**, skip L5 and note "native zstd killed: zstd stage X ms on P-7b packs".
- L6 then runs with `vcache` minus `nativeZstd`: edit the request or use the p8 request plus `vectorCache`. Say so in the notes.

```fish
bash $FA/session/mark.sh $M L5-start
devices/android-run.sh $FA/requests/and-q15-quick-zstd.request.json 1 --tag fg-zstd --out $D
sleep 300
devices/android-run.sh $FA/requests/and-q15-quick-zstd.request.json 2 --tag fg-zstd --out $D
python3 $FA/stages_report.py $D/be-and-q15-quick-fg-zstd-r1 $D/be-and-q15-quick-fg-zstd-r2 --ref $D/be-and-q15-quick-fg-p8-r1
bash $FA/session/mark.sh $M L5-end
```

**Expected:**
- `zstdFallbacks` = 0 on every row;
- `zstdMs` p50 a few tens of ms at most (M1 native: 6.7 ms per question on 64 KB blocks, about 75× less than fzstd);
- `zstdOutBytes` equal to L4's for the same items.
- **If `zstdFallbacks` > 0:** stop the leg and keep the rows. The module refused blocks it decodes on desktop: a bug.

### L6. +vector cache ×2 (R, `vectorCache`): 25 min

```fish
bash $FA/session/mark.sh $M L6-start
devices/android-run.sh $FA/requests/and-q15-quick-vcache.request.json 1 --tag fg-vcache --out $D
sleep 300
devices/android-run.sh $FA/requests/and-q15-quick-vcache.request.json 2 --tag fg-vcache --out $D
python3 $FA/stages_report.py $D/be-and-q15-quick-fg-vcache-r1 $D/be-and-q15-quick-fg-vcache-r2 --ref $D/be-and-q15-quick-fg-zstd-r1
adb shell dumpsys meminfo $PKG | grep -E "TOTAL (PSS|RSS)"
bash $FA/session/mark.sh $M L6-end
```

Expected:
- `corpusCacheHit` true on every retrieving row but the first of each run;
- `corpusSqlMs` ≈ 0 on hits (vs L5's full scan of 5,300 rows);
- `corpusScoreMs` ~3× lower (Hermes L0: 30 ms saved per question on the M1);
- app RSS up ≤ ~15 MB vs L5 (the cached rows).

### L7. Restore the 64 KB packs (5 min)

The P-7b copies move to `files/packs-p7b/`. No deletion.

```fish
bash $FA/session/mark.sh $M L7-start
adb shell am force-stop $PKG
adb shell run-as $PKG mkdir -p files/packs-p7b
adb shell run-as $PKG mv files/corpus/boar-wikivoyage-en.sqlite files/corpus/boar-crypto.sqlite files/packs-p7b/
adb shell run-as $PKG mv files/packs-64k/boar-wikivoyage-en.sqlite files/packs-64k/boar-crypto.sqlite files/corpus/
adb exec-out run-as $PKG ls -l files/corpus
bash $FA/session/mark.sh $M L7-end
```

Expected: 351092736 and 36093952, as in S0. Probe B and the gate probe compare against desktop traces made with these packs.

## Session 2: probes on D (Metro edits)

If Session 2 is a new sitting, redo S0 steps 1–8 first (≈ 15 min, not counted below).

### L8. Probe B: Qwen3-4B with `no_extra_bufts` (35 min). Spec: `anvil/specs/probe-b-no-repack-g75.md`

1. **Back to D and Metro:**
   - `bash $FA/session/mark.sh $M L8-start`
   - `adb install -r …forge-debug-arm64.apk` → `Success`.
   - Metro running from `wt/forge-arms`, as in S0 steps 5–7.
2. **Apply Probe B** in the Metro tree:
   - `git -C <workspace>/wt/forge-arms apply $FA/probe-b.patch`
   - `git -C <workspace>/wt/forge-arms diff --stat` → `src/inference/LlamaEngine.ts | 3 +++`.
3. **Make the 4B loadable** (approved by the coordinator; our dev app only). It was parked, and the app recorded it as load-crashed: `answer()` and the request check refuse a model in `loadCrashedIds`.
   ```fish
   adb shell am force-stop $PKG
   adb shell run-as $PKG mv files/parked/qwen3-4b-instruct-2507-q4km.gguf files/models/
   adb exec-out run-as $PKG cat files/settings.json > $BE/$D/settings.before-probeb.json
   node -e 'const fs=require("fs");const s=JSON.parse(fs.readFileSync(process.argv[1],"utf8"));s.loadCrashedIds=(s.loadCrashedIds||[]).filter(i=>!/qwen3-4b/.test(i));delete s.pendingLoadCrash;fs.writeFileSync(process.argv[2],JSON.stringify(s))' $BE/$D/settings.before-probeb.json $BE/$D/settings.probeb.json
   adb exec-in run-as $PKG sh -c 'cat > files/settings.json' < $BE/$D/settings.probeb.json
   adb exec-out run-as $PKG cat files/settings.json > $BE/$D/settings.after-probeb.json
   node -e 'const fs=require("fs");const [a,b]=process.argv.slice(1).map(f=>JSON.parse(fs.readFileSync(f,"utf8")));const k=[...new Set([...Object.keys(a),...Object.keys(b)])].filter(k=>JSON.stringify(a[k])!==JSON.stringify(b[k]));console.log("changed keys:",k.join(", ")||"none");console.log("loadCrashedIds before:",JSON.stringify(a.loadCrashedIds),"after:",JSON.stringify(b.loadCrashedIds))' $BE/$D/settings.before-probeb.json $BE/$D/settings.after-probeb.json
   adb exec-out run-as $PKG ls -l files/models
   ```
   Expected:
   - `changed keys: loadCrashedIds` (plus `pendingLoadCrash` if it was set). Any other key changed means the write went wrong: restore `settings.before-probeb.json` and stop.
   - `before` lists `qwen3-4b-instruct-2507-q4km`; `after` doesn't.
   - `qwen3-4b-instruct-2507-q4km.gguf` 2497281120 appears in `files/models`.
4. **Cold load 1**, a separate terminal per command:
   - `bash $FA/session/meminfo-poll.sh $BE/$D/probeb-c1.mem.csv 900`
   - Launch on Metro (S0 step 7). **Verify** that the Metro log shows `[engine] PROBE-B no_extra_bufts=true …` once the 4B loads. If it is absent, the bundle is stale: stop.
   - `devices/android-run.sh $FA/requests/probeb-4b10.request.json 1 --tag c1 --out $D`
   - The request loads the 4B (that load is cold load 1) and asks 10 P3a questions: ≈ 8 min.
5. **Cold load 2:** `adb shell am force-stop $PKG`, then the same three commands with `c2` / `probeb-c2.mem.csv` and rep `2`.
6. **Read against the frozen criteria** (Anvil's §4):
   - **Kills:** `grep -E "am_kill|killinfo|am_proc_died" $BE/$D/events-session.log | grep -c aoair` → **0**.
   - **Memory:** each meminfo-poll run ends with `peak TOTAL RSS x.xx GiB` → **≤ 3.5 GiB** for both.
   - **Rows:** 10/10 `outcome: success` per run.
   - **Route/sources vs the desktop `and-qwen` trace:** Anvil, with `scorers/convert_device.py` + `devices/agreement.py`.
   - **Speed:** `anvil/tools/e2_latency_check.py`, reported only.
   - **Deviation from the spec:**
     - 2 × 10 answers (the request does the load) instead of 2 launches + 10 answers. Both cold loads are still measured.
     - USB stays plugged (adb meminfo needs it), where the spec says unplugged. **Approved by the coordinator**: the same condition for control and arm; battery temperature is in `legs.csv`.
7. **Probe B FAIL:**
   - park the 4B again (`mv files/models/qwen3-4b… files/parked/`);
   - restore `settings.before-probeb.json` with the same `exec-in` line, then dump again to `settings.restored.json` (it must equal `settings.before-probeb.json`);
   - **skip L10**.

   **PASS:** keep the patch and the 4B for L10.
8. `bash $FA/session/mark.sh $M L8-end`

### L9. Gate probe leg A: g75 + 1.5B (30 min)

Spec: `anvil/specs/probe-gate-prefix-cache.md` §4. Block design: Anvil (relay 2026-10-03); **L9/L10 approved by Anvil as written, frozen for this session** (spare rule kept). References: `anvil/specs/probe-gate-items.json` (re-pinned to B5).

**Gate patch per leg (Anvil, 2026-10-03; B6 passed L1, re-pinned before any device data):**
- **Leg A (1.5B, this L9): B5 unchanged.** `b5gate-engine.patch` sha `50609046…`, compared against `desktop_15b`. Why not B6: B6's prompt collapses the 1.5B's label mass (< 0.4 on 5/12 items, 0 on 2), so P1 there would test the no-label fallback.
- **Leg B (4B, L10): B6**, applied as a delta on top of B5 (see L10). Compared against `desktop_4b_b6` (all 0.000/1.000).
- **The requests don't change** (same items).

**Why blocks:** the gate's on/off switch is a source edit served by Metro. Toggling it per item would reload JS and reset the gate's cache state, so every gate would take the cold path that P2/P3 must not measure.

1. **Apply B5** in the Metro tree, on top of Probe B if it is still applied (both apply together, checked):
   ```fish
   bash $FA/session/mark.sh $M L9-start
   shasum -a 256 <workspace>/rnd/research/anvil/exp/chat-routing/arm/b5gate-engine.patch
   cd <workspace>/wt/forge-arms
   git apply <workspace>/rnd/research/anvil/exp/chat-routing/arm/b5gate-engine.patch
   git status --short
   cd $BE
   ```
   Expected:
   - sha `50609046e22fe14c…aee9958`;
   - `git status --short` shows ` M` for `LlamaEngine.ts`, `answer.ts` and their tests, and `??` for the new `src/routing/routeGate.ts` and `routeGate.test.ts`.
2. **Gate switch** (one command per block; leg A adds `anyModel = true`, so the gate runs on the 1.5B):
   ```fish
   # ON:
   sed -i '' 's/ROUTE_GATE_CONFIG = { anyModel: [a-z]*, off: [a-z]* }/ROUTE_GATE_CONFIG = { anyModel: true, off: false }/' <workspace>/wt/forge-arms/src/routing/routeGate.ts
   # OFF:
   sed -i '' 's/ROUTE_GATE_CONFIG = { anyModel: [a-z]*, off: [a-z]* }/ROUTE_GATE_CONFIG = { anyModel: true, off: true }/' <workspace>/wt/forge-arms/src/routing/routeGate.ts
   grep -n "ROUTE_GATE_CONFIG =" <workspace>/wt/forge-arms/src/routing/routeGate.ts
   ```
3. **Blocks, in this order:**

   | Block | Gate | Request (1 unmeasured warm-up + 5 measured, back to back) | Tag |
   |---|---|---|---|
   | A1 | ON | `gate-A-items1-5` (cs-001, cs-008, cs-014, cs-021, cs-028) | `ga-a1` |
   | B1 | OFF | `gate-A-items1-5` | `ga-b1` |
   | A2 | ON | `gate-A-items6-10` (cs-042, cs-050, cs-053, cs-029†, cs-040†) | `ga-a2` |
   | B2 | OFF | `gate-A-items6-10` | `ga-b2` |

   † multi-turn: the frozen history goes in the request (patch v2).

   **Per block** (here A1; substitute the switch, request and tag):
   ```fish
   # 1. switch (step 2), then:
   adb shell am force-stop $PKG; adb logcat -c
   bash $FA/session/mark.sh $M L9-ga-a1-start
   bash $FA/session/meminfo-poll.sh $BE/$D/ga-a1.mem.csv 300 &
   # 2. cold start on Metro (S0 step 7). Expected: Metro prints "Android Bundled …" (the edit was picked up) and the chat shows the model loaded
   devices/android-run.sh $FA/requests/gate-A-items1-5.request.json 1 --tag ga-a1 --out $D
   adb logcat -d -s ReactNativeJS:V > $BE/$D/ga-a1.logcat.txt
   grep "\[gate\]" $BE/$D/ga-a1.logcat.txt
   ```
   Expected:
   - **ON block:** 6 lines `[gate] model=… newTok=… cachedTok=… loadGateMs=… gateMs=… top=…`, one per item. The first is the warm-up (`cs-010-warmup`, the cold path), unmeasured by design. In A1 the warm-up creates the gate and answer session files, so measured items never take the first-gate cold path (Anvil checked that smallTalk catches none of cs-010 or the 10 items). **If an ON block's warm-up shows no `[gate]` line, write it in the session notes.** Each is followed by `[gate] answer prefix restored in N ms` when an answer follows.
   - **OFF block:** no `[gate] model=` line.
   - `✓ 6 rows`, all `outcome: success`.
   - About 4 min per block, including the cold start.
4. **Spare:** if a measured item has no `[gate] model=` line in an ON block (smallTalk answered first), run `gate-A-spare.request.json` (cs-054) right after that block, same tag + `-spare`, no restart. Do the same after its paired OFF block.
5. **Read (Anvil):**
   - P1–P5 from the rows, `ga-*.logcat.txt` and `ga-*.mem.csv`;
   - **P3 uses only the gate-ON `[gate]` lines of the 10 measured items** (`loadGateMs + gateMs + loadAnswerMs`);
   - the A − B answer totals are reported, not gated;
   - leg A: P3 reported only.
6. `bash $FA/session/mark.sh $M L9-end`. Leave B5 applied for L10. If L10 is skipped, revert the tree (L11 step 1).

### L10. Gate probe leg B: g75 + 4B on B6, only if Probe B PASSED (40 min)

1. **Upgrade B5 → B6** in the Metro tree. B5 (from L9) and Probe B stay applied; the delta touches only `src/routing/routeGate.ts` + `routeGate.test.ts`:
   ```fish
   bash $FA/session/mark.sh $M L10-start
   shasum -a 256 <workspace>/rnd/research/anvil/exp/chat-routing/arm/b5-to-b6-gate.patch
   git -C <workspace>/wt/forge-arms apply -p1 <workspace>/rnd/research/anvil/exp/chat-routing/arm/b5-to-b6-gate.patch
   grep -n "ROUTE_GATE_MODEL_IDS: \|ROUTE_GATE_CONFIG =" <workspace>/wt/forge-arms/src/routing/routeGate.ts
   ```
   Expected:
   - sha `21211329514a16edc9b3ec31379227d7a7e8054044f391bf3c6fc204a9e0169f`;
   - `ROUTE_GATE_MODEL_IDS` contains `qwen3-4b-instruct-2507-q4km`.
   - Checked on a copy 2026-10-03: B5 + Probe B + this delta is byte-identical to B6 (`17a50083…`) + Probe B.
2. **Gate switch for leg B: `anyModel: false`.** The 4B is in `ROUTE_GATE_MODEL_IDS`, so the gate runs on it by model id:
   ```fish
   # ON:
   sed -i '' 's/ROUTE_GATE_CONFIG = { anyModel: [a-z]*, off: [a-z]* }/ROUTE_GATE_CONFIG = { anyModel: false, off: false }/' <workspace>/wt/forge-arms/src/routing/routeGate.ts
   # OFF:
   sed -i '' 's/ROUTE_GATE_CONFIG = { anyModel: [a-z]*, off: [a-z]* }/ROUTE_GATE_CONFIG = { anyModel: false, off: true }/' <workspace>/wt/forge-arms/src/routing/routeGate.ts
   ```
3. **Blocks:** as in L9 steps 3–5, with:
   - requests `gate-B-items1-5` / `gate-B-items6-10` (4B, `confirmLargeModels: true`);
   - tags `gb-a1`, `gb-b1`, `gb-a2`, `gb-b2`; marks `L10-…`; spare `gate-B-spare`;
   - meminfo-poll 480 s per block; about 7 min per block.
4. **Probe B's patch stays applied:** `no_extra_bufts` is what lets the 4B load.
5. **Read (Anvil):** against `desktop_4b_b6`. **P3 (gate overhead p50 ≤ 1.0 s over the 10 measured gate-ON items) is judged here.** Kills: as in L8.
6. `bash $FA/session/mark.sh $M L10-end`. Afterwards, the 4B stays installed or is parked again: r4to's call, with the Probe B result.

### L11. Teardown (5 min)

1. Revert the Metro tree. B5 creates 2 new files (`src/routing/routeGate.ts` and its test), so a checkout alone isn't enough:
   ```fish
   git -C <workspace>/wt/forge-arms checkout -- .
   git -C <workspace>/wt/forge-arms clean -fd -e node_modules -e .expo
   git -C <workspace>/wt/forge-arms status --short
   ```
   Expected: empty.
2. Airplane off: `adb shell cmd connectivity airplane-mode disable`.
3. Stop the events logcat (Ctrl-C).
4. Leave D installed: it is base 0cfd4a77 behaviour with all flags off.
5. Phone files left by this session: `files/packs-64k/` (empty after L7) and `files/packs-p7b/` (≈ 405 MB). Delete them only with r4to's OK.
6. `bash $FA/session/mark.sh $M S-end`.
7. Copy `$D` notes into the session report: arms run or killed, the kill-rule reading, the deviations.

## 6. Criteria for the Forge arms (frozen 2026-10-02, before any device run)

Common to both:
- Desktop step 0 PASS (Kiln: byte-identity 72/72 vs base, flags off and on; unit suite).
- 0 BOAR kills and 0 errors in the arm's runs.
- Route and shown sources = the previous arm's on 72/72 (`devices/agreement.py`; answer text may differ at temperature 0.7).
- Read in release mode (R), back to back with the previous arm.

### 6.1 `nativeZstd` (L5)

0. **Kill rule** (coordinator, standing): **skip if L4's `zstdMs` p50 < 300 ms** on the P-7b packs.
1. **Native module in use:** `zstdFallbacks` = 0 on every row, and `zstdModule` true.
2. **Retrieval p50 ≤ 0.8× L4** (pooled over 2 reps, both arms).
   - Prediction: the zstd stage drops by ~95%.
   - Retrieval ≈ 0.6–0.75× L4, because P-7b already halved fzstd. A wide margin on the 0.8 bar comes only if fzstd is ≥ 40% of L4's retrieval.
3. TTFT p50 reported, not gated.

**PASS = 1 + 2.** PASS → candidate for adoption: the claim build gets the module plus the flag on by default, and an iOS device check before any iOS default.

### 6.2 `vectorCache` (L6)

1. **Mechanism:**
   - `corpusCacheHit` true on ≥ 66 of the 68 retrieving rows of each run;
   - per-row median of (`corpusSqlMs` + `corpusScoreMs`) **≤ 0.5×** L5's.
2. **No regression:** retrieval p50 ≤ 1.0× L5 (pooled).
3. App TOTAL RSS after the run ≤ L5's + 30 MB.

**PASS = 1 + 2 + 3.** The size of the saving is reported, not gated. The phone cost of moving 10.6 MB/question across the bridge is the UNKNOWN this measures.

## UNKNOWN

- Whether Android 16's `adb exec-in` works with `run-as` on this phone. A fallback is given in L3.
- Release-variant `debuggable true` and ART: Java/Kotlin code may run slightly slower than a true release build. JS (Hermes bytecode) and native code are unaffected.
- Whether the dev-client deep link `exp+boar-app://…` opens Metro directly on this build. The tap fallback is given in S0 step 7.
- Time per R run (≈ 11 min) is an estimate. L2 measures it; adjust the rest of the plan from it.
