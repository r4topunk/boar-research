#!/bin/bash
# RULER-FINAL: BoarLite b4ef94f3 on ruler v0.4 (harness-lite conv, --port nh, kit = the APK bundle as arms/searchport/tools/run.sh). Derived from native_v04.sh.
# NATIVE-RC on ruler v0.4 (R3): the JVM harness 'conv' mode on the MacBook (retrieval, prompt, display step) with generation on the Mac mini
# (llama-server b11010 CPU, Qwen3-1.7B Q4_K_M b139949c, -c 4096 -t 4, port 8197) through an ssh tunnel (MacBook 8297 -> mini 8197).
# Kiln lock mini-long held by the caller. Never prints item text. usage: native_v04.sh <seed> [<seed> ...]
set -euo pipefail
B=<workspace>; A=$B/rnd/research/coordinator/arms/native-rc; W=$A/work; SNAP=$W/rf/snap; V=$W/v04; ITEMS=${ITEMS:-$V/native-items.jsonl}; OUTP=${OUTP:-$V/lite}
export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
LS=$B/rnd/research/coordinator/arms/native-parity/work/llama-bin/llama-server
pgrep -f "port 8181" >/dev/null || { $LS -m $B/shared-models/bge-small-en-v1.5-q8_0.gguf --embedding -c 512 -b 512 -ub 512 -t 4 --port 8181 >$W/emb.log 2>&1 & }
pgrep -f "port 8183" >/dev/null || { $LS -m $B/shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf --jinja --chat-template-kwargs '{"enable_thinking":false}' -c 4096 -t 2 --port 8183 >$W/tok17.log 2>&1 & }
<on the mini> "bash -c 'df -g ~ | tail -1 | awk \"{ if (\\\$4 < 25) exit 3 }\"; pgrep -f \"port 8197\" >/dev/null || { nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m <runner>/shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf -c 4096 -t 4 -np 1 --port 8197 > <runner>/kiln/native-rc/server-v04.log 2>&1 < /dev/null & }; for i in \$(seq 120); do curl -sf localhost:8197/health >/dev/null && break; sleep 1; done'"
pgrep -f "8297:127.0.0.1:8197" >/dev/null || { ssh -T -N -L 8297:127.0.0.1:8197 MINI_HOST & }
for p in 8181 8183 8297; do for i in $(seq 90); do curl -sf localhost:$p/health >/dev/null && break; sleep 1; done; done
SD=$B/shared-data/packs
KIT="wiki-vital5=$SD/wiki-vital5.sqlite,boar-crypto=$B/shared-data/crypto/boar-crypto.sqlite,boar-wikivoyage-en=$SD/boar-wikivoyage-en.sqlite,boar-factbook=$SD/wave2/boar-factbook.sqlite"
KIT="$KIT,boar-firstaid-en=$SD/v3proto/boar-firstaid-en.sqlite,boar-medlineplus-en=$SD/v3proto/boar-medlineplus-en.sqlite,qa-health-se=$SD/v3proto/qa-health-se.sqlite"
KIT="$KIT,qa-outdoors-se=$SD/v3proto/qa-outdoors-se.sqlite,qa-travel-se=$SD/v3proto/qa-travel-se.sqlite,boar-simplewiki-en=$SD/v3proto/boar-simplewiki-en.sqlite"
KIT="$KIT,qa-cooking-se=$SD/wave3/qa-cooking-se.sqlite,qa-money-se=$SD/wave3/qa-money-se.sqlite,boar-visa-en=$SD/wave4/boar-visa-en.sqlite"
for S in "$@"; do
  $W/rf/build/install/native-parity-harness/bin/native-parity-harness conv --port nh --items $ITEMS --gen http://127.0.0.1:8297 --seed $S \
    --out $OUTP-s$S.jsonl --kb $W/kb-recommended.sqlite --embed http://127.0.0.1:8181 --embed-cache $W/embed-cache.jsonl --tok http://127.0.0.1:8183 \
    --personalities $SNAP/android-native/app/src/main/assets/boar-data/personalities.json --lexicon $SNAP/assets/lexicon/pt-en.json \
    --packs "$KIT" --model-bytes 1107409472 --ctx 4096 2> $OUTP-s$S.log
  tail -1 $OUTP-s$S.log
done
pkill -f "8297:127.0.0.1:8197" || true
<on the mini> 'pkill -f "port 8197" || true'
