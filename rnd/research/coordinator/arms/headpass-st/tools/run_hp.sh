#!/usr/bin/env bash
# HEADPASS-ST step 0 replays (0 LLM / 0 judge / 0 paid). REF = tk2off tree (pristine cut-7 copy), modes off;
# HP = kiln-local/be-0cfd4a77-cut7-headpass (cut 7 + headpass.vs-cut7.patch), modes off,x1,off (pass 3 = repeat identity
# + warm timing). Published packs. Sets: v0.1 public kit-only (v01-kit), v0.1 public + boar-simplewiki-en (v01-sw),
# 9 x 20 self-tests (kit + the item's pack). No --pool (keepMs then excludes any extra retrieve). 4 runs in parallel.
set -uo pipefail
B=<workspace>; cd $B
A=$B/rnd/research/coordinator/arms/headpass-st; R=$A/tools/replay-hp.sh; O=$A/runs
pub() { case "$1" in boar-crypto) echo shared-data/crypto/boar-crypto.sqlite;; boar-wikivoyage-en) echo shared-data/packs/boar-wikivoyage-en.sqlite;;
  boar-factbook|boar-simplewiki-en) echo shared-data/packs/wave2/$1.sqlite;; *) echo shared-data/packs/wave1/$1.sqlite;; esac; }
job() { local cell=$1 set=$2 p=$3; local T M PK
  if [ $cell = ref ]; then T=kiln-local/be-0cfd4a77-cut7-tk2off; M=off; else T=kiln-local/be-0cfd4a77-cut7-headpass; M=off,x1,off; fi
  PK=$(pub boar-crypto),$(pub boar-wikivoyage-en); [ -n "$p" ] && PK=$PK,$(pub $p)
  local out=$O/$set.$cell.jsonl; [ -s $out ] && return
  if [ ${set%%-*} = v01 ]; then Q="--questions boar-eval/bench/v0.1/questions.public.jsonl --gold boar-eval/bench/v0.1/gold/sources.json"
  else Q="--questions rnd/research/packs/selftest/$p.jsonl --gold none"; fi
  local free; free=$(df -g <home> | awk 'NR==2{print $4}'); if [ "$free" -lt 8 ]; then echo "[$set $cell] SKIP disk ${free} GiB"; return; fi
  $R --gate search --k 6 --tree $T --modes $M --packs $PK $Q --out $out 2>&1 | grep -E '^\{|app dir|FATAL|error' | sed "s/^/[$set $cell] /"; }
N=0
for cell in ref hp; do
  job $cell v01-kit "" & N=$((N+1)); [ $((N % 4)) -eq 0 ] && wait
  job $cell v01-sw boar-simplewiki-en & N=$((N+1)); [ $((N % 4)) -eq 0 ] && wait
  for p in qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en; do
    job $cell st-$p $p & N=$((N+1)); [ $((N % 4)) -eq 0 ] && wait
  done
done; wait
echo RUN-HP-DONE
