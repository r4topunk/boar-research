# Dynamic offline test (manual): does the app actually send 0 bytes?

TL;DR: The static audit (`audit_apk.py`) shows what the APK *can* do. This protocol shows what it *does*: run a scripted session and read the kernel's per-UID traffic counters before and after. Pass = **0 bytes rx/tx for the app's UID**, and no packets from the device to anything except the capture host. It takes about 20 minutes per device. It is not automated yet (needs a USB phone).

```bash
# 0. identify
adb shell pm list packages -U | grep -E 'aoair|competitor-a|competitor-b'   # -> package:team.sopa.aoair.offline uid:10xxx
UID=10xxx; PKG=team.sopa.aoair.offline
# 1. snapshot kernel counters for that UID (works on stock Android and GrapheneOS)
adb shell dumpsys netstats detail | grep -A3 "uid=$UID" > before.txt
adb shell cat /proc/net/xt_qtaguid/stats 2>/dev/null | awk -v u=$UID '$4==u' >> before.txt   # older kernels only
# 2. run the scripted session (below), then
adb shell dumpsys netstats detail | grep -A3 "uid=$UID" > after.txt
diff before.txt after.txt   # PASS = no diff / no bucket for the UID
```

## Three rounds (each must pass)

| # | Network state | What it proves | Pass criterion |
|---|---|---|---|
| R1 | **Airplane mode ON**, Wi-Fi OFF | The app works with no network at all (the bounty requirement) | All 10 scripted queries answer. No error or spinner caused by the network. |
| R2 | **Wi-Fi ON, connected to a capture AP** (laptop hotspot + `tcpdump -i <ap-if> -w boar.pcap`), mobile data OFF | The app *does not try* to reach the network even when it could | `dumpsys netstats` shows no bucket for the UID. The pcap has no flow attributable to the app (only OS noise such as connectivity checks, NTP and Play Services, which you must separate by UID via netstats). |
| R3 | **GrapheneOS**, Network permission toggled OFF for the app (only visible if the APK requests INTERNET) | Covers the downloader flavor: OS-level denial of both direct and indirect network access ([GrapheneOS features](https://grapheneos.org/features#network-permission-toggle)) | Offline features work. Downloads fail cleanly with a clear message. |

If the APK has **no INTERNET permission** (the BOAR offline flavor, a competitor team, a competitor team), R3 is moot: the toggle does not appear because the kernel already denies sockets to the UID. Record that fact instead.

## Scripted session (same for every app, so results are comparable)

1. Cold start (force-stop first: `adb shell am force-stop $PKG`).
2. Five queries from `rnd/lantern/vitalik-evalset.jsonl`: `vit-cry-005` (Privacy Pools vs Tornado), `vit-cry-007` (d/acc), `vit-fa-007` and `vit-cry-008` (honest refusal: the app must say the offline source doesn't cover it; see `grading.refuse_ok`), plus one "near me" query with location ON. Refusals are the interesting case, because an app that "looks it up" online would answer instead.
3. Import one PDF through the document picker. Ask about it.
4. Open settings, the model list and the knowledge packs screen (screens that *would* show download UI).
5. Background the app for 5 minutes (catches retries on foreground, e.g. BOAR `SetupWizardScreen.tsx:1057`), foreground, one more query.
6. Tap a citation link / a place card (`geo:` hand-off). **Expected**: this leaves the app via an Intent. It is recorded as *user-mediated egress by another app*, not app traffic.

## What to record (append to `reports/dynamic-<device>-<date>.md`)

- Device, OS build (e.g. `adb shell getprop ro.build.fingerprint`), GrapheneOS yes/no, sandboxed Play installed yes/no
- APK sha256 (must match a static report in `reports/`)
- R1/R2/R3 pass/fail, bytes rx/tx per UID (from netstats), pcap sha256, and the list of flows by UID
- A screen recording of R1 (this doubles as bounty proof: "app running offline")

## Known blind spots

- **Delegated egress**: the browser, the maps app (`geo:`), the share target, the keyboard/IME, and the speech recognizer (voice input runs in the provider's process, which has its own INTERNET) are *other UIDs*. Their traffic is not the app's. Recording it is still useful, because the user perceives it as "the app sent something".
- **Passive location**: BOAR's `PASSIVE_PROVIDER` fallback may return a fix originally obtained by another app with network assistance (`modules/offline-location/.../OfflineLocationModule.kt:124,152`). It makes no traffic, but it is not pure GPS.
- netstats buckets are coarse (roughly 2 h). Run R2 on a freshly rebooted device, or compare the UID's totals, not the deltas of other UIDs.

UNKNOWN: whether `dumpsys netstats detail` output format is identical on GrapheneOS 2026 builds (untested, no device on hand). UNKNOWN: whether DownloadManager (a system UID) would download on behalf of an app without INTERNET. AOSP behaviour has not been checked against source, so R2 would catch it as a system-UID flow right after an app action.
