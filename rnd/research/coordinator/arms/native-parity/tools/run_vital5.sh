#!/bin/bash
# Extra configs after run.sh: Standard KB + wiki-vital5 on MAIN 97 (sweep) and the X6 replica on X6's own 73 questions.
set -euo pipefail
B=<workspace>; ARM=$B/rnd/research/coordinator/arms/native-parity; W=$ARM/work; SNAP=$B/wt/native-qa/android-native
BIN=$W/build/install/native-parity-harness/bin/native-parity-harness; export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
V5=$W/dl/wiki-vital5.sqlite
[ -f $V5 ] || { mkdir -p $W/dl; curl -sSL -o $V5 https://github.com/UPSTREAM_REPO/boar-app/releases/download/knowledge-pack-v1/wiki-vital5.sqlite; }
echo "d3b87d562baba3489f6878bf99783f50d504db94c347029771e53f6d1aecc666  $V5" | shasum -a 256 -c -
python3 -I -c "
import json,sys
r=json.load(open('$B/boar-eval/runs/device-poco-x6pro/native-x6-v01/raw/request.json'))
with open('$W/questions-x6.jsonl','w') as o:
  for q in r['questions']: o.write(json.dumps({'id':q['id'],'question':q['query']})+'\n')"
COMMON="--kb $W/kb-standard.sqlite --corpus $B/wt/native-qa/assets/corpus --embed http://127.0.0.1:8181 --embed-cache $W/embed-cache.jsonl --tok http://127.0.0.1:8182 --personalities $SNAP/app/src/main/assets/boar-data/personalities.json --lexicon $B/wt/native-qa/assets/lexicon/pt-en.json"
$BIN $COMMON --questions $W/questions-main97.jsonl --label kbvital5 --packs $V5 --cutoffs 0.7,0.5,0.3 --model-bytes 2497281120 --out $W/out/kbvital5.jsonl
$BIN $COMMON --questions $W/questions-x6.jsonl --label x6replica --packs $V5 --cutoffs 0.7 --personas succinct --model-bytes 2497281120 --out $W/out/x6replica.jsonl
