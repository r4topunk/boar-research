#!/bin/bash
# score the five replays (K3, K3CM, K3W, KSE, KFULL): lexical funnel + cm oracle funnel
cd <workspace>/rnd/research/coordinator/arms/coverage-map
ids(){ tr ',' '\n' < replay/kit.$1.txt | xargs -n1 basename | sed 's/.sqlite$//' | paste -sd, -; }
A=(); for k in K3 K3CM K3W KSE KFULL; do A+=("$k=replay/main.$k.jsonl=$(ids $k)"); done
python3 -I tools/score_kfull.py aggregates/coverage-pool.json aggregates/kfull-funnel.json "${A[@]}"
python3 -I tools/cm_stage.py aggregates/cm-stage.json "${A[@]}"
