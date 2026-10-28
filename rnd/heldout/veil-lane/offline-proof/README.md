# offline-proof: a verifiable "no network" audit for Android APKs

TL;DR: `audit_apk.py` is a single-file static auditor with no dependencies beyond the Python stdlib and `aapt2`. It turns "trust us, it's offline" into a report anyone can reproduce from the APK alone. It checks permissions, manifest flags, GMS/Firebase, tracker SDKs, remote-code loaders, network libraries, native socket imports, hosts embedded in DEX, Hermes JS, native libs and assets, the signing certificate, and indirect egress channels. The reference run covers 6 APKs: 2 competitors, 3 local BOAR builds and the published BOAR v1.0.0. All 6 controls and the release-key gate pass, and the output is byte-identical across runs.

```bash
# one APK -> markdown on stdout
python3 rnd/veil/offline-proof/audit_apk.py path/to/app.apk
# many APKs -> reports/<apk>.md + .json + SUMMARY.md
python3 rnd/veil/offline-proof/audit_apk.py a.apk b.apk --out /tmp/reports
# reference run + controls + determinism check (~35 s on M1)
bash rnd/veil/offline-proof/run-all.sh
# + the published GitHub release (downloads 123 MB to a temp dir, verifies .sha256, deletes after) + release-key gate
FETCH_PUBLISHED=1 bash rnd/veil/offline-proof/run-all.sh
# release gate alone: exit 3 if signed with CN=Android Debug / a known public key
python3 rnd/veil/offline-proof/audit_apk.py boar.apk --require-release-key
```

Requirements: `python3` ≥ 3.9 and Android build-tools `aapt2`, found automatically under `$ANDROID_HOME`, `~/Library/Android/sdk` or `~/Android/Sdk`; override with `--aapt2`. **No Java needed**: the APK Signing Block v2/v3 is parsed directly. Exit code: 0 if every APK is `NO-NETWORK-BY-CONSTRUCTION`, 1 otherwise, 2 on a tool error, 3 when `--require-release-key` finds a debug/public signing key. That makes it usable as a CI gate.

## Reference results (2026-09-30, tool 0.2.0)

