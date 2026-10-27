#!/usr/bin/env bash
# QMERGE step 0 replays (0 LLM / 0 judge): kiln-local/be-cut7-qmerge (pr1 8ac9eb7a + qmerge.patch) + PUBLISHED packs (claim kit + item pack),
# modes off,qm,off; detector :8094 (never restarted); v0.1 60 on the claim kit with v01-qmap.json.
set -uo pipefail
B=<workspace>; cd $B
A=$B/rnd/research/coordinator/arms/qmerge; R=$A/tools/replay-qm.sh; O=$A/runs; T=kiln-local/be-cut7-qmerge
[ "$(cat $T/ARM)" = pr1+qmerge ] || { echo "FAIL ARM"; exit 1; }
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down"; exit 1; }
$B/rnd/research/coordinator/arms/headpass-st/tools/busy.sh && { echo "FAIL busy"; exit 1; }
FREE=$(df -g <home> | awk 'NR==2{print $4}'); [ "$FREE" -lt 5 ] && { echo "FAIL disk $FREE GiB"; exit 1; }
pub() { case "$1" in boar-crypto) echo shared-data/crypto/boar-crypto.sqlite;; boar-wikivoyage-en) echo shared-data/packs/boar-wikivoyage-en.sqlite;;
  boar-factbook|boar-simplewiki-en) echo shared-data/packs/wave2/$1.sqlite;; *) echo shared-data/packs/wave1/$1.sqlite;; esac; }
job() { local p=$1; local out=$O/st-$p.qm.jsonl; [ -s $out ] && return
  $R --gate search --k 6 --tree $T --modes off,qm,off --pool 8 --qmap $B/rnd/research/coordinator/arms/qwrite/runs/qmap.json --packs $(pub boar-crypto),$(pub boar-wikivoyage-en),$(pub $p) \
     --questions rnd/research/packs/selftest/$p.jsonl --gold none --out $out 2>&1 | grep -E '^\{|FATAL|rror' | sed "s/^/[$p] /"; }
# first job alone (fresh cache key: seed corpus indexing), then 3 at a time
job qa-travel-se
N=0
for p in qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en; do
  job $p & N=$((N+1)); [ $((N % 3)) -eq 0 ] && wait
done; wait
[ -s $O/v01.qm.jsonl ] || $R --gate search --k 5 --tree $T --modes off,qm,off --pool 8 --qmap $O/v01-qmap.json \
  --questions boar-eval/bench/v0.1/questions.public.jsonl --out $O/v01.qm.jsonl 2>&1 | grep -E '^\{|FATAL|rror' | sed "s/^/[v01] /"
echo RUN-QM-DONE
