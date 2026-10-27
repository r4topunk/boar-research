#!/usr/bin/env bash
# CVH L1: judge only the changed items (judge.v1-med, both orders), run from the MacBook. Resumes from its output.
cd <workspace>/boar-eval; O=runs/kiln/cvh-l1
for s in 44 45; do node harness/judge.mjs --traces $O/cvh-v01-s$s.traces.jsonl --out $O/cvh-v01-s$s.judgments.v1-med.jsonl --bench bench/v0.1 --system cvh-l1-s$s --effort medium --ids lan-cmp-001,lan-cmp-002,lan-cmp-004,lan-cmp-005 > $O/cvh-v01-s$s.judge.log 2>&1; echo "judge s$s rc=$?"; done
