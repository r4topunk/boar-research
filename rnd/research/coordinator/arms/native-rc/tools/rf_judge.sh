#!/bin/bash
# RULER-FINAL judges (never prints item text). g1: judge.v1 Opus both orders vs the Claude refs (copy in work/v04/bench/refs/claude.jsonl, sha b27eac37),
# shard_judge N 4 (150 calls, cap 160). g2: boar-eval harness/judge-codex.mjs unchanged (judge.v1-codex, gpt-5.6-sol, reasoning high, r4to's ChatGPT
# CLI login via codex exec, as CV5-LADDER-CODEX) vs the Codex refs boar-eval/bench/v0.4/refs/v2/codex.jsonl (sha 047cb199), --strict, seed 7,
# --concurrency 2 --gap-ms 2000, --limit 160; resumable (rerun the same command after a rate limit). usage: rf_judge.sh g1|g2
set -uo pipefail
A=<workspace>/rnd/research/coordinator/arms/native-rc; V=$A/work/v04; BE=<workspace>/boar-eval; TR=$V/traces/lite-s42.traces.jsonl; J=$A/judge/rf
mkdir -p $J
case $1 in
  g1) [ "$(shasum -a 256 $V/bench/refs/claude.jsonl | cut -c1-16)" = b27eac37a88918ca ] || { echo "claude refs sha mismatch"; exit 1; }
      bash $A/../deepthink/tools/shard_judge.sh $TR $J/lite-s42.opus.judgments.jsonl $V/bench $A/judge/r3/ids.txt "nrc-v04-lite-s42" 4 opus > $J/g1.log 2>&1; echo "g1 rc=$?";;
  g2) R=$BE/bench/v0.4/refs/v2/codex.jsonl; [ "$(shasum -a 256 $R | cut -c1-16)" = 047cb199e2673bce ] || { echo "codex refs sha mismatch"; exit 1; }
      IDS=$(paste -sd, $A/judge/r3/ids.txt)
      node $BE/harness/judge-codex.mjs --bench $V/bench --refs $R --ids "$IDS" --strict --traces $TR --out $J/lite-s42.codex.judgments.jsonl \
        --seed 7 --gap-ms 2000 --concurrency 2 --limit 160 > $J/g2.log 2>&1; echo "g2 rc=$?";;
esac
