#!/bin/bash
# Forge job 2 (+ job 1a): <runner>/android/forge-build = git archive 0cfd4a77 + forge-arms.patch (914086dc…a107f), node_modules
# APFS-cloned from <runner>-and-build (same lockfile 45d66dd9), expo prebuild done, release buildType = debug keystore + debuggable.
# Runs inside <runner>/bin/run-heavy: (a) vitest suite, (D) assembleDebug dev client (Plumb's recipe), (R) assembleRelease with JS
# bundled + EXPO_PUBLIC_DEVICE_EVAL=1. Both arm64-v8a, same rnllama variants. Disk watchdog: abort below FORGE_FLOOR (18) GiB
# during a build; build outputs are deleted after each copy so the steady state stays >= 25 GiB. FORGE_ONLY=release skips (a)+(D).
set -uo pipefail
R=$HOME/boar/android/forge-build; cd "$R"; OUT=$HOME/boar/android/apk
export JAVA_HOME=$(/usr/libexec/java_home -v 17) ANDROID_HOME=$HOME/Library/Android/sdk ANDROID_SDK_ROOT=$HOME/Library/Android/sdk CI=1
free() { df -g ~ | tail -1 | awk '{print $4}'; }
echo "[forge] $(date +%T) start free $(free) GB"
# (a) unit suite on the patched tree
[ "${FORGE_ONLY:-}" = release ] || npx vitest run > vitest.log 2>&1; echo "[forge] vitest rc=$? $(grep -E 'Test Files|Tests ' vitest.log | tr -s ' ' | tr '\n' ' ')"
gradle() { # task
  (cd android && ./gradlew --no-daemon -Dorg.gradle.workers.max=${GRADLE_WORKERS:-4} "$1" -PreactNativeArchitectures=arm64-v8a -PrnllamaVariants=rnllama,rnllama_v8_2_dotprod -q) > "gradle-$1.log" 2>&1 & GP=$!
  local aborted=0 minf=99; while kill -0 $GP 2>/dev/null; do f=$(free); [ "$f" -lt "$minf" ] && minf=$f; if [ "$f" -lt ${FORGE_FLOOR:-18} ]; then echo "[forge] ABORT free $f GB"; pkill -P $GP; kill $GP; pkill -f GradleDaemon; aborted=1; break; fi; sleep 10; done
  wait $GP; local rc=$?; echo "[forge] $1 rc=$rc aborted=$aborted min free ${minf} GB $(date +%T)"; [ $rc -eq 0 ] && [ $aborted -eq 0 ]
}
t=$(date +%s)
if [ "${FORGE_ONLY:-}" = release ]; then echo "[forge] D skipped"; elif gradle :app:assembleDebug; then
  A=$OUT/boar-0cfd4a77-forge-debug-arm64.apk; cp android/app/build/outputs/apk/debug/app-debug.apk "$A"; shasum -a 256 "$A" | tee "$A.sha256"
else tail -30 gradle-:app:assembleDebug.log; fi
echo "[forge] D took $(( $(date +%s) - t ))s"; t=$(date +%s)
rm -rf android/app/build; for d in node_modules/*/android/build node_modules/@*/*/android/build; do [ -d "$d" ] && rm -rf "$d"; done; echo "[forge] D outputs cleaned, free $(free) GB"
if EXPO_PUBLIC_DEVICE_EVAL=1 gradle :app:assembleRelease; then
  A=$OUT/boar-0cfd4a77-forge-release-arm64.apk; cp android/app/build/outputs/apk/release/app-release.apk "$A"; shasum -a 256 "$A" | tee "$A.sha256"
else tail -30 gradle-:app:assembleRelease.log; fi
echo "[forge] R took $(( $(date +%s) - t ))s"
for v in debug release; do A=$OUT/boar-0cfd4a77-forge-$v-arm64.apk; [ -f "$A" ] || continue
  echo "[forge] $v: $(unzip -l "$A" | grep -c 'lib/arm64-v8a/libboarzstd.so') libboarzstd.so, bundle: $(unzip -l "$A" | grep -E 'assets/index.android.bundle' | awk '{print $1}')"
  unzip -l "$A" | grep -E 'lib/(armeabi|x86)' | head -2
done
A=$OUT/boar-0cfd4a77-forge-release-arm64.apk; if [ -f "$A" ]; then unzip -p "$A" assets/index.android.bundle | head -c 4 | xxd | head -1; fi
rm -rf android/app/build; for d in node_modules/*/android/build node_modules/@*/*/android/build; do [ -d "$d" ] && rm -rf "$d"; done
(cd android && ./gradlew --stop >/dev/null 2>&1 || true)
echo "[forge] done free $(free) GB"
