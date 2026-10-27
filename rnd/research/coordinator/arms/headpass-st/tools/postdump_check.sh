#!/usr/bin/env bash
# Re-check after adding headpass-dump.eval.patch (env-gated, absent in replays): modes off,x1 on all 11 sets must equal the step-0 hp outputs.
set -uo pipefail
B=<workspace>; cd $B; A=rnd/research/coordinator/arms/headpass-st; mkdir -p $A/runs/postdump
pub() { case "$1" in boar-factbook|boar-simplewiki-en) echo shared-data/packs/wave2/$1.sqlite;; *) echo shared-data/packs/wave1/$1.sqlite;; esac; }
KIT=shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite; N=0
for set in v01-kit v01-sw st-qa-travel-se st-qa-ethereum-se st-qa-bitcoin-se st-qa-health-se st-qa-outdoors-se st-boar-firstaid-en st-boar-medlineplus-en st-boar-factbook st-boar-simplewiki-en; do
  p=${set#st-}; V="--questions boar-eval/bench/v0.1/questions.public.jsonl --gold boar-eval/bench/v0.1/gold/sources.json"
  case $set in v01-kit) PK=$KIT; Q=$V;; v01-sw) PK=$KIT,$(pub boar-simplewiki-en); Q=$V;; *) PK=$KIT,$(pub $p); Q="--questions rnd/research/packs/selftest/$p.jsonl --gold none";; esac
  $A/tools/replay-hp.sh --gate search --k 6 --tree kiln-local/be-0cfd4a77-cut7-headpass --modes off,x1 --packs $PK $Q --out $A/runs/postdump/$set.hp.jsonl 2>&1 | grep -E "FATAL|error" &
  N=$((N+1)); [ $((N % 4)) -eq 0 ] && wait
done; wait
python3 -I - <<'PY'
import json, glob, os
A = "<workspace>/rnd/research/coordinator/arms/headpass-st/runs"
key = lambda l: json.dumps([[[x.get(k) for k in ("chunkId","title","section","source","similarity","via")] for x in l["raw"]], [x.get("chunkId") for x in l["kept"]], l.get("promptSha"), l["task"], l["query"], l["k"], l["mode"], l["id"]])
tot = same = 0
for f in sorted(glob.glob(f"{A}/postdump/*.hp.jsonl")):
    new = [key(json.loads(l)) for l in open(f)]; old = [key(json.loads(l)) for l in open(f"{A}/{os.path.basename(f)}")][:len(new)]
    s = sum(a == b for a, b in zip(new, old)); tot += len(new); same += s
print("postdump identical", same, "/", tot)
PY
