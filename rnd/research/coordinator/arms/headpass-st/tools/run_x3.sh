#!/usr/bin/env bash
# HEADPASS-X3 step 0 replays (criterion HEADPASS-X3-criterion.md sha 275fe748...; 0 LLM / 0 judge / 0 paid; MacBook).
# Tree kiln-local/be-0cfd4a77-cut7-headpass-x3 = the X2b tree + packRerank (src/rag/rerank.ts; patch headpass-x3.vs-cut7.patch).
# Resumable: each cell writes <out>.tmp and renames it on success; a finished <out> is skipped.
#
#   nohup rnd/research/coordinator/arms/headpass-st/tools/run_x3.sh [phase ...] > .../headpass-st/logs/run_x3.log 2>&1 &
#
# Phases (default: score x3 v01 m2):
#   score  reranker server UP (llama-server --rerank -ub 2048, CPU build, port 8099, -t 4; waits until no Qwen3-4B
#          llama-server runs, so the timing is uncontended), live scoring; every pair -> runs-x3/scores.jsonl
#          ({qsha, chunkId, score}, no text), candidate ids -> runs-x3/cands.jsonl; server DOWN at the end.
#            st-<pack>  x3a on the 180 (one pack + kit, sidecar copies)      -> runs-x3/score-st-<pack>.jsonl (rr ms per item)
#            v01-sw     x3a,m2 on v0.1 public + simplewiki                   -> runs-x3/score-v01-sw.jsonl
#            all9-st180 m2 on the 180 with all 9 + kit                       -> runs-x3/score-all9-st180.jsonl
#            all9-v01   m2 on v0.1 public with all 9 + kit                   -> runs-x3/score-all9-v01.jsonl
#   x3     off,x1,x2b,x3a,x3b,off on the 180 (scores looked up)             -> runs-x3/st-<pack>.x3.jsonl
#   v01    v0.1 kit-only off,x3a,x3b,m2,off (no sidecars) / v0.1 + simplewiki same modes -> runs-x3/v01-{kit,sw}.x3.jsonl
#   m2     all 9 + kit: the 180 off,m2,off / v0.1 public off,m2,off          -> runs-x3/m2-all9-{st180,v01}.jsonl
#   v02    v0.2 kit-only off,x3a,x3b,m2,off, SCRIPT-ONLY (output under blind/bench-v02/runs-packs/, summary line only;
#          kit-only never reaches a scorer). Opt-in; EXPOSURES row + QUEUE entry when it runs.
set -uo pipefail
B=<workspace>; cd $B
A=$B/rnd/research/coordinator/arms/headpass-st; R=$A/tools/replay-x3.sh; O=$A/runs-x3; mkdir -p $O
TREE=kiln-local/be-0cfd4a77-cut7-headpass-x3
V=shared-data/packs/v3proto
KIT=shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite
PACKS="qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en"
pub() { case "$1" in boar-factbook|boar-simplewiki-en) echo shared-data/packs/wave2/$1.sqlite;; *) echo shared-data/packs/wave1/$1.sqlite;; esac; }
ALL=$KIT; for p in $PACKS; do ALL="$ALL,$(pub $p)"; done
ST180=$O/st180.questions.jsonl
[ -s $ST180 ] || for p in $PACKS; do cat rnd/research/packs/selftest/$p.jsonl; done > $ST180
V01Q=boar-eval/bench/v0.1/questions.public.jsonl; V01G=boar-eval/bench/v0.1/gold/sources.json
C=(--gate search --k 6 --tree $TREE)
PORT=8099; URL=http://127.0.0.1:$PORT; SRV=$B/spikes/llama-b11010-cpu/bin/llama-server; GGUF=$B/shared-models/bge-reranker-v2-m3-q4km.gguf
disk_ok() { local free; free=$(df -g <home> | awk 'NR==2{print $4}'); [ "$free" -ge 8 ] || { echo "[$1] SKIP disk ${free} GiB < 8"; return 1; }; }
cell() { # tag out modes packs questions gold [extra replay args...]
  local tag=$1 out=$2 modes=$3 packs=$4 q=$5 g=$6; shift 6
  [ -s "$out" ] && { echo "[$tag] done (skip)"; return 0; }
  disk_ok "$tag" || return 0
  local t0=$SECONDS
  $R "${C[@]}" --modes "$modes" --packs "$packs" --questions "$q" --gold "$g" --out "$out.tmp" "$@" 2>&1 \
    | grep -E '^\{|app dir|FATAL|error' | sed "s/^/[$tag] /"
  local want; want=$(( $(grep -c . "$q") * $(echo "$modes" | tr ',' '\n' | grep -c .) ))
  if [ -s "$out.tmp" ] && [ "$(grep -c . "$out.tmp")" -eq "$want" ]; then mv "$out.tmp" "$out"; echo "[$tag] ok $want lines $((SECONDS - t0)) s"
  else echo "[$tag] INCOMPLETE ($(grep -c . "$out.tmp" 2>/dev/null || echo 0)/$want lines); kept $out.tmp"; fi
}
st_q() { echo rnd/research/packs/selftest/$1.jsonl; }
server_up() {
  while pgrep -f "llama-server.*Qwen3-4B" >/dev/null; do echo "[score] waiting: a Qwen3-4B llama-server is running"; sleep 30; done
  curl -s $URL/health | grep -q ok && { echo "[score] FATAL port $PORT busy"; return 1; }
  [ "$(shasum -a 256 $GGUF | cut -c1-64)" = e186a244ed455b4ab66ec64339ce7427a6ae13f5c0b5e544de96e50f0f8b3673 ] || { echo "[score] FATAL reranker sha"; return 1; }
  $SRV --rerank -ub 2048 -b 2048 -c 8192 --parallel 1 -t 4 --no-webui --host 127.0.0.1 --port $PORT -m $GGUF > $A/logs/rerank-server.log 2>&1 &
  SRVPID=$!
  for i in $(seq 1 120); do curl -s $URL/health | grep -q ok && { echo "[score] server up (pid $SRVPID)"; return 0; }; sleep 1; done
  echo "[score] FATAL server not healthy"; return 1
}
server_down() { [ -n "${SRVPID:-}" ] && kill $SRVPID 2>/dev/null; wait $SRVPID 2>/dev/null; echo "[score] server down"; }
LIVE=(--rerank-url $URL --scores-out $O/scores.jsonl)
phase_score() {
  server_up || return 1
  for p in $PACKS; do cell "score st $p" $O/score-st-$p.jsonl x3a $KIT,$(pub $p) $(st_q $p) none --sidecars $V "${LIVE[@]}" --cands-out $O/cands-st-$p.jsonl; done
  cell "score v01-sw" $O/score-v01-sw.jsonl x3a,m2 $KIT,$(pub boar-simplewiki-en) $V01Q $V01G --sidecars $V "${LIVE[@]}" --cands-out $O/cands-v01-sw.jsonl
  cell "score all9-st180" $O/score-all9-st180.jsonl m2 $ALL $ST180 none --sidecars $V "${LIVE[@]}" --cands-out $O/cands-all9-st180.jsonl
  cell "score all9-v01" $O/score-all9-v01.jsonl m2 $ALL $V01Q $V01G --sidecars $V "${LIVE[@]}" --cands-out $O/cands-all9-v01.jsonl
  server_down
  cat $O/cands-st-*.jsonl $O/cands-v01-sw.jsonl $O/cands-all9-st180.jsonl $O/cands-all9-v01.jsonl > $O/cands.jsonl 2>/dev/null
  echo "[score] scores $(grep -c . $O/scores.jsonl) pairs; cands $(grep -c . $O/cands.jsonl) item lines"
}
SC=(--scores $O/scores.jsonl)
X3=off,x1,x2b,x3a,x3b,off
phase_x3() { for p in $PACKS; do cell "x3 $p" $O/st-$p.x3.jsonl $X3 $KIT,$(pub $p) $(st_q $p) none --sidecars $V "${SC[@]}"; done; }
phase_v01() {
  cell "v01-kit" $O/v01-kit.x3.jsonl off,x3a,x3b,m2,off $KIT $V01Q $V01G --no-sidecars "${SC[@]}"
  cell "v01-sw" $O/v01-sw.x3.jsonl off,x3a,x3b,m2,off $KIT,$(pub boar-simplewiki-en) $V01Q $V01G --sidecars $V "${SC[@]}"
}
phase_m2() {
  cell "m2 all9-st180" $O/m2-all9-st180.jsonl off,m2,off $ALL $ST180 none --sidecars $V "${SC[@]}"
  cell "m2 all9-v01" $O/m2-all9-v01.jsonl off,m2,off $ALL $V01Q $V01G --sidecars $V "${SC[@]}"
}
phase_v02() { # script-only: never print item content; the summary line only
  local O2=$B/blind/bench-v02/runs-packs out=$B/blind/bench-v02/runs-packs/headpass-x3-v02-kit.jsonl
  [ -s $out ] && { echo "[v02-kit] done (skip)"; return 0; }
  disk_ok v02-kit || return 0
  mkdir -p $O2
  $R "${C[@]}" --modes off,x3a,x3b,m2,off --packs $KIT --questions blind/bench-v02/live/v0.2/questions.v02-new.jsonl \
     --gold boar-eval/bench/v0.2/gold/sources.json --no-sidecars "${SC[@]}" --out $out.tmp 2>&1 | grep -E '^\{"n"' | sed 's/^/[v02-kit] /'
  [ -s $out.tmp ] && mv $out.tmp $out
  python3 -I $A/tools/gate_x3.py --v02-counts $out 2>&1 | sed 's/^/[v02-kit] /'
}
for ph in ${*:-score x3 v01 m2}; do echo "== phase $ph $(date +%H:%M:%S)"; phase_$ph; done
echo RUN-X3-DONE $(date +%H:%M:%S)
