#!/usr/bin/env bash
# HEADPASS-X3 G3 timing pass (0 LLM / 0 judge): the reranker cost measured on a fixed 36-item subset of the 180 (items 1, 7, 13, 19 of each pack
# self-test) with the MacBook otherwise idle: waits (up to 60 min) until CPU idle >= 60 % and no Qwen3-4B llama-server or
# Foundry `forge` test runs (another project on the host), then scores x3a (one pack + kit) and m2 (all 9 + kit) live; load average and CPU idle are logged before
# and after each cell. Scores go to runs-x3/timing-scores.jsonl (throwaway; the gate uses runs-x3/scores.jsonl).
#   rnd/research/coordinator/arms/headpass-st/tools/run_x3_timing.sh > .../logs/run_x3_timing.log 2>&1
set -uo pipefail
B=$BOAR_WS; cd $B
A=$B/rnd/research/coordinator/arms/headpass-st; R=$A/tools/replay-x3.sh; O=$A/runs-x3
TREE=runner-local/be-0cfd4a77-cut7-headpass-x3; V=shared-data/packs/v3proto
KIT=shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite
PACKS="qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en"
pub() { case "$1" in boar-factbook|boar-simplewiki-en) echo shared-data/packs/wave2/$1.sqlite;; *) echo shared-data/packs/wave1/$1.sqlite;; esac; }
ALL=$KIT; for p in $PACKS; do ALL="$ALL,$(pub $p)"; done
PORT=8099; URL=http://127.0.0.1:$PORT; SRV=$B/spikes/llama-b11010-cpu/bin/llama-server; GGUF=$B/shared-models/bge-reranker-v2-m3-q4km.gguf
# macOS load average counts Spotlight I/O threads (load 12-18 at 70 % idle CPU), so the wait uses CPU idle % (top) instead.
load1() { echo "load $(sysctl -n vm.loadavg | awk '{print $2}') idle $(top -l 2 -n 0 | grep 'CPU usage' | tail -1 | awk '{print $7}')"; }
idle() { top -l 2 -n 0 | grep 'CPU usage' | tail -1 | awk '{print int($7)}'; }
for i in $(seq 1 120); do
  if pgrep -f "llama-server.*Qwen3-4B" >/dev/null || pgrep -x forge >/dev/null || [ "$(idle)" -lt 60 ]; then echo "[timing] waiting ($(load1))"; sleep 30; else break; fi
done
echo "[timing] start load $(load1)"
$SRV --rerank -ub 2048 -b 2048 -c 8192 --parallel 1 -t 4 --no-webui --host 127.0.0.1 --port $PORT -m $GGUF > $A/logs/rerank-server-timing.log 2>&1 &
SP=$!; for i in $(seq 1 120); do curl -s $URL/health | grep -q ok && break; sleep 1; done
rm -f $O/timing-scores.jsonl
for p in $PACKS; do
  ids=$(python3 -I -c "import json,sys; L=[json.loads(l)['id'] for l in open(sys.argv[1]) if l.strip()]; print(','.join(L[k] for k in range(0,len(L),6)))" rnd/research/packs/selftest/$p.jsonl)
  echo "[timing x3a $p] load before $(load1)"
  $R --gate search --k 6 --tree $TREE --modes x3a --packs $KIT,$(pub $p) --questions rnd/research/packs/selftest/$p.jsonl --ids $ids --gold none \
     --sidecars $V --rerank-url $URL --scores-out $O/timing-scores.jsonl --out $O/timing-x3a-$p.jsonl 2>&1 | grep -E 'FATAL|error'
  echo "[timing x3a $p] load after $(load1)"
done
ALLIDS=$(python3 -I -c "import json,sys; L=[json.loads(l)['id'] for l in open(sys.argv[1]) if l.strip()]; print(','.join(L[k] for k in range(len(L)) if (k % 20) % 6 == 0))" $O/st180.questions.jsonl)
echo "[timing m2] load before $(load1)"
$R --gate search --k 6 --tree $TREE --modes m2 --packs $ALL --questions $O/st180.questions.jsonl --ids $ALLIDS --gold none \
   --sidecars $V --rerank-url $URL --scores-out $O/timing-scores.jsonl --out $O/timing-m2-all9.jsonl 2>&1 | grep -E 'FATAL|error'
echo "[timing m2] load after $(load1)"
kill $SP 2>/dev/null; wait $SP 2>/dev/null
echo TIMING-DONE $(date +%H:%M:%S)
