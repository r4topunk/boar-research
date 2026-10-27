#!/usr/bin/env bash
# CRYPTOSEL L1: judge only the changed items (judge.v1-med, both orders), run from the MacBook. lan-exp-007 changed with an identical context (generation noise) and is judged too.
cd <workspace>/boar-eval; O=runs/kiln/cryptosel-l1
for s in 44 45; do node harness/judge.mjs --traces $O/cryptosel-v01-s$s.traces.jsonl --out $O/cryptosel-v01-s$s.judgments.v1-med.jsonl --bench bench/v0.1 --system cryptosel-l1-s$s --effort medium --ids vit-cry-002,vit-cry-003,vit-cry-009,lan-exp-007 > $O/cryptosel-v01-s$s.judge.log 2>&1; echo "judge s$s rc=$?"; done
