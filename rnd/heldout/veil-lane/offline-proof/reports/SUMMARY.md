# offline-proof summary

TL;DR: one row per APK. `NO-NETWORK-BY-CONSTRUCTION` = no INTERNET permission, no GMS, no tracker classes.

| apk | package | verdict | INTERNET | net perms | GMS | trackers | remote code | review hosts | sensitive perms | signer | sha256 (12) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `competitor-a-1.0.0.apk` | `<competitor package>` | **NO-NETWORK-BY-CONSTRUCTION** | no | 0 | - | - | - | 7 (android.googlesource.com, auth.docker.io, docs.z.ai, ggml.ai…) | MANAGE_EXTERNAL_STORAGE, POST_NOTIFICATIONS | O=a competitor team, CN=a competitor team | `246bd4ee2ed7` |
| `competitor-b-1.1.10.apk` | `<competitor package>` | **NO-NETWORK-BY-CONSTRUCTION** | no | 0 | - | - | - | 10 (android.googlesource.com, auth.docker.io, creativecommons.org, docs.z.ai…) | - | O=Independent Developer, CN=POIDH Bounty 31 Android Release | `5bc392c3f18a` |
| `boar-integration-1928502d-offline-arm64.apk` | `team.sopa.aoair.offline` | **NO-NETWORK-BY-CONSTRUCTION** | no | 0 | - | - | Expo dev launcher (loads JS from a URL) (stub) | 21 (android.googlesource.com, archive.org, classic-assets.eascdn.net, eips.ethereum.org…) | ACCESS_COARSE_LOCATION, ACCESS_FINE_LOCATION | **public debug key** | `14216e92637d` |
| `boar-integration-b7e31b7-downloader-arm64.apk` | `team.sopa.aoair` | **NETWORK-CAPABLE** | yes | 1 | - | - | Expo dev launcher (loads JS from a URL) (stub) | 21 (android.googlesource.com, archive.org, classic-assets.eascdn.net, eips.ethereum.org…) | ACCESS_COARSE_LOCATION, ACCESS_FINE_LOCATION, RECORD_AUDIO | **public debug key** | `206ddccb9c1c` |
| `boar-main-9898b35-release-arm64.apk` | `team.sopa.aoair` | **NETWORK-CAPABLE** | yes | 1 | - | - | Expo dev launcher (loads JS from a URL) (stub) | 12 (android.googlesource.com, classic-assets.eascdn.net, en.wikipedia.org, filesystem.local…) | READ_EXTERNAL_STORAGE, RECORD_AUDIO, SYSTEM_ALERT_WINDOW, WRITE_EXTERNAL_STORAGE | **public debug key** | `d2ca3827f348` |
| `boar-v1.0.0-arm64.apk` | `team.sopa.aoair` | **NETWORK-CAPABLE** | yes | 1 | - | - | Expo dev launcher (loads JS from a URL) (stub) | 12 (android.googlesource.com, classic-assets.eascdn.net, en.wikipedia.org, filesystem.local…) | READ_EXTERNAL_STORAGE, RECORD_AUDIO, SYSTEM_ALERT_WINDOW, WRITE_EXTERNAL_STORAGE | O=sopa.team, CN=BOAR | `de9e3156b459` |
