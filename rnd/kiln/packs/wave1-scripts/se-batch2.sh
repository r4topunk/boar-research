#!/bin/bash
S=<runner>/kiln/packs/scripts
for pair in "bitcoin qa-bitcoin-se Bitcoin Stack Exchange Q&A" "ethereum qa-ethereum-se Ethereum Stack Exchange Q&A" "travel qa-travel-se Travel Stack Exchange Q&A"; do
  set -- $pair; site=$1; id=$2; shift 2; name="$*"
  echo "=== $id $(date +%T)"
  j=$(ls <runner>/kiln/packs/work/$id/*.jsonl)
  bash $S/build.sh $id "$name" <runner>/kiln/packs/work/$id/manifest.json $j > <runner>/kiln/packs/logs/build-$id.log 2>&1 || echo "build FAILED $id"
  tail -2 <runner>/kiln/packs/logs/build-$id.log
done
echo ALLDONE $(date +%T)
