#!/bin/bash
# Stub for judge.mjs (tests only, 0 LLM calls): writes both orders for every id in --ids to --out.
# Env: STUB_SKIP=id,id (omit these ids = judge.mjs skipping an errored trace) STUB_SLEEP=s STUB_RC=n (exit code) STUB_MARK=file (touch when run)
while [ $# -gt 0 ]; do case $1 in --out) out=$2; shift;; --ids) ids=$2; shift;; esac; shift; done
[ -n "${STUB_MARK:-}" ] && echo "ran $out" >> "$STUB_MARK"
sleep "${STUB_SLEEP:-0}"; mkdir -p "$(dirname "$out")"
IFS=, read -r -a L <<< "$ids"
for i in "${L[@]}"; do case ",${STUB_SKIP:-}," in *",$i,"*) continue;; esac
  for o in boarA boarB; do echo "{\"queryId\":\"$i\",\"order\":\"$o\",\"ok\":true,\"judgeModel\":\"stub\",\"mapped\":{\"winner\":\"tie\",\"boar\":{\"correctness\":3,\"completeness\":3,\"usefulness\":3},\"ref\":{\"correctness\":4,\"completeness\":4,\"usefulness\":4}}}" >> "$out"; done; done
exit "${STUB_RC:-0}"
