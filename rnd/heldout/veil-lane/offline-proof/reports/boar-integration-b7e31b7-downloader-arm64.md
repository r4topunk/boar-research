# offline-proof report: `boar-integration-b7e31b7-downloader-arm64.apk`

TL;DR: **NETWORK-CAPABLE**. INTERNET=yes, GMS=no, trackers=0, hosts to review=21.

## Findings

- HIGH if distributed / MEDIUM for local test builds: signed with a PUBLIC key (React Native / Expo prebuild template debug.keystore (SHA-1 5E:8F:16:06:2E:A3:CD:2C:...)). Anyone can sign an APK with the same package name that Android accepts as an update over this one, inheriting the app's private data. Never ship it; check the distributed APK's signer.
- HIGH: declares INTERNET; every `review` host below needs a justification and a dynamic test.
- INFO: Expo dev-launcher module present as a 8-class stub (no DevLauncherController/launcher package): consistent with the release no-op variant.

## Identity

| field | value |
|---|---|
| package | `team.sopa.aoair` 1.0.0 (1) |
| sha256 | `206ddccb9c1cd208f1a564a264aefed4c474b4b62d176ae447a2054bb7d92272` |
| size | 135,950,326 bytes, 1331 entries |
| sdk | min 24 / target 36 |
| signing | v1=False v2=True v3=False debug-cert=True subject=`O=Unknown, CN=Android Debug` |
| signer cert sha256 | `fac61745dc0903786fb9ede62a962b399f7348f0bb6f899b8332667591033b9c` |
| tool | offline-proof/audit_apk.py 0.2.0 (signing block parsed, signature NOT cryptographically verified: use `apksigner verify`) |

## 1. Permissions

All declared: `ACCESS_COARSE_LOCATION`, `ACCESS_FINE_LOCATION`, `INTERNET`, `RECORD_AUDIO`, `VIBRATE`, `WAKE_LOCK`, `team.sopa.aoair.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION`

Network-related: `android.permission.INTERNET` (open network sockets (kernel-enforced via the inet group))

Sensitive: `ACCESS_COARSE_LOCATION` (approximate location), `ACCESS_FINE_LOCATION` (precise location), `RECORD_AUDIO` (microphone)

## 2. Manifest flags

| flag | value |
|---|---|
| allowBackup | `false` |
| fullBackupContent | `false` |
| dataExtractionRules | `@0x7f130001` |
| usesCleartextTraffic | `false` |
| networkSecurityConfig | `<unset>` |
| debuggable | `<unset>` |
| extractNativeLibs | `false` |
| sharedUserId | `<none>` |
| uses-library | androidx.window.extensions (required=false), androidx.window.sidecar (required=false) |

`<queries>`: `android.intent.action.OPEN_DOCUMENT */*`; `android.intent.action.OPEN_DOCUMENT_TREE`; `android.intent.action.SEND */*`; `android.intent.action.VIEW https`

<details><summary>meta-data (12)</summary>

- `android.support.FILE_PROVIDER_PATHS=@0x7f130002`
- `android.support.FILE_PROVIDER_PATHS=@0x7f130008`
- `androidx.emoji2.text.EmojiCompatInitializer=androidx.startup`
- `androidx.lifecycle.ProcessLifecycleInitializer=androidx.startup`
- `androidx.profileinstaller.ProfileInstallerInitializer=androidx.startup`
- `com.facebook.soloader.enabled=true`
- `expo.modules.clipboard.CLIPBOARD_FILE_PROVIDER_PATHS=@0x7f130000`
- `expo.modules.updates.ENABLED=false`
- `expo.modules.updates.ENABLE_BSDIFF_PATCH_SUPPORT=true`
- `expo.modules.updates.EXPO_UPDATES_CHECK_ON_LAUNCH=ALWAYS`
- `expo.modules.updates.EXPO_UPDATES_LAUNCH_WAIT_MS=0`
- `org.unimodules.core.AppLoader#react-native-headless=expo.modules.adapters.react.apploader.RNHeadlessAppLoader`

</details>

## 3. Google Play Services / Firebase

none found

## 4. Tracker / analytics SDKs (Exodus-style class signatures)

none found

## 5. Remote code loading (OTA / dev launcher)

- **Expo dev launcher (loads JS from a URL)**: `expo.modules.devlauncher.BuildConfig`, `expo.modules.devlauncher.DevLauncherPackage`, `expo.modules.devlauncher.DevLauncherPackageDelegate`, `expo.modules.devlauncher.R`, `expo.modules.devlauncher.modules.ExpoDevLauncherModule`, `... +3 more`

