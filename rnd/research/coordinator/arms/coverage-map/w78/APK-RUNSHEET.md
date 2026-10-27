# W78-APK runsheet (2026-10-23; 0 LLM, 0 phone touched, nothing installed): BOAR Bench APK with the W78 retrieval stack, for the Pixel 8a read

TL;DR: one APK carries SEFIX-124 + W78-BINARY + W78C/PACKFMT IVF and switches per request (`"w78": {"mode": "w78" | "sefix124" | "off"}`, absent = w78), so the control is the same APK with the W78 switches off (no second APK). Run order on the phone: `w78-on`, `w78-ctl`, `w78-on` again (about 25 phone min after a 6-10 min kit push). Everything below is in `<workspace>/handoff/w78-apk-2026-10-23/` (not in git; `SHA256SUMS` there).

## What was built
| item | value |
|---|---|
| APK | `boar-bench-0cfd4a77-cut7-w78-nonet-d0d12e57febf.apk`, 77,965,848 B (74.4 MiB), sha256 `bbf22aa374dd331e383ff06f4e0923f951b2a176ece1e3b07ade8aef135914b2`; debuggable, no INTERNET, arm64, same 21 native libs as the gemma2 APK (llama.rn rc.4 unchanged) |
| engine | commit 0cfd4a77 + `w78-stack.vs-0cfd4a77.patch` (sha dd8f4da3c83241e8…, = diff of kiln-local/rs-W78 vs 0cfd4a77 over the engine file set); tree hash **d0d12e57febfe010…** = `node scripts/tree-hash.mjs kiln-local/rs-W78` (byte-identical). rs-W78 = cut7-headpass-x2+litepacks + H4-MERGE + SEFIX-ALL + W78-BINARY + W78B + W78C + W78-PACKFMT (wikiPack.ts sha 7be8cfe7). F3 code is in the tree but off (RS_HEALTH_NOSOURCE_FALLBACK never set), i.e. SEFIX-124 |
| bench shell | bench-app c9c6a22 + `bench-app-w78.vs-c9c6a22.patch` (sha 0f04f36b…; uncommitted, work copy `<workspace>/kiln-local/bench-w78`; bench-app itself untouched). Adds src/w78.ts (env + the two settings per request), src/nodeFsShim.ts (Metro alias of `node:fs` for wikiPack.ts and answer.ts: sidecar reads through expo-file-system, logs kept in memory), `process.memoryUsage` shim (VmRSS, only while the dense log is on), push-kit.sh accepts `w78/leadbits/` |
| switches in mode w78 | env RS_MERGE=gidf, RS_SE_LEAD=0.78, RS_SE_MAXDF=0.25, RS_KEEP_NOPROPER=1 (SEFIX-124 = F1+F2+F4) + settings packHeadPass=a2, packDense2=append-budget + RS_SE_LEAD_BIN=32 (W78) + RS_DENSE_IVFP=32 (PACKFMT); logs RS_SE_LEAD_LOG/RS_DENSE_LOG to memory, written into `bench.json` (`w78Logs`, `w78` = what was applied). mode sefix124 = the same minus the two W78 switches; mode off = nothing (plain cut-7 retrieval) |
| requests (13 q) | `requests/w78-{on,ctl,off}.request.json`: warmup-000 + the 10 E1-PAR speed ids (saf-008, saf-005, saf-007, saf-010, saf-011, lan-ref-002, vit-hlt-003, lan-exp-001, lan-rsn-003, vit-cry-009) + 2 IVF-pack items from W78C MAIN where stage 1 kept a simplewiki/travel chunk **and** F1 fires: st-qa-cooking-se-011 (kept: cooking 4, simplewiki 1, firstaid 1) and st-qa-money-se-010 (money 4, travel 2). Qwen3-1.7B, quickFirst. Desktop kept lists for the 7 MAIN ids: `w78-desktop-expected.json` |
| kit | `kits/w78-sefix124.kit.txt` (3.05 GB): 13-pack SEFIX-124 N10 kit with the PF copies of simplewiki (817,307,648 B, sha 9c316ff2…) and travel (229,244,928 B, 6c7221a6…) + F1 sidecars c54ce6fea381e7ce.leadbits (cooking, 1,336,312 B) and f1866b7666db1e11.leadbits (money, 1,825,320 B) + 1.7B, embedding, detector |

## Install and kit (fish; phone on USB, airplane mode on)
```fish
fish_add_path ~/Library/Android/sdk/platform-tools
set H <workspace>/handoff/w78-apk-2026-10-23; set W <workspace>/kiln-local/bench-w78
set G <workspace>/rnd/research/coordinator/arms/device-day-1022; set BE <workspace>/boar-eval
cd $H; mkdir -p runs; shasum -a 256 -c SHA256SUMS; adb shell df -h /data | tail -1        # need >= 5 GB free
adb install -r $H/boar-bench-0cfd4a77-cut7-w78-nonet-d0d12e57febf.apk       # same package id: keeps the 1.7B and packs already there
cd $W; scripts/push-kit.sh $H/kits/w78-sefix124.kit.txt                     # streams over run-as into files/corpus, files/models, files/w78/leadbits; sha-checks each (= already when equal)
```
Pack dir = app-private `files/corpus/` (as the device-day: run-as streaming, no /sdcard). **The kit overwrites 3 persona-a-union packs** (factbook, medlineplus, firstaid, v3proto versions): restore at the end with `scripts/push-kit.sh kits/persona-a-union.kit.txt` (from <workspace>/bench-app). Added bytes vs the plain packs: simplewiki PF +81.8 MB, travel PF +17.2 MB, two leadbits +3.16 MB.

