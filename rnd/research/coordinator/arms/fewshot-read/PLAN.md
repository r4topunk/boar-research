# FEWSHOT-READ plan / resume
Criterion FEWSHOT-criterion.md (sha256 86bc3115...), committed 081c410c before generation.
Resume (re-runs skip finished steps by inputs sha):
    cd <workspace>/rnd/research/coordinator/arms
    OUT_BASE=$PWD CRITERION=$PWD/fewshot-read/FEWSHOT-criterion.md bash null-cal/tools/run_pool.sh fewshot-read K0 ../ruler/ids/stage1-pool.ids $PWD/fewshot-read/fewshot-read.patch
    python3 -I sample2-gate/tools/report.py fewshot-read