## 6. Network-capable libraries present (capability, not proof of use)

- **OkHttp**: `okhttp3.Address`, `okhttp3.Authenticator`, `okhttp3.Authenticator$Companion`, `okhttp3.Authenticator$Companion$AuthenticatorNone`, `okhttp3.Cache`, `... +318 more`
- **java.net.HttpURLConnection**: `java.net.HttpURLConnection`
- **java.net.Socket**: `java.net.Socket`
- **android.webkit.WebView**: `android.webkit.WebView`
- **React Native networking**: `com.facebook.react.modules.network.CookieJarContainer`, `com.facebook.react.modules.network.CustomClientBuilder`, `com.facebook.react.modules.network.ForwardingCookieHandler`, `com.facebook.react.modules.network.ForwardingCookieHandler$$ExternalSyntheticLambda0`, `com.facebook.react.modules.network.ForwardingCookieHandler$Companion`, `... +27 more`
- **React Native WebSocket**: `com.facebook.react.modules.websocket.WebSocketModule`, `com.facebook.react.modules.websocket.WebSocketModule$Companion`, `com.facebook.react.modules.websocket.WebSocketModule$ContentHandler`, `com.facebook.react.modules.websocket.WebSocketModule$connect$2`

## 7. Native libraries with network imports

none

JS bundle: Hermes bytecode v98, 192,040 strings decoded (99.9% printable, parse sanity check).

## 8. Embedded hosts

Classes: `review` = could be contacted at runtime and needs a justification; `doc-link` = error/doc URLs; `namespace` = XML/schema identifiers; `local/dev` = loopback/dev server. Syntactically invalid hosts (text fragments) are counted but not listed.

