#!/bin/bash
# DEVICE-FINAL M1 judges = native-rc/tools/rf_judge.sh with the phone traces (never prints item text). g1: judge.v1 Opus both orders vs the Claude refs
# (b27eac37), shard_judge N 4, cap 160 per seed. g2: judge-codex.mjs (gpt-5.6-sol, r4to's ChatGPT CLI login) vs the Codex refs (047cb199), resumable.
# usage: m1_judge.sh g1|g2 <seed>
set -uo pipefail
N=<workspace>/rnd/research/coordinator/arms/native-rc; V=$N/work/v04; BE=<workspace>/boar-eval
D=<workspace>/rnd/research/coordinator/arms/device-final; S=$2; TR=$D/traces/dev-s$S.traces.jsonl; J=$D/judge
case $1 in
  g1) [ "$(shasum -a 256 $V/bench/refs/claude.jsonl | cut -c1-16)" = b27eac37a88918ca ] || { echo "claude refs sha mismatch"; exit 1; }
      bash $N/../deepthink/tools/shard_judge.sh $TR $J/dev-s$S.opus.judgments.jsonl $V/bench $N/judge/r3/ids.txt "df-v04-labrat-s$S" 4 opus > $J/g1-s$S.log 2>&1; echo "g1 s$S rc=$?";;
  g2) R=$BE/bench/v0.4/refs/v2/codex.jsonl; [ "$(shasum -a 256 $R | cut -c1-16)" = 047cb199e2673bce ] || { echo "codex refs sha mismatch"; exit 1; }
      IDS=$(paste -sd, $N/judge/r3/ids.txt)
      (cd $BE && node harness/judge-codex.mjs --bench $V/bench --refs $R --ids "$IDS" --strict --traces $TR --out $J/dev-s$S.codex.judgments.jsonl \
        --seed 7 --gap-ms 2000 --concurrency 2 --limit 160) > $J/g2-s$S.log 2>&1; echo "g2 s$S rc=$?";;
esac
