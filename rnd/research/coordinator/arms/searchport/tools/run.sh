#!/bin/bash
# SEARCHPORT delivery run on the MacBook (0 LLM generation): builds the harness against an engine source tree with a hook, runs MAIN 97,
# ST 180 (3 kit groups), probes 65, writes replays/<name>/{main,st.on-k13,st.on-k13+qa-bitcoin-se,st.on-k13+qa-ethereum-se,probes}.jsonl.
# usage: run.sh <name> <b0|port> <engine java src dir> <on|off> [sets]
# Kit = the BoarLite APK bundle in catalog order (stage-bundle.sh at 078a2627) with factbook v1 c5854353 (coordinator 10-24 18:2x).
set -euo pipefail
B=<workspace>; A=$B/rnd/research/coordinator/arms/searchport; W=$A/work
NAME=$1; HOOK=$2; ESRC=$3; PORT=$4; SETS=${5:-main st probes}
export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
GRADLE=$(ls -d $HOME/.gradle/wrapper/dists/gradle-8.14.3-bin/*/gradle-8.14.3)/bin/gradle
LS=$B/rnd/research/coordinator/arms/native-parity/work/llama-bin/llama-server
pgrep -f "port 8181" >/dev/null || { $LS -m $B/shared-models/bge-small-en-v1.5-q8_0.gguf --embedding -c 512 -b 512 -ub 512 -t 4 --port 8181 >$W/emb.log 2>&1 & }
for i in $(seq 90); do curl -sf localhost:8181/health >/dev/null && break; sleep 1; done
BD=$W/build-$HOOK; ES=$W/engine-$HOOK
chmod -R u+w $ES 2>/dev/null || true; rm -rf $ES && cp -R $ESRC $ES && chmod -R u+w $ES && bash $B/rnd/research/coordinator/arms/native-rc/tools/cutoff.patch.sh $ES >/dev/null
(cd $A/tools/harness && ENGINE_SRC=$ES HOOK_SRC=$A/tools/hook-$HOOK BUILD_DIR=$BD $GRADLE -q --no-daemon installDist)
SD=$B/shared-data/packs
KIT="wiki-vital5=$SD/wiki-vital5.sqlite,boar-crypto=$B/shared-data/crypto/boar-crypto.sqlite,boar-wikivoyage-en=$SD/boar-wikivoyage-en.sqlite,boar-factbook=$SD/wave2/boar-factbook.sqlite"
KIT="$KIT,boar-firstaid-en=$SD/v3proto/boar-firstaid-en.sqlite,boar-medlineplus-en=$SD/v3proto/boar-medlineplus-en.sqlite,qa-health-se=$SD/v3proto/qa-health-se.sqlite"
KIT="$KIT,qa-outdoors-se=$SD/v3proto/qa-outdoors-se.sqlite,qa-travel-se=$SD/v3proto/qa-travel-se.sqlite,boar-simplewiki-en=$SD/v3proto/boar-simplewiki-en.sqlite"
KIT="$KIT,qa-cooking-se=$SD/wave3/qa-cooking-se.sqlite,qa-money-se=$SD/wave3/qa-money-se.sqlite,boar-visa-en=$SD/wave4/boar-visa-en.sqlite"
O=$A/replays/$NAME; mkdir -p $O
h() { # <questions> <out> <kit>
  local t0=$(date +%s)
  $BD/install/native-parity-harness/bin/native-parity-harness --label $NAME --questions $1 --out $2 \
    --kb $W/kb.sqlite --corpus /dev/null --embed http://127.0.0.1:8181 --embed-cache $W/embed-cache.jsonl --tok ${TOK:-none} \
    --personalities $W/snap-assets/personalities.json --lexicon $W/snap-assets/pt-en.json \
    --packs "$3" --personas succinct --model-bytes 1107409472 --ctx 4096 --cutoffs 0.7 --port $PORT 2> $2.err
  echo "$NAME $(basename $2) $(( $(date +%s) - t0 ))s rows $(wc -l < $2)" | tee -a $O/runs.log; }
for S in $SETS; do case $S in
  main) h $W/q-main.jsonl $O/main.jsonl "$KIT";;
  st) h $W/q-st-k13.jsonl $O/st.on-k13.jsonl "$KIT"
      h $W/q-st-btc.jsonl $O/st.on-k13+qa-bitcoin-se.jsonl "$KIT,local-qa-bitcoin-se=$SD/v3proto/qa-bitcoin-se.sqlite"
      h $W/q-st-eth.jsonl $O/st.on-k13+qa-ethereum-se.jsonl "$KIT,local-qa-ethereum-se=$SD/v3proto/qa-ethereum-se.sqlite";;
  probes) h $W/q-probes-hist.jsonl $O/probes.jsonl "$KIT";;
  r1) h $W/q-r1on.jsonl $O/r1.jsonl "$KIT";;
esac; done
