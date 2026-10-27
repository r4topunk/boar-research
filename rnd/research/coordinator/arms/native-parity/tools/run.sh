#!/bin/bash
# NATIVE-PARITY: desktop run of the native engine's answer path up to the prompt (0 LLM generation, 0 judge).
# MacBook. Needs: JDK 17, Gradle 8.14.3 (wrapper cache), llama-server b11010 (spikes/), bge-small + Qwen2.5-1.5B GGUFs.
set -euo pipefail
B=<workspace>; ARM=$B/rnd/research/coordinator/arms/native-parity; W=$ARM/work
SNAP=$B/wt/native-qa/android-native   # snapshot 5f8cc8f4, read-only
export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
GRADLE=$(ls -d $HOME/.gradle/wrapper/dists/gradle-8.14.3-bin/*/gradle-8.14.3)/bin/gradle
# llama-server b11010 CPU, copied with an @executable_path rpath (the spikes/ copy points at a deleted build dir)
if [ ! -x $W/llama-bin/llama-server ]; then mkdir -p $W; cp -R $B/spikes/llama-b11010-cpu/bin $W/llama-bin; install_name_tool -add_rpath @executable_path $W/llama-bin/llama-server; codesign -s - -f $W/llama-bin/llama-server; fi
LS=$W/llama-bin/llama-server
rm -rf $W/engine-src && cp -R $SNAP/engine/src/main/java $W/engine-src && bash $ARM/tools/cutoff.patch.sh $W/engine-src
# servers: embedder (bge-small, ctx 512 as the app) and the 1.5B for its chat template + tokenizer
pgrep -f "port 8181" >/dev/null || { $LS -m $B/shared-models/bge-small-en-v1.5-q8_0.gguf --embedding -c 512 -b 512 -ub 512 -t 4 --port 8181 >$W/emb.log 2>&1 & }
pgrep -f "port 8182" >/dev/null || { $LS -m $B/shared-models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf -c 4096 -t 2 --port 8182 >$W/tok.log 2>&1 & }
for p in 8181 8182; do for i in $(seq 60); do curl -sf localhost:$p/health >/dev/null && break; sleep 1; done; done
export ENGINE_SRC=$W/engine-src BUILD_DIR=$W/build RUN_DIR=$W
COMMON="--questions ${QUESTIONS:-$W/questions-main97.jsonl} --kb $W/kb-standard.sqlite --corpus $B/wt/native-qa/assets/corpus \
 --embed http://127.0.0.1:8181 --embed-cache $W/embed-cache.jsonl --tok http://127.0.0.1:8182 \
 --personalities $SNAP/app/src/main/assets/boar-data/personalities.json --lexicon $B/wt/native-qa/assets/lexicon/pt-en.json"
KIT="$B/shared-data/crypto/boar-crypto.sqlite,$B/shared-data/packs/boar-wikivoyage-en.sqlite"
cd $ARM/tools/harness
$GRADLE -q --no-daemon installDist
BIN=$W/build/install/native-parity-harness/bin/native-parity-harness
$BIN $COMMON --label kb --cutoffs 0.7,0.5,0.3 --out $W/out/kb.jsonl
$BIN $COMMON --label kbpacks --packs "$KIT" --cutoffs 0.7,0.5,0.3 --out $W/out/kbpacks.jsonl
bash $ARM/tools/run_vital5.sh