| host | class | urls | where | example |
|---|---|---|---|---|
| `android.googlesource.com` | review | 1 | lib/arm64-v8a/libappmodules.so, lib/arm64-v8a/libc++_shared.so, lib/arm64-v8a/libexpo-modules-core.so … | `https://android.googlesource.com/toolchain/llvm-project` |
| `archive.org` | review | 1 | assets/index.android.bundle | `https://archive.org/details/USArmyFM2176` |
| `classic-assets.eascdn.net` | review | 1 | assets/index.android.bundle | `https://classic-assets.eascdn.net/~assets/` |
| `eips.ethereum.org` | review | 1 | assets/index.android.bundle | `https://eips.ethereum.org` |
| `en.wikibooks.org` | review | 1 | assets/index.android.bundle | `https://en.wikibooks.org` |
| `en.wikipedia.org` | review | 301 | assets/index.android.bundle | `https://en.wikipedia.org/wiki/CRISPR` |
| `en.wikivoyage.org` | review | 2 | assets/index.android.bundle | `https://en.wikivoyage.org` |
| `ercs.ethereum.org` | review | 1 | assets/index.android.bundle | `https://ercs.ethereum.org` |
| `ethereum.org` | review | 1 | assets/index.android.bundle | `https://ethereum.org` |
| `filesystem.local` | review | 1 | classes2.dex | `http://filesystem.local` |
| `github.com (downloads)` | review | 1 | assets/index.android.bundle | `https://github.com/UPSTREAM_REPO/boar-app/releases/download/knowledge-pack-v1/wiki-vital5.sqlite` |
| `huggingface.co` | review | 22 | assets/index.android.bundle, lib/arm64-v8a/librnllama.so, lib/arm64-v8a/librnllama_v8.so … | `https://huggingface.co/LiquidAI/LFM2.5-8B-A1B-GGUF/resolve/49c14831707011e64d70b2ebd8462ba08d608434/LFM2.5-8B-A1B-Q4_K_M.gguf` |
| `raw.githubusercontent.com` | review | 2 | assets/index.android.bundle | `https://raw.githubusercontent.com/UPSTREAM_REPO/boar-app/9e46dc4d8f9a95bc7716194b94117f769504c0e0/assets/corpus/corpus-full.json` |
| `scripts.sil.org` | review | 1 | assets/com/tom_roush/pdfbox/resources/ttf/LiberationSans-Regular.ttf | `http://scripts.sil.org/OFL` |
| `sourceforge.net` | review | 1 | assets/com/tom_roush/pdfbox/resources/glyphlist/glyphlist.txt, assets/com/tom_roush/pdfbox/resources/glyphlist/zapfdingbats.txt | `http://sourceforge.net/adobe/aglfn/` |
| `www.android.com` | review | 1 | classes.dex | `http://www.android.com/` |
| `www.appropedia.org` | review | 1 | assets/index.android.bundle | `https://www.appropedia.org` |
| `www.ascendercorp.com` | review | 2 | assets/com/tom_roush/pdfbox/resources/ttf/LiberationSans-Regular.ttf | `http://www.ascendercorp.com/` |
| `www.openstreetmap.org` | review | 1 | assets/index.android.bundle | `https://www.openstreetmap.org/` |
| `www.ready.gov` | review | 1 | assets/index.android.bundle | `https://www.ready.gov` |
| `youtrack.jetbrains.com` | review | 2 | classes2.dex | `https://youtrack.jetbrains.com/issue/KT-55980` |
| `apache.org` | namespace | 2 | classes2.dex | `http://apache.org/xml/features/disallow-doctype-decl` |
| `dev.to` | doc-link | 1 | assets/index.android.bundle | `https://dev.to/li/how-to-requestpermission-for-devicemotion-and-deviceorientation-events-in-ios-13-46g2` |
| `docs.expo.dev` | doc-link | 2 | assets/index.android.bundle | `https://docs.expo.dev/development/introduction/` |
| `docs.swmansion.com` | doc-link | 15 | assets/index.android.bundle, classes2.dex, lib/arm64-v8a/libworklets.so | `https://docs.swmansion.com/react-native-reanimated/docs/debugging/logger-configuration` |
| `github.com` | doc-link | 26 | assets/index.android.bundle, classes.dex, classes2.dex … | `https://github.com/ethereum/yellowpaper` |
| `localhost` | local/dev | 1 | assets/index.android.bundle | `http://localhost:8081/` |
| `ns.adobe.com` | namespace | 1 | classes2.dex | `http://ns.adobe.com/xfdf/` |
| `react.dev` | doc-link | 1 | assets/index.android.bundle | `https://react.dev/link/invalid-hook-call` |
| `react.i18next.com` | doc-link | 1 | assets/index.android.bundle | `https://react.i18next.com/latest/usetranslation-hook` |
| `reactnative.dev` | doc-link | 1 | lib/arm64-v8a/libreactnative.so | `https://reactnative.dev/docs/debugging` |
| `reactnavigation.org` | doc-link | 8 | assets/index.android.bundle | `https://reactnavigation.org/docs/getting-started` |
| `schemas.android.com` | namespace | 2 | classes.dex, classes2.dex | `http://schemas.android.com/apk/res-auto` |
| `www.apache.org` | namespace | 2 | META-INF/androidx/annotation/annotation/LICENSE.txt, assets/com/tom_roush/pdfbox/resources/glyphlist/additional.txt, org/apache/commons/codec/language/bm/ash_approx_any.txt … | `http://www.apache.org/licenses/` |
| `www.bouncycastle.org` | namespace | 1 | classes3.dex | `https://www.bouncycastle.org` |
| `www.unicode.org` | doc-link | 6 | assets/com/tom_roush/fontbox/resources/unicode/Scripts.txt, assets/com/tom_roush/pdfbox/resources/text/BidiMirroring.txt | `http://www.unicode.org/reports/tr24/` |
| `xml.org` | namespace | 2 | classes2.dex | `http://xml.org/sax/features/external-general-entities` |

0 invalid host fragments skipped.

Watch-listed domains (substring, catches runtime-built URLs): `githubusercontent.com` (assets/index.android.bundle), `huggingface.co` (assets/index.android.bundle, lib/arm64-v8a/librnllama.so)

IPv4 literals in dex: `10.0.1.1`, `10.0.2.2`, `10.0.3.2`, `127.0.0.1`

## 9. Indirect egress channels (work even without INTERNET)

- Declares <queries> for VIEW http(s): can hand a URL to a browser (user-visible; URL could carry data).
- Declares <queries> for SEND: can open the share sheet (user-mediated export).
- Exported activity team.sopa.aoair.MainActivity schemes=['exp+boar-app'] permission=-
- Exported receiver androidx.profileinstaller.ProfileInstallReceiver schemes=- permission=android.permission.DUMP

## Limits of a static audit

- Proves *capability*, not *behaviour*. Without INTERNET the kernel blocks sockets for this UID, which is the strongest static guarantee; with INTERNET, hosts built at runtime or fetched from config are invisible here.
- Does not see what other apps (browser, GMS, keyboard, speech service) do with data handed to them.
- Pair with the dynamic test in `DYNAMIC-TEST.md`.