| APK | verdict | INTERNET | GMS | trackers | signer | notable |
|---|---|---|---|---|---|---|
| a competitor team 1.0.0 (`246bd4ee…`) | **NO-NETWORK-BY-CONSTRUCTION** | no | no | 0 | own cert `51b8c61c…` | `MANAGE_EXTERNAL_STORAGE` (models in shared storage: tamperable by other apps). `libllama-common.so` imports `socket/connect/getaddrinfo` (llama.cpp's `-hf`/docker downloader), dead without INTERNET |
| a competitor team 1.1.10 (`5bc392c3…`) | **NO-NETWORK-BY-CONSTRUCTION** | no | no | 0 | own cert `13112751…` | same llama-common imports. `allowBackup` defaulted but `dataExtractionRules` set |
| BOAR offline `1928502d`, local test build (`14216e92…`) | **NO-NETWORK-BY-CONSTRUCTION** | no | no | 0 | public debug key (local) | no native socket imports at all. Model/pack URLs (HF, GitHub) still present in the JS bundle as dead code. Dev-launcher = release no-op stub |
| BOAR downloader `b7e31b7`, local (positive control) | NETWORK-CAPABLE | yes | no | 0 | public debug key (local) | + RECORD_AUDIO |
| BOAR main `9898b35`, local (positive control) | NETWORK-CAPABLE | yes | no | 0 | public debug key (local) | + SYSTEM_ALERT_WINDOW, `allowBackup` default, no extraction rules |
| **BOAR published v1.0.0** (`de9e3156…`, = release `.sha256`) | NETWORK-CAPABLE | yes | no | 0 | **own key** `O=sopa.team, CN=BOAR`, cert SHA-256 `7cf514f9…1f01` / SHA-1 `497D5E09…0B67` | downloader-style ("open it once online to download the ~1 GB default model"), + SYSTEM_ALERT_WINDOW, RECORD_AUDIO, `allowBackup` default, no extraction rules |

Full reports: [`reports/SUMMARY.md`](reports/SUMMARY.md) and one `.md` + `.json` per APK.

**Findings for BOAR:**
1. **Signing, MEDIUM (process).** The published v1.0.0 uses BOAR's own key. But all **20/20** local/test APKs in `builds/android/` are signed with certificate SHA-256 `fac61745…3b9c` (SHA-1 `5E:8F:16:06:2E:A3:CD:2C:4A:0D:54:78:76:BA:A6:F3:8C:AB:F6:25`, `CN=Android Debug`). This is the standard React Native / Expo prebuild `debug.keystore` ([expo/eas-cli#3127](https://github.com/expo/eas-cli/issues/3127)), byte-identical to `wt/devicelab/android/app/debug.keystore`. `boar-app/plugins/withReleaseSigning.js` falls back to it silently when `BOAR_UPLOAD_*` is missing (fail-open), and the real cert fingerprint isn't published. A debug-signed install can be "updated" by anyone, keeping its chats, so never distribute one. `run-all.sh` now gates the published APK with `--require-release-key`.
2. **P1 for the published artifact, MEDIUM.** v1.0.0 declares INTERNET. Offline-during-use there is enforced by app code (`networkAllowed()`), not by the kernel. Only the offline flavor is provable statically, and it hasn't been released with the BOAR key.

## What each check means

| Section | Evidence | Why it matters |
|---|---|---|
| Permissions | `aapt2 dump xmltree` | Without `INTERNET` the app UID is not in the `inet` group, so `socket(AF_INET)` fails (BOAR's own note: `review/ETH_NODE_INTEGRATION.md:106`, "inclusive 127.0.0.1"; [Manifest.permission.INTERNET](https://developer.android.com/reference/android/Manifest.permission#INTERNET)). **This is the only check that is a guarantee**; everything else is capability or smell. |
| Manifest flags | allowBackup, dataExtractionRules, cleartext, debuggable, sharedUserId, `<queries>`, exported components | Data-at-rest leaving via backup, and indirect channels |
| GMS / trackers / remote code | DEX `type_ids`, class-prefix signatures modelled on [Exodus Privacy](https://reports.exodus-privacy.eu.org/en/trackers/) | GMS runs in another process that has network, so an app without INTERNET can still cause egress through binder calls |
| Network libraries | DEX types (OkHttp, HttpURLConnection, WebView, DownloadManager, RN networking) | Capability only. React Native always links OkHttp. |
| Native imports | ELF `.dynsym` undefined symbols (`socket`, `connect`, `getaddrinfo`, curl, SSL). Cross-checked against `llvm-nm -D` on 3 libs, identical | llama.cpp builds may carry HTTP downloaders |
| Hosts | URLs in DEX strings, **decoded Hermes bytecode string table** (v98: 240,414 strings, 99.9% printable), native libs, assets. Classified `review / doc-link / namespace / local/dev / junk` | What the app *would* talk to. The watch-list catches runtime-built URLs (e.g. `supabase.co`) |
| Signing | APK Signing Block v2/v3 parsed. Cert SHA-256. Known public debug certs flagged | Update-hijack / supply chain (see above) |
| Indirect channels | `<queries>` VIEW/SEND, shared storage, GMS, exported components | Egress through *other* apps, which the static check cannot see |

## Limits (read before quoting a verdict)

- Static = capability, not behaviour. Pair with [`DYNAMIC-TEST.md`](DYNAMIC-TEST.md) (airplane mode, capture AP, GrapheneOS toggle, per-UID `netstats`).
- The signature is **not cryptographically verified** (no Java here). Run `apksigner verify --print-certs` where Java exists.
- The tracker list is a subset of Exodus signatures (22 SDKs), not the full list. UNKNOWN: coverage versus Exodus's current list.
- The Hermes parser anchors on the string-kind table. It is tested on HBC v98 only; on failure it falls back to a raw byte regex, which can merge adjacent strings.
- URLs built at runtime from config or env (e.g. BOAR's `EXPO_PUBLIC_SUPABASE_URL` in the downloader build) are only caught by the domain watch-list if the domain literal survives in the bundle. It did not appear in any BOAR build audited here. UNKNOWN: whether any of these builds had the Supabase env set.

## Relation to existing audits

`boar-app/scripts/audit-offline-apk.sh` and a competitor team's `scripts/verify_offline.sh` are **self-gates** (allowlists tuned to their own app). This kit is **app-agnostic and third-party**: it adds JS/Hermes host extraction, native socket imports, signing-key checks and indirect channels, and emits a diffable JSON so two people auditing the same APK hash get the same bytes. Suggested use: attach `SUMMARY.md` + the APK sha256 to the bounty claim, and let anyone rerun it.

## Metric + next step

- **Metric:** 6/6 controls correct + release gate verified both ways (published APK passes; a debug-signed APK exits 3), 0 false "no network" verdicts, reports byte-identical across 2 runs, ~3–6 s per 130 MB APK on M1.
- **Next step:** run `DYNAMIC-TEST.md` R1+R2 on one physical Android phone with the BOAR offline APK. This turns the static verdict into a measured "0 B sent", which the app currently claims without a counter.
