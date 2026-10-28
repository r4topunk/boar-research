# offline-proof report: `competitor-a-1.0.0.apk`

TL;DR: **NO-NETWORK-BY-CONSTRUCTION**. INTERNET=no, GMS=no, trackers=0, hosts to review=7.

## Findings

- MEDIUM: shared-storage write access: model/corpus files there can be tampered with by other apps.

## Identity

| field | value |
|---|---|
| package | `<competitor package>` 1.0.0-dev (100) |
| sha256 | `246bd4ee2ed7049d63b2b5ec926ca3efab29ea677d9c7f817a16a5e1bb4fc013` |
| size | 56,857,610 bytes, 152 entries |
| sdk | min 29 / target 34 |
| signing | v1=False v2=True v3=False debug-cert=False subject=`O=a competitor team, CN=a competitor team` |
| signer cert sha256 | `51b8c61c8f1a435e094964a5f6a31eac97f6552c2d4ed2420c5539c43bb83da3` |
| tool | offline-proof/audit_apk.py 0.2.0 (signing block parsed, signature NOT cryptographically verified: use `apksigner verify`) |

## 1. Permissions

All declared: `FOREGROUND_SERVICE`, `FOREGROUND_SERVICE_DATA_SYNC`, `MANAGE_EXTERNAL_STORAGE`, `POST_NOTIFICATIONS`, `WAKE_LOCK`, `<competitor package>`

Network-related: **none**

Sensitive: `MANAGE_EXTERNAL_STORAGE` (all-files access (shared storage is readable by other apps)), `POST_NOTIFICATIONS` (notifications)

## 2. Manifest flags

| flag | value |
|---|---|
| allowBackup | `false` |
| fullBackupContent | `<unset>` |
| dataExtractionRules | `<unset>` |
| usesCleartextTraffic | `<unset>` |
| networkSecurityConfig | `<unset>` |
| debuggable | `<unset>` |
| extractNativeLibs | `true` |
| sharedUserId | `<none>` |
| uses-library | <none> |

<details><summary>meta-data (4)</summary>

- `android.support.FILE_PROVIDER_PATHS=@0x7f0c0000`
- `androidx.emoji2.text.EmojiCompatInitializer=androidx.startup`
- `androidx.lifecycle.ProcessLifecycleInitializer=androidx.startup`
- `androidx.profileinstaller.ProfileInstallerInitializer=androidx.startup`

</details>

## 3. Google Play Services / Firebase

none found

## 4. Tracker / analytics SDKs (Exodus-style class signatures)

none found

## 5. Remote code loading (OTA / dev launcher)

none found

## 6. Network-capable libraries present (capability, not proof of use)

- **java.net.Socket**: `java.net.Socket`
- **android.webkit.WebView**: `android.webkit.WebView`
- **android.app.DownloadManager**: `android.app.DownloadManager`

## 7. Native libraries with network imports

| lib | imported network symbols | linked net/TLS libs |
|---|---|---|
| `lib/arm64-v8a/libllama-common.so` | bind, connect, getaddrinfo, listen, sendto, socket | - |

## 8. Embedded hosts

Classes: `review` = could be contacted at runtime and needs a justification; `doc-link` = error/doc URLs; `namespace` = XML/schema identifiers; `local/dev` = loopback/dev server. Syntactically invalid hosts (text fragments) are counted but not listed.

| host | class | urls | where | example |
|---|---|---|---|---|
| `android.googlesource.com` | review | 3 | lib/arm64-v8a/libandroidx.graphics.path.so, lib/arm64-v8a/libbmoe-cli.so, lib/arm64-v8a/libc++_shared.so … | `https://android.googlesource.com/toolchain/clang` |
| `auth.docker.io` | review | 1 | lib/arm64-v8a/libllama-common.so | `https://auth.docker.io/token?service=registry.docker.io&scope=repository` |
| `docs.z.ai` | review | 1 | lib/arm64-v8a/libllama-common.so | `https://docs.z.ai/guides/capabilities/thinking-mode#preserved-thinking` |
| `ggml.ai` | review | 1 | lib/arm64-v8a/libllama-common.so | `https://ggml.ai/f0.png` |
| `goo.gle` | review | 1 | classes.dex | `https://goo.gle/compose-feedback` |
| `huggingface.co` | review | 1 | lib/arm64-v8a/libllama-common.so | `https://huggingface.co/` |
| `registry-1.docker.io` | review | 1 | lib/arm64-v8a/libllama-common.so | `https://registry-1.docker.io/v2/` |
| `github.com` | doc-link | 10 | lib/arm64-v8a/libllama-common.so, lib/arm64-v8a/libllama.so | `https://github.com/ggml-org/llama.cpp/issues` |
| `issuetracker.google.com` | doc-link | 2 | classes.dex | `https://issuetracker.google.com/issues/297974033` |
| `json-schema.org` | namespace | 1 | lib/arm64-v8a/libllama-common.so | `https://json-schema.org/` |
| `localhost` | local/dev | 1 | lib/arm64-v8a/libllama-common.so | `http://localhost:8080` |
| `schemas.android.com` | namespace | 1 | classes.dex | `http://schemas.android.com/apk/res/android` |
| `www.w3.org` | namespace | 1 | classes.dex | `http://www.w3.org/2000/svg` |

0 invalid host fragments skipped.

Watch-listed domains (substring, catches runtime-built URLs): `huggingface.co` (lib/arm64-v8a/libllama-common.so)

## 9. Indirect egress channels (work even without INTERNET)

- Shared-storage access: files placed there (models, corpora, exports) are readable/writable by other apps that may have INTERNET (exfiltration or tampering by a colluding app).
- Exported receiver androidx.profileinstaller.ProfileInstallReceiver schemes=- permission=android.permission.DUMP

## Limits of a static audit

- Proves *capability*, not *behaviour*. Without INTERNET the kernel blocks sockets for this UID, which is the strongest static guarantee; with INTERNET, hosts built at runtime or fetched from config are invisible here.
- Does not see what other apps (browser, GMS, keyboard, speech service) do with data handed to them.
- Pair with the dynamic test in `DYNAMIC-TEST.md`.
