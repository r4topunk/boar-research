#!/usr/bin/env bash
# One heavy-queue job per model (exp-01 / exp-02). Runs on the Mac mini from <runner>/kiln.
# Usage (on the mini): <runner>/bin/run-heavy Kiln bash <runner>/kiln/harness/run-model.sh <model-id>
# Waits for the 1-min load average to drop below 8 before starting (coordinator's gate).
set -euo pipefail
cd <runner>/kiln
SERVER_B8="$HOME/boar/spikes/bmoe/third_party/llama.cpp/build-cpu/bin/llama-server"   # llama.cpp 0e8c83e (2026-08-28)
SERVER_MAPLE="$HOME/boar/spikes/llama-b11010/build-cpu/bin/llama-server"              # llama.cpp b11010 (exp-02 only)
case "$1" in
  qwen2.5-1.5b) GGUF=<runner>/shared-models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf; SHA=1adf0b11065d8ad2e8123ea110d1ec956dab4ab038eab665614adba04b6c3370; SERVER=$SERVER_B8 ;;
  qwen3-4b)     GGUF=<runner>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf; SHA=3605803b982cb64aead44f6c1b2ae36e3acdb41d8e46c8a94c6533bc4c67e597; SERVER=$SERVER_B8 ;;
  ling-3.0-tiny) GGUF=<runner>/kiln/models/Ling-3.0-tiny-Q4_K_M.gguf; SHA=246d67d45f5b0c7447ca0ce0bdb8b46b8a47b593c5068635dc16422c051d7be9; SERVER=$SERVER_B8 ;;
  qwen3-4b-b11010) GGUF=<runner>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf; SHA=3605803b982cb64aead44f6c1b2ae36e3acdb41d8e46c8a94c6533bc4c67e597; SERVER=$SERVER_MAPLE ;;
  maple-preview) GGUF=<runner>/kiln/models/maple-preview-TQ2_0-head-Q4_K.gguf; SHA=221f792cc9760d27a34f449b4229e258fa968a63bd4213993e45d9c0bb477a9e; SERVER=$SERVER_MAPLE ;;
  *) echo "unknown model $1"; exit 2 ;;
esac
waited=0
while awk -v l="$(sysctl -n vm.loadavg | awk '{print $2}')" 'BEGIN{exit !(l >= 8)}'; do
  [ $waited -ge 1200 ] && { echo "load stayed >= 8 for 20 min, giving up"; exit 4; }
  sleep 15; waited=$((waited + 15))
done
echo "load gate passed after ${waited}s: $(sysctl -n vm.loadavg)"
mkdir -p runs
python3 harness/serve-bench.py --model-id "$1" --gguf "$GGUF" --sha256 "$SHA" --server "$SERVER" \
  --captures capture/v2-hard12.jsonl,capture/lantern52.jsonl --out "runs/$1.jsonl" ${KILN_SERVER_ARGS:-}
# exp-02 onward: KILN_SERVER_ARGS="--server-arg=--cache-ram --server-arg=0" (no server prompt cache, memory valid in one pass)