## Runs (thermal start rule of the device-day: status 0 and battery <= 31.0 C)
```fish
for a in "w78-on 1 a" "w78-ctl 1 b" "w78-on 2 c"
  set p (string split " " $a); adb shell am force-stop team.sopa.boarbench     # cold process: the engine caches lead matrix / sidecars per process
  python3 $G/thermal_gate.py $p[1] 310
  adb shell "run-as team.sopa.boarbench cat /proc/\$(pidof team.sopa.boarbench)/io" > $H/runs/io-before-$p[3].txt   # if pidof is empty the app is not up yet: start it first (am start -n team.sopa.boarbench/.MainActivity)
  BOAR_EVAL=$BE $W/scripts/bench-run.sh $H/requests/$p[1].request.json $p[2] --tag $p[3] --out $H/runs
  adb shell "run-as team.sopa.boarbench cat /proc/\$(pidof team.sopa.boarbench)/io" > $H/runs/io-after-$p[3].txt    # read_bytes delta = OS-level storage reads (UNKNOWN: whether run-as may read /proc/<pid>/io)
end
```
Optional 4th arm `w78-off`. After the session restore the persisted settings (the APK writes packHeadPass/packDense2 into files/settings.json on every request; `off` removes them):
```fish
adb exec-out run-as team.sopa.boarbench cat files/settings.json | python3 -c 'import json,sys; s=json.load(sys.stdin); s.pop("packHeadPass",None); s.pop("packDense2",None); print(json.dumps(s))' | adb exec-in run-as team.sopa.boarbench sh -c 'cat > files/settings.json'
```
Control = the same APK, `w78-ctl` (mode sefix124: exact int8 F1 scan of lead_vecs, exact dense stage 1 through the full lead matrix; it reads the same PF-copy files, whose lead_vecs are byte-identical). Cold per arm = force-stop; the OS page cache cannot be dropped without root (state it with the numbers; `read_bytes` is the check).

## What to measure (all from `<out>/<rid>/`: rows.jsonl, bench.json, telemetry.csv; readout `python3 -I rnd/.../e1-partime/tools/e1par_readout.py` takes ids from the request, so 12 items work)
- cold retrieval ms: the `retrieve` / `search-wikipacks` span of the first question that searches packs (carries the matrix or sidecar load; `w78Logs.denselog[0..]` loadMs/scanMs per pack), then warm p50/p90 over the 12 items; total ms (rows.totalLatencyMs), TTFT.
- PSS after load and peak: telemetry.csv `app_pss_kb` (5 s sampler = lower bound of the peak), plus `rssAfter` in the dense log (VmRSS at each stage 1); delta ctl vs on is the point (desktop first-question RSS growth 360.6 -> 76.9 MB).
- bytes read: `w78Logs.summary` (scanBytes per pack and mode, rescoreRows) and the `read_bytes` delta of /proc/pid/io. Mode check: `ivfp32` on simplewiki and travel, `bin32` on cooking and money, `int8` on the other packs; `int8` on a big pack in the w78 arm means the lead_ivf tables were not found (wrong pack file).
- kept-id parity: retrievedTitles on-vs-ctl on all 12 items (expect identical; desktop kept PF32 = IVF32 on 97/97, = exact B on 96/97, the one loss is money-005, not in this request); vs `w78-desktop-expected.json` only for orientation (the phone routes by its own gate, the desktop replay used the funnel-K3 tasks).

## Desktop numbers to compare (MacBook V8; W78.md, W78C.md, W78-PACKFMT.md)
| metric | exact (ctl) | W78 on |
|---|---|---|
| F1 bytes scanned per question (2 packs) / ratio | 23.35 MB | 2.94 MB, 0.126x |
| F1 scan ms per call, mean (p50) / first load | 14.6 (14) / 102-140 ms | 1.5 (1) / 2-3 ms |
| stage-1 dense bytes per question | 101.75 MB | 18.32 MB (SQLite pages 12.14 MB + centroids 2 x 0.39 MB + 5 small packs 5.39 MB) |
| whole kit bytes per question | 125.09 MB | 21.26 MB (0.17x) |
| stage-1 scan ms per question / matrix load total | 120.7 / 471 ms | 45.2 / 48 ms |
| cold first question (fresh process): stage 1 incl. load / storage read / RSS growth | 620 ms / 101.75 MB / 360.6 MB | 92 ms / 17.10 MB / 76.9 MB |
Hermes has no SIMD popcount and the F1 loop is JS: the 14.6 -> 1.5 ms ratio is V8 and may not hold; bytes and RSS ratios should transfer, ms may not. Freeze a pass/fail criterion (sha256) before the first run if it will decide anything: none is frozen here.

## Not done / UNKNOWN
- Nothing installed or run: no phone, no emulator. Verified only at build level: Metro resolved the `node:fs` alias, the bundle holds the W78 strings, tsc clean on src/, tree hash = rs-W78. First risk on the phone: `File.bytesSync` on a `file://` path and `process.env` writes under Hermes (a failed leadbits read makes the run error visibly in bench.json, it does not silently fall back).
- Base tree is the rs lineage (serial pack search, no batchret/parsearch/blockcache of the current bench APKs), so absolute ms are not comparable with E1-PAR A/B/E rows (those had a 6-pack kit anyway); compare only ctl vs on in this APK. W78 + parsearch is a later combination.
- The 13-pack kit on 8 GB has no phone number yet (simplewiki PF is 817 MB; lead matrices in ctl mode are about 104 MB resident); an LMK kill in ctl is a result, not a failure of the runsheet.
- IVF lists are built on the MacBook with k-means seed 42 (ARM build time unmeasured); the F1 sidecars exist only for the two wave3 files in the kit.
