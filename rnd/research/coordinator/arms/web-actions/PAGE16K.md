# PAGE16K: 16 KB page-size readiness of the native app's arm64 libs (WEB 26.1a/26.1b, 0 LLM, no phone, 2026-10-21)

TL;DR: every arm64 .so in the native tree's two local APKs is already `align 2**14` (flag reached llama/ggml). The open risk is the Drive rc1 APK (16 of 19 libs at 4 KB per the handoff, not held here, not re-checked) and `useLegacyPackaging = true`, which compresses libs and removes the 16 KB backcompat path. Maintainer-note candidate for issue #88; needs r4to's OK before sending.

Tool: NDK 27.1.12297006 `llvm-objdump -p lib.so | grep LOAD` (all LOAD segments, unique align values). Libs unzipped to the scratchpad.

| APK (held) | arm64 libs | max LOAD align | not 2**14 |
|---|---|---|---|
| wt/native-qa/.../apk/devtest/app-devtest.apk (14:59) | 15 | 2**14 on all 15 (libboar_engine, libllama, libllama-common, libggml, libggml-base, 7 libggml-cpu-android_*, libc++_shared, libomp, libandroidx.graphics.path) | none |
| wt/native-qa/.../apk/perf/app-perf.apk (13:12) | 15 | 2**14 on all 15 | none |
| handoff/pixel8-2026-10-20/bench/apk/boar-bench cut7 (bench app, comparison) | 21 | 2**14 on all 21 (RN/Hermes/rnllama set) | none |
| rc1 internal APK 20d84efe (Drive) | not held | per handoff/16kb-pages-handoff-2026-10-21-1553.md: 16 of 19 at 4 KB | re-check on the real file |

`zipalign -c -P 16 4 app-devtest.apk` (build-tools 36.0.0): exit 0. Libs in that APK are stored Defl:N (compressed), so zipalign has nothing to align for them.

Build config (wt/native-qa/android-native, read-only): AGP 8.13.2 (gradle/libs.versions.toml); `ndkVersion = "27.1.12297006"` (app/build.gradle.kts l.13); engine CMake args include `-DANDROID_SUPPORT_FLEXIBLE_PAGE_SIZES=ON`; app/build.gradle.kts l.91: `packaging { jniLibs { useLegacyPackaging = true } }`; gradle.properties has no `useLegacyPackaging` and no `android.bundle.enableUncompressedNativeLibs`.

Maintainer sentence (draft, for #88):
"On our side every arm64 .so in a build of your tree is `align 2**14` with `-DANDROID_SUPPORT_FLEXIBLE_PAGE_SIZES=ON` (NDK 27.1); the rc1 APK still shows 4 KB on 16 of 19 libs, so please rebuild it from a tree with that flag in every native module (engine plus the llama/ggml variants) and check with `llvm-objdump -p lib.so | grep LOAD`. Also, `useLegacyPackaging = true` stores the libs compressed, and the official 16 KB backcompat mode only works when ELF files are stored uncompressed and 4 KB zip-aligned (developer.android.com/16kb-page-size), so a 4 KB-aligned lib then has no fallback on a 16 KB kernel; with aligned libs this is harmless, but the safer setting is to drop legacy packaging (uncompressed libs, `extractNativeLibs=false`) at the cost of a larger APK."

Caveats: the "no fallback" reading is inferred from the official text (the log's source), not tested on a 16 KB kernel (26.1c needs the phone). Dropping legacy packaging grows the APK by roughly the compressed-vs-stored delta of the libs (about 8 MB stored vs 4 MB compressed in devtest) and changes install size, a maintainer call.
Status: MAINTAINER-NOTE CANDIDATE (#88), not sent; awaiting r4to's OK.
