**Why.** #40 builds the offline APK in CI and signs it with BOAR's key, and #39's `scripts/check-release-apk.sh` checks the package, versionCode and signer. What's still missing is a way for *anyone else* to check the offline claim itself: that this APK can't reach the network, and that on a phone it really sends nothing. Right now that's a promise in the README. This PR makes it one command on the published file, plus a one-session phone test that also collects the Android numbers we don't have yet.

**What.**
- `scripts/audit-apk.py` (python3 + `aapt2`, no Java; works on any APK) reports:
  - permissions and manifest flags;
  - Play Services / Firebase / tracker classes and OTA loaders;
  - native socket imports;
  - every host embedded in the dex, the Hermes bundle, native libs and assets;
  - the signer certificate.

  Verdicts are `NO-NETWORK-BY-CONSTRUCTION` / `NETWORK-CAPABLE` (+ trackers), and the same APK gives a byte-identical report.
- `make offline-proof APK=… [RELEASE=1] [RELEASE_VARIANT=downloader]` (`scripts/offline-proof.sh`): fails unless the offline APK is `NO-NETWORK-BY-CONSTRUCTION`. `RELEASE=1` also requires the release signer, reusing `RELEASE_SIGNER` from #39's `check-release-apk.sh`, so there's one pin and no `apksigner` is needed.
- `scripts/netstats-uid.sh <package>` reads the kernel's per-app traffic counters over adb (`mAppUidStatsMap` + the recorded history). This is the "sends nothing" check on a phone. A bare `grep uid=` would be wrong: the app also appears in `mUidCounterSetMap`, which only records foreground state.
- `docs/OFFLINE_PROOF.md`: how to run it and what each verdict means.
- `docs/device-test-pack/`: one ~1–1.5 h session on a physical phone, in three parts:
  - (A) the signed offline APK stays at 0 B in airplane mode and on Wi-Fi;
  - (B) the in-app benchmark on Qwen3-4B, s16, which needs #36's dev build;
  - (C) a smoke test of Maple-Preview 20B-A1B installed through the in-app Hugging Face search, on 5 factual questions next to Qwen3-4B.

  The two request files parse and resolve with #36's `deviceEvalRequest`.

**Ask for the v1.1.0 release notes.** Publish these two lines, so users can check the download without trusting us:
- Signer certificate SHA-256: `7cf514f9ab8253cbd78eb7d112d66fd05c2ad27e6fc987bf8f3276a7eedf1f01` (CN=BOAR, O=sopa.team, same key as v1.0.0)
- `make offline-proof APK=boar-offline-v1.1.0-arm64.apk RELEASE=1` → `OK: … (offline): NO-NETWORK-BY-CONSTRUCTION, signed with the release key`, plus the report's sha256

Once #40 is merged, the workflow could run `scripts/offline-proof.sh` next to `check-release-apk.sh` and attach the report to the draft release. I left that out so this PR doesn't touch #40's files.

**How to test.**
```bash
make offline-proof APK=dist/boar-offline-1.1.0-arm64.apk                                     # OK: … NO-NETWORK-BY-CONSTRUCTION
RELEASE_VARIANT=downloader scripts/offline-proof.sh dist/boar-downloader-1.1.0-arm64.apk     # OK: … NETWORK-CAPABLE (report only)
make offline-proof APK=<a debug-signed offline build> RELEASE=1                              # FAIL: not signed with the release key
scripts/netstats-uid.sh team.sopa.aoair.offline                                               # on a phone: rx=0 B tx=0 B, exit 0
```

**How verified.**
- Ran on 6 APKs: a competitor team 1.0.0, a competitor team 1.1.10, BOAR v1.0.0 and three local BOAR builds.
- Offline builds come out `NO-NETWORK-BY-CONSTRUCTION`; downloader builds and v1.0.0 come out `NETWORK-CAPABLE`.
- `RELEASE=1` passes on v1.0.0 (cert `7cf514f9…`) and fails on debug-signed builds.
- Reports are byte-identical across runs.
- The ELF import parser matches `llvm-nm -D`, and the signer cert matches `openssl x509` on the extracted DER.
- `netstats-uid.sh` was checked on an Android 15 emulator: an installed offline build shows 0 B, and the parser reads non-zero rows correctly. It hasn't run on a phone yet; part A of the pack is that first run.

**Found on the way (not fixed here).** `src/services/modelBrowser.ts:62` reads the hash from `siblings[].lfs.oid`, but the `/api/models/{repo}?blobs=true` response carries it as `lfs.sha256` (checked on `deepgrove/maple-preview-GGUF`). So every model installed through search gets `sha256: ""` and is only size-checked (`ModelManager.ts:262,720`). The catalog is unaffected: all 39 bundled entries have a sha256. The fix is `s.lfs?.sha256 ?? s.lfs?.oid ?? null`. Until then, part C of the pack checks Maple's hash by hand.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
