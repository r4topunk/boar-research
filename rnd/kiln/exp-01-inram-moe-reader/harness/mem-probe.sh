#!/usr/bin/env bash
# Memory probe without llama-server's host prompt cache (--cache-ram 0): 5 longest-context v2 items, same settings
# as the main run otherwise. The main run left the default --cache-ram 8192 MiB on, which inflates peak footprint.
# Usage (on the mini): <runner>/bin/run-heavy Kiln bash <runner>/kiln/harness/mem-probe.sh <model-id> <gguf> <sha256> [server]
set -euo pipefail
cd <runner>/kiln
SERVER="${4:-$HOME/boar/spikes/bmoe/third_party/llama.cpp/build-cpu/bin/llama-server}"
mkdir -p runs-mem
python3 harness/serve-bench.py --model-id "$1" --gguf "$2" --sha256 "$3" --server "$SERVER" \
  --captures capture/v2-hard12.jsonl --limit 6 --out "runs-mem/$1.jsonl" --server-arg=--cache-ram --server-arg=0
