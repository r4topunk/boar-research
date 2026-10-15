#!/usr/bin/env bash
# HEADPASS-X3 step 0, fix pass (0 LLM / 0 judge / 0 paid). Two implementation gaps found in the first pass (logs/run_x3.log):
#  1. packRerankCandidates anchored the union on a raw user-pack passage; with none in raw (29 of the 180: the kit fills the
#     raw list) it returned null (headpass:rerank:nocand). The criterion's union is "the pack's BM25 top-80 ∪ dense top-12 ∪
#     the top article's chunks": the fixed tree falls back to the installed user pack(s) (BM25 top-80 + dense, no top article).
#  2. fetch's 300 s headers timeout cancelled 2 long scoring requests under CPU contention (Foundry forge tests at load 40-140):
#     replay-x3.ts now posts with node:http and no client timeout.
# This pass re-scores the 180 (x3a) and v0.1 + simplewiki (x3a, m2) with the cache (pairs already in runs-x3/scores.jsonl are
# not sent again; new pairs appended), then re-runs the lookup cells x3 and v01 (old outputs moved to runs-x3/pass1/).
set -uo pipefail
B=$BOAR_WS; cd $B
A=$B/rnd/research/coordinator/arms/headpass-st; R=$A/tools/replay-x3.sh; O=$A/runs-x3
TREE=runner-local/be-0cfd4a77-cut7-headpass-x3; V=shared-data/packs/v3proto
KIT=shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite
PACKS="qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en"
pub() { case "$1" in boar-factbook|boar-simplewiki-en) echo shared-data/packs/wave2/$1.sqlite;; *) echo shared-data/packs/wave1/$1.sqlite;; esac; }
V01Q=boar-eval/bench/v0.1/questions.public.jsonl; V01G=boar-eval/bench/v0.1/gold/sources.json
PORT=8099; URL=http://127.0.0.1:$PORT; SRV=$B/spikes/llama-b11010-cpu/bin/llama-server; GGUF=$B/shared-models/bge-reranker-v2-m3-q4km.gguf
mkdir -p $O/pass1
for f in $O/st-*.x3.jsonl $O/v01-kit.x3.jsonl $O/v01-sw.x3.jsonl; do [ -e "$f" ] && mv "$f" $O/pass1/; done
curl -s $URL/health | grep -q ok && { echo "FATAL port $PORT busy"; exit 1; }
$SRV --rerank -ub 2048 -b 2048 -c 8192 --parallel 1 -t 4 --no-webui --host 127.0.0.1 --port $PORT -m $GGUF > $A/logs/rerank-server-fix.log 2>&1 &
SP=$!; for i in $(seq 1 120); do curl -s $URL/health | grep -q ok && break; sleep 1; done; echo "server up $SP"
CACHE=(--rerank-url $URL --scores $O/scores.jsonl --scores-out $O/scores.jsonl)
for p in $PACKS; do
  out=$O/score2-st-$p.jsonl; [ -s $out ] && continue
  $R --gate search --k 6 --tree $TREE --modes x3a --packs $KIT,$(pub $p) --questions rnd/research/packs/selftest/$p.jsonl --gold none \
     --sidecars $V "${CACHE[@]}" --cands-out $O/cands2-st-$p.jsonl --out $out 2>&1 | grep -E '^\{|FATAL|error' | cut -c1-400 | sed "s/^/[score2 $p] /"
done
[ -s $O/score2-v01-sw.jsonl ] || $R --gate search --k 6 --tree $TREE --modes x3a,m2 --packs $KIT,$(pub boar-simplewiki-en) --questions $V01Q --gold $V01G \
   --sidecars $V "${CACHE[@]}" --cands-out $O/cands2-v01-sw.jsonl --out $O/score2-v01-sw.jsonl 2>&1 | grep -E '^\{|FATAL|error' | cut -c1-400 | sed "s/^/[score2 v01-sw] /"
kill $SP 2>/dev/null; wait $SP 2>/dev/null; echo "server down"
cat $O/cands2-st-*.jsonl $O/cands2-v01-sw.jsonl $O/cands-all9-st180.jsonl $O/cands-all9-v01.jsonl > $O/cands.jsonl 2>/dev/null
rm -f $O/cands-st-*.jsonl $O/cands-v01-sw.jsonl
$A/tools/run_x3.sh x3 v01
echo RUN-X3-FIX-DONE $(date +%H:%M:%S)
