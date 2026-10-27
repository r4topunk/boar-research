# SAMPLE2-GATE plan / resume
Criterion SAMPLE2-criterion.md (sha256 5e59c13c...), committed 081c410c before generation.
    cd <workspace>/rnd/research/coordinator/arms/sample2-gate
    bash tools/gen_dump.sh                                   # 1. S43 + prompt dump on the mini (waits for a slot and the 2-server guard)
    python3 -I tools/s2g.py inputs gate/s2g.inputs.jsonl gate/items.json
    bash tools/run_gate.sh s2g gate/s2g.inputs.jsonl         # 2. GATE17 on the mini -> gate/s2g.outputs.jsonl
    python3 -I tools/s2g.py select gate/s2g.outputs.jsonl gate/items.json traces/sample2-gate-K0-stage1-pool-s42s43.traces.jsonl gate/selection.json
    CRITERION=$PWD/SAMPLE2-criterion.md bash tools/judge_agg.sh   # 3. Haiku on the S43 picks only
    python3 -I tools/report.py sample2-gate
Tool fix after freeze (no criterion change): gen_dump.sh first try failed (adapter refuses a request arm != tree ARM); the job now writes the arm name into tree/ARM, as run_pool.sh does.
