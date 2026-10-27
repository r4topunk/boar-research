#!/bin/bash
# RETRIEVE-SWEEP arm H2 HEALTH-TOPIC-FALLBACK: replays, sequential, 0 LLM. Divergence-first: the helper is reachable only inside the
# `if (health)` branches of answer.ts, so only the items that the switch-off replay marks grounding:health-strict can differ.
# Those items are replayed (switch off / on 1 / on 2); every other item's row is the switch-off row (merge in tools/h2-merge.py).
set -u
cd <workspace>/rnd/research/coordinator/arms/retrieve-sweep
T=<workspace>/kiln-local/rs-H2
R() { local name=$1; shift; local t0=$(date +%s); echo "== $name"; "$@" 2>&1 | grep -E '^\{"n"|FATAL|NEW|rror' ; echo "   $(( $(date +%s) - t0 ))s"; }
HM=replay/h2/health.main.requests.jsonl; HQ=replay/h2/health.qform.questions.jsonl; SQ=replay/h2/siblings.notmain.questions.jsonl
R H2.main.off tools/replay-h2.sh $T $HM replay/h2/H2.main.off.sub.jsonl main
python3 -I tools/proofdiff.py replay/B0.main.jsonl replay/h2/H2.main.off.sub.jsonl
R H2.main env RS_HEALTH_TOPIC_FB=1 tools/replay-h2.sh $T $HM replay/h2/H2.main.sub.jsonl main
R H2b.main env RS_HEALTH_TOPIC_FB=2 tools/replay-h2.sh $T $HM replay/h2/H2b.main.sub.jsonl main
R H2.qform.off tools/replay-h2.sh $T $HQ replay/h2/H2.qform.off.sub.jsonl qform
python3 -I tools/proofdiff.py ../qform/replay/qform.replay.jsonl replay/h2/H2.qform.off.sub.jsonl
R H2.qform env RS_HEALTH_TOPIC_FB=1 tools/replay-h2.sh $T $HQ replay/h2/H2.qform.sub.jsonl qform
R H2b.qform env RS_HEALTH_TOPIC_FB=2 tools/replay-h2.sh $T $HQ replay/h2/H2b.qform.sub.jsonl qform
R H2.sib.off tools/replay-h2.sh $T $SQ replay/h2/H2.sib.off.jsonl qform
R H2.sib env RS_HEALTH_TOPIC_FB=1 tools/replay-h2.sh $T $SQ replay/h2/H2.sib.jsonl qform
echo ALLDONE
