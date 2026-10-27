#!/usr/bin/env bash
# VITALPACK step 0: deep-tier retrieval replays, base kit vs base + wiki-vital5, on v0.1 (public) and the two blind sets (script-only; outputs under blind/). Run from the repo root.
set -euo pipefail
A=rnd/research/coordinator/arms/vitalpack; D=rnd/research/coordinator/arms/deepcovfb
export BOAR_REPLAY_CACHE=$PWD/$D/cache
BASEP=shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite
VP=$BASEP,shared-data/packs/wiki-vital5.sqlite
C=(--deep --gate rules --tree wt/cut7 --k 6 --pool 20)
$D/tools/replay-deep.sh "${C[@]}" --questions boar-eval/bench/v0.1/questions.public.jsonl --packs $VP --out $A/replay-vital-v01.jsonl 2> $A/logs/replay-vital-v01.log; tail -1 $A/logs/replay-vital-v01.log
for S in V-para:items.jsonl:runs-cut6/judged.ids:vpara bench-v02:live/v0.2/questions.v02-new.jsonl:runs-deepvpara/judged.ids:v02; do
  IFS=: read set q idsf lab <<< "$S"; O=blind/$set/runs-vitalpack; mkdir -p $O; IDS=$(paste -sd, blind/$set/$idsf)
  $D/tools/replay-deep.sh "${C[@]}" --questions blind/$set/$q --ids "$IDS" --packs $BASEP --out $O/replay-base.jsonl 2> $A/logs/replay-base-$lab.log; tail -1 $A/logs/replay-base-$lab.log
  $D/tools/replay-deep.sh "${C[@]}" --questions blind/$set/$q --ids "$IDS" --packs $VP --out $O/replay-vital.jsonl 2> $A/logs/replay-vital-$lab.log; tail -1 $A/logs/replay-vital-$lab.log
done
