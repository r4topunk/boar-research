#!/bin/bash
# NOREPACK97 mini arm (runs ON the mini). Needs <runner>/kiln/nr/{mini_gen.sh,req97.jsonl}. Usage: norepack97_mini.sh <arm name> <extra args>
set -u
N=$1; X=${2:-}; K=<runner>/kiln; J=$K/nr/$N
rm -rf $J; mkdir -p $J; cp -c -R $K/be-0cfd4a77-cut7-litepacks $J/tree; cp $K/nr/req97.jsonl $J/requests.jsonl
printf 'BOAR_SERVER_EXTRA_ARGS="--reasoning off %s"\n' "$X" > $J/env
bash $K/nr/mini_gen.sh $J; echo "$N $(tail -1 $J/STATUS) rows=$(wc -l < $J/traces.jsonl)"
