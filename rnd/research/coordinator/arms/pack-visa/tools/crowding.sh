#!/usr/bin/env bash
# PACK-VISA CROWDING probe = arms/packs/tools/crowding.sh protocol (0 LLM, 0 judge, MacBook): deep-tier retrieval replay (k 6, pool 20,
# gate rules, tree wt/packs) of the claim kit (crypto + wikivoyage) alone and + boar-visa-en as a peer, on v0.1 public (60) and the
# public rivalset (72; 20 travel). v0.2 is not replayed (its question file is under blind/). Then aggregates/crowding-visa.json.
set -euo pipefail
B=<workspace>; H=$B/rnd/research/coordinator/arms/pack-visa; cd "$B"
export BOAR_REPLAY_CACHE="$B/rnd/research/coordinator/arms/deepcovfb/cache"
R=$B/rnd/research/coordinator/arms/packs/tools/replay-crowd.sh
KIT=shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite
O=$H/replay; mkdir -p "$O"
for lab in base boar-visa-en; do
  P=$KIT; [ $lab = base ] || P="$KIT,shared-data/packs/wave4/$lab.sqlite"
  C=(--deep --gate rules --k 6 --pool 20 --tree wt/packs --packs "$P")
  "$R" "${C[@]}" --questions boar-eval/bench/v0.1/questions.public.jsonl --gold boar-eval/bench/v0.1/gold/sources.json \
    --out "$O/v01-$lab.jsonl" 2> >(grep -E '^\{|app dir' | sed "s/^/[v01 $lab] /" >&2)
  "$R" "${C[@]}" --questions boar-eval/bench/rivalset/questions.jsonl --gold /nonexistent-no-gold.json \
    --out "$O/rival-$lab.jsonl" 2> >(grep -E '^\{|app dir' | sed "s/^/[rival $lab] /" >&2)
done
python3 -I "$H/tools/crowding_agg.py"
