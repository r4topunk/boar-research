#!/bin/bash
# SELFTEST-LOCALJUDGE chain: wait for pass 1 (localjudge.log ALLDONE) -> pass 2 (the 6 wave-1 packs skipped by the missing-ids bug)
# -> aggregate (aggregates/localjudge.json) -> stop the mini's Qwen judge server (port 18092 only; detector :8094 untouched) -> close the tunnel.
H=$(cd "$(dirname "$0")/.." && pwd); D=$H/selftest-runs; cd "$D"
until grep -q ALLDONE localjudge.log; do sleep 30; done
caffeinate -i "$H/tools/localjudge_run.sh" qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en
python3 -I "$H/tools/localjudge_agg.py" > "$H/aggregates/localjudge.json" && echo "agg ok"
ssh -n $RUNNER_HOST "bash -c 'pkill -f \"llama-server.*Qwen3.6-35B.*18092\"; sleep 3; pgrep -fl llama-server | cut -c1-120; df -g ~ | tail -1'" && echo "server stopped $(date '+%F %T')"
pkill -f "ssh -N -L 18092:127.0.0.1:18092"; echo FINISHED
