#!/usr/bin/env bash
# BATCHRET-PHONE: same-session A/B on litelat-9 (Qwen3-1.7B), A = cmp30off APK, B = cmp30off + batchret APK, order A B A B.
# Each run: adb install -r (keeps files/), thermal gate (status 0, battery <= 34.0 C), boar_bench.py run (cold start).
set -euo pipefail
export PATH="$HOME/Library/Android/sdk/platform-tools:$PATH"
BOAR=<workspace>; HERE="${BOAR}/rnd/research/coordinator/arms/batchret/phone"; BENCH="${BOAR}/handoff/pixel8-2026-10-20/bench"
A="${BOAR}/bench-app/build/boar-bench-0cfd4a77-cut7-cmp30off-nonet-c407db3224e2.apk"
B="${BOAR}/bench-app/build/boar-bench-0cfd4a77-cut7-cmp30off-batchret-nonet-0ca54d870ba8.apk"
for spec in "batchret-1a:$A" "batchret-2b:$B" "batchret-3a:$A" "batchret-4b:$B"; do
  rid="${spec%%:*}"; apk="${spec#*:}"
  echo "=== $rid $(basename "$apk") $(date +%H:%M:%S)"
  adb install -r "$apk"
  python3 "$HERE/thermal_gate.py" "$rid" 340
  (cd "$BENCH" && python3 boar_bench.py run "$rid" --timeout-min 30)
done
echo "=== all done $(date +%H:%M:%S)"
