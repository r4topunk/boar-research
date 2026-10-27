#!/usr/bin/env bash
# BATCHRET parity + SQL-count replays (0 LLM, 0 judge, 0 paid; MacBook). Usage: run_parity.sh <tag> <tree> [pass]
# Sets (public dev only; never blind/, never bench/v0.4):
#   v01      bench/v0.1/questions.public.jsonl (60) on the claim kit (crypto + wikivoyage)
#   st180    the 9 pack self-tests x 20 (bench/selftest/<pack>), kit + that pack (as HEADPASS-X2 identity)
#   cw150    bench/slices/chainwhen-v1/questions.jsonl (150), each item on kit + its selftest.pack
# Output: runs/<tag>[.<pass>]/<set>[-<pack>].jsonl
set -euo pipefail
TAG=$1; TREE=$2; PASS=${3:-1}
B=<workspace>; A=$B/rnd/research/coordinator/arms/batchret; R=$A/tools/parity-replay.sh
O=$A/runs/$TAG.p$PASS; mkdir -p $O
KIT=$B/shared-data/crypto/boar-crypto.sqlite,$B/shared-data/packs/boar-wikivoyage-en.sqlite
PACKS="qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en"
pub() { case "$1" in boar-factbook|boar-simplewiki-en) echo $B/shared-data/packs/wave2/$1.sqlite;; *) echo $B/shared-data/packs/wave1/$1.sqlite;; esac; }
run() { local set=$1 q=$2 packs=$3 out=$4
  $R --tree $TREE --gate search --gold none --set $set --packs $packs --questions $q --out $out 2>&1 | grep -E '^\{|FATAL' | sed "s/^/[$TAG $set] /"
  [ "$(grep -c . $out)" -eq "$(grep -c . $q)" ] || { echo "[$TAG $set] LINE COUNT MISMATCH"; exit 1; }
}
run v01 $B/boar-eval/bench/v0.1/questions.public.jsonl $KIT $O/v01.jsonl
for p in $PACKS; do run st180 $B/boar-eval/bench/selftest/$p/questions.jsonl $KIT,$(pub $p) $O/st180-$p.jsonl; done
CW=$A/runs/cw150-split; mkdir -p $CW
python3 - "$B/boar-eval/bench/slices/chainwhen-v1/questions.jsonl" "$CW" <<'PY'
import json, sys
by = {}
for l in open(sys.argv[1]):
    if l.strip(): by.setdefault(json.loads(l)["selftest"]["pack"], []).append(l if l.endswith("\n") else l + "\n")
for p, ls in by.items(): open(f"{sys.argv[2]}/{p}.jsonl", "w").writelines(ls)
PY
for p in $PACKS; do [ -s $CW/$p.jsonl ] && run cw150 $CW/$p.jsonl $KIT,$(pub $p) $O/cw150-$p.jsonl; done
echo "[$TAG] done $O"
