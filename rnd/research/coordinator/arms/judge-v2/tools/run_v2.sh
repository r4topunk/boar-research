#!/bin/bash
# JUDGE-V2 runs (MacBook, claude -p, Haiku 5.5). Order: (1) key-point extraction for the 97 dev items (frozen prompt, Haiku effort medium, cached in data/kp-dev97.jsonl);
# (2) judge.v2 on the K0 MAIN control answers, repeats 1-3 (Haiku effort low, concurrency 4); (3) judge.v2 on the reference answers, repeat 1 (denominator).
# Every call goes to runs/calls.ledger; judge-v2.mjs refuses a call once the ledger reaches CAP (criterion calls_cap). Resumable.
set -eu
J=<workspace>/rnd/research/coordinator/arms/judge-v2; E=<workspace>/boar-eval; CAP=${CAP:-1200}; LED=$J/runs/calls.ledger
cd $E
node harness/judge-v2.mjs extract --items $J/data/items-dev97.jsonl --out $J/data/kp-dev97.jsonl --effort medium --ledger $LED --cap $CAP
for r in 1 2 3; do
  node harness/judge-v2.mjs judge --items $J/data/items-dev97.jsonl --kp $J/data/kp-dev97.jsonl --answers $J/data/answers-K0main.jsonl --side app --repeat $r \
    --out $J/v2/app-r$r.jsonl --effort low --concurrency 4 --ledger $LED --cap $CAP
done
node harness/judge-v2.mjs judge --items $J/data/items-dev97.jsonl --kp $J/data/kp-dev97.jsonl --answers $J/data/answers-ref.jsonl --side ref --repeat 1 \
  --out $J/v2/ref-r1.jsonl --effort low --concurrency 4 --ledger $LED --cap $CAP
echo "run_v2 done; ledger $(wc -l < $LED | tr -d ' ')"
