# offline-proof report: `competitor-b-1.1.10.apk`

TL;DR: **NO-NETWORK-BY-CONSTRUCTION**. INTERNET=no, GMS=no, trackers=0, hosts to review=10.

## Findings

- LOW: allowBackup not false; relies on dataExtractionRules (Android 12+) and fullBackupContent (<unset>) for Android <=11. Check the rules exclude app data.

## Identity

| field | value |
|---|---|
| package | `<competitor package>` 1.1.10 (13) |
| sha256 | `5bc392c3f18ac25d0797c93a6b4f2cd95452146942f659035cd861d1cd54799d` |
| size | 49,155,300 bytes, 234 entries |
| sdk | min 33 / target 36 |
| signing | v1=False v2=True v3=False debug-cert=False subject=`O=Independent Developer, CN=POIDH Bounty 31 Android Release` |
| signer cert sha256 | `131127512c99a625acd0dd4baf20e1c7cd240b0fd573449197070000e3d6b666` |
| tool | offline-proof/audit_apk.py 0.2.0 (signing block parsed, signature NOT cryptographically verified: use `apksigner verify`) |

## 1. Permissions

All declared: `<competitor package>.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION`

Network-related: **none**

Sensitive: none

## 2. Manifest flags

| flag | value |
|---|---|
| allowBackup | `<unset>` |
| fullBackupContent | `<unset>` |
| dataExtractionRules | `@0x7f0c0000` |
| usesCleartextTraffic | `false` |
| networkSecurityConfig | `<unset>` |
| debuggable | `<unset>` |
| extractNativeLibs | `true` |
| sharedUserId | `<none>` |
| uses-library | <none> |

<details><summary>meta-data (3)</summary>

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

none found

## 7. Native libraries with network imports

| lib | imported network symbols | linked net/TLS libs |
|---|---|---|
| `lib/arm64-v8a/libllama-common.so` | bind, connect, getaddrinfo, listen, sendto, socket | - |

## 8. Embedded hosts

Classes: `review` = could be contacted at runtime and needs a justification; `doc-link` = error/doc URLs; `namespace` = XML/schema identifiers; `local/dev` = loopback/dev server. Syntactically invalid hosts (text fragments) are counted but not listed.

| host | class | urls | where | example |
|---|---|---|---|---|
| `android.googlesource.com` | review | 4 | lib/arm64-v8a/libai-chat.so, lib/arm64-v8a/libandroidx.graphics.path.so, lib/arm64-v8a/libdatastore_shared_counter.so … | `https://android.googlesource.com/toolchain/clang` |
| `auth.docker.io` | review | 1 | lib/arm64-v8a/libllama-common.so | `https://auth.docker.io/token?service=registry.docker.io&scope=repository` |
| `creativecommons.org` | review | 1 | assets/competitor-b-reference-1.0.0.fapack | `https://creativecommons.org/publicdomain/zero/1.0/legalcode` |
| `docs.z.ai` | review | 1 | lib/arm64-v8a/libllama-common.so | `https://docs.z.ai/guides/capabilities/thinking-mode#preserved-thinking` |
| `ggml.ai` | review | 1 | lib/arm64-v8a/libllama-common.so | `https://ggml.ai/f0.png` |
| `goo.gle` | review | 1 | classes.dex | `https://goo.gle/compose-feedback` |
| `huggingface.co` | review | 1 | lib/arm64-v8a/libllama-common.so | `https://huggingface.co/` |
| `openmp.llvm.org` | review | 1 | lib/arm64-v8a/libomp.so | `http://openmp.llvm.org/` |
| `registry-1.docker.io` | review | 1 | lib/arm64-v8a/libllama-common.so | `https://registry-1.docker.io/v2/` |
| `youtrack.jetbrains.com` | review | 1 | classes.dex | `https://youtrack.jetbrains.com/issue/KT-55980` |
| `github.com` | doc-link | 12 | lib/arm64-v8a/libdatastore_shared_counter.so, lib/arm64-v8a/libllama-common.so, lib/arm64-v8a/libllama.so … | `https://github.com/Kotlin/llvm-project` |
| `json-schema.org` | namespace | 1 | lib/arm64-v8a/libllama-common.so | `https://json-schema.org/` |
| `localhost` | local/dev | 1 | lib/arm64-v8a/libllama-common.so | `http://localhost:8080` |
| `www.apache.org` | namespace | 2 | META-INF/androidx/annotation/annotation/LICENSE.txt, META-INF/androidx/collection/collection-ktx/LICENSE.txt, META-INF/androidx/collection/collection/LICENSE.txt … | `http://www.apache.org/licenses/` |

0 invalid host fragments skipped.

Watch-listed domains (substring, catches runtime-built URLs): `huggingface.co` (lib/arm64-v8a/libllama-common.so)

## 9. Indirect egress channels (work even without INTERNET)

- Exported receiver androidx.profileinstaller.ProfileInstallReceiver schemes=- permission=android.permission.DUMP

## Limits of a static audit

- Proves *capability*, not *behaviour*. Without INTERNET the kernel blocks sockets for this UID, which is the strongest static guarantee; with INTERNET, hosts built at runtime or fetched from config are invisible here.
- Does not see what other apps (browser, GMS, keyboard, speech service) do with data handed to them.
- Pair with the dynamic test in `DYNAMIC-TEST.md`.
