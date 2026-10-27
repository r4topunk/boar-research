#!/bin/bash
# NATIVE-RC PROBES-OFFICIAL prompts (upstream/main e5c7abe1 snapshot work/main/snap, harness-main built separately; PERSONA env = detailed (shipped) | succinct). Derived from prompts.sh.
# NATIVE-RC prompts on the MacBook (0 LLM generation): builds the JVM harness on the read-only engine snapshot (wt/judge-clean f1023b93,
# archived to work/snap), seeds the app's KB (builtin + corpus-standard + corpus-full, the Recommended setup), opens the kit in the app's
# order and writes one prompt row per question. usage: prompts.sh <label> <questions.jsonl> <out.jsonl> [factbook path]
set -euo pipefail
B=<workspace>; A=$B/rnd/research/coordinator/arms/native-rc; W=$A/work; SNAP=$W/main/snap
LABEL=$1; QF=$2; OUT=$3; FB=${4:-$B/shared-data/packs/wave2/boar-factbook.sqlite}
export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
GRADLE=$(ls -d $HOME/.gradle/wrapper/dists/gradle-8.14.3-bin/*/gradle-8.14.3)/bin/gradle
LS=$B/rnd/research/coordinator/arms/native-parity/work/llama-bin/llama-server   # b11010 CPU, @executable_path rpath (native-parity run.sh)
pgrep -f "port 8181" >/dev/null || { $LS -m $B/shared-models/bge-small-en-v1.5-q8_0.gguf --embedding -c 512 -b 512 -ub 512 -t 4 --port 8181 >$W/emb.log 2>&1 & }
pgrep -f "port 8183" >/dev/null || { $LS -m $B/shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf --jinja --chat-template-kwargs '{"enable_thinking":false}' -c 4096 -t 2 --port 8183 >$W/tok17.log 2>&1 & }
for p in 8181 8183; do for i in $(seq 90); do curl -sf localhost:$p/health >/dev/null && break; sleep 1; done; done
SD=$B/shared-data/packs
# App order (BoarServices.scanPacks): catalog sqlite-packs in catalog order, then local files by name (local-<name>).
KIT="wiki-vital5=$SD/wiki-vital5.sqlite,boar-crypto=$B/shared-data/crypto/boar-crypto.sqlite,boar-wikivoyage-en=$SD/boar-wikivoyage-en.sqlite,boar-factbook=$FB"
KIT="$KIT,boar-firstaid-en=$SD/wave1/boar-firstaid-en.sqlite,boar-medlineplus-en=$SD/wave1/boar-medlineplus-en.sqlite,qa-health-se=$SD/wave1/qa-health-se.sqlite"
KIT="$KIT,qa-outdoors-se=$SD/wave1/qa-outdoors-se.sqlite,qa-travel-se=$SD/wave1/qa-travel-se.sqlite,boar-simplewiki-en=$SD/candidates/boar-simplewiki-en-convfix/boar-simplewiki-en.sqlite"
KIT="$KIT,local-boar-visa-en=$SD/wave4/boar-visa-en.sqlite,local-qa-cooking-se=$SD/wave3/qa-cooking-se.sqlite,local-qa-money-se=$SD/wave3/qa-money-se.sqlite"
$W/main/build/install/native-main-harness/bin/native-main-harness --label $LABEL --questions $QF --out $OUT \
  --kb $W/main/kb-recommended.sqlite --corpus $SNAP/assets/corpus --corpora corpus-standard,corpus-full \
  --embed http://127.0.0.1:8181 --embed-cache $W/embed-cache.jsonl --tok http://127.0.0.1:8183 \
  --personalities $SNAP/android-native/app/src/main/assets/boar-data/personalities.json --lexicon $SNAP/assets/lexicon/pt-en.json \
  --packs "$KIT" --personas ${PERSONA:-succinct} --model-bytes 1107409472 --ctx 4096 --cutoffs 0.7 --labs on --facts $SNAP/android-native/app/src/labs/plugins/facts/res/raw/lab_facts_facts_v1.json --cities $SNAP/android-native/app/src/labs/plugins/distance/res/raw/lab_distance_world_cities_v1.json
