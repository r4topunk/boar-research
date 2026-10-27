#!/bin/bash
# W63 mini arms (run ON the mini or via ssh). Usage: norepack_mini.sh <arm name> <extra args>. Needs <runner>/kiln/nr/req.jsonl (the 10 requests).
# Uses the 2-slot guard script (mini_gen.sh.used = lp-screens/tools/mini_gen.sh) with a job dir: tree = APFS clone of be-0cfd4a77-cut7-litepacks, env file
# overriding BOAR_SERVER_EXTRA_ARGS (mini_gen.sh sources it after its own default).
set -u
N=$1; X=${2:-}; K=<runner>/kiln; J=$K/nr/$N
rm -rf $J; mkdir -p $J; cp -c -R $K/be-0cfd4a77-cut7-litepacks $J/tree; cp $K/nr/req.jsonl $J/requests.jsonl
printf 'BOAR_SERVER_EXTRA_ARGS="--reasoning off %s"\n' "$X" > $J/env
bash $K/nr/mini_gen.sh $J; echo "$N $(tail -1 $J/STATUS) rows=$(wc -l < $J/traces.jsonl)"
