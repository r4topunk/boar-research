#!/bin/bash
# GEMMATHINK MacBook driver (criterion 46e058d3…) = deepthink dt.sh on the gemmathink tree; mkreq arm G = Gemma 4 deep model. Prints counts/ids/timings only.
#   dv.sh mkreq <srcRequests> <outRequests> <runId> <D|C> [ids,comma]   rewrite runId + config.settings (items untouched)
#   dv.sh launch <requests> <runId> <D|C>    scp requests, start remote-run.sh under nohup on the mini, return at once
#   dv.sh status <runId>                     remote STATUS + progress line count
#   dv.sh fetch <runId> <outTraces> <requests>  scp traces/logs, validate, print counts/route/timing aggregates
set -u
H=MINI_HOST; T=boar/kiln/be-0cfd4a77-gemmathink; E=<workspace>/boar-eval
cmd=$1; shift
case $cmd in
mkreq) src=$1 out=$2 run=$3 arm=$4 ids=${5:-}
  if [ $arm = G ]; then st='{"quickFirst":true,"alwaysComplete":true,"deepModelId":"gemma-4-26b-a4b-ud-q2kxl"}'; elif [ $arm = D ]; then st='{"quickFirst":true,"alwaysComplete":true,"deepModelId":"qwen3.6-35b-a3b-ud-q2kxl"}'; else st='{"quickFirst":true,"alwaysComplete":false}'; fi
  jq -c --arg r "$run" --argjson s "$st" --arg ids "$ids" 'select($ids=="" or (.item.id as $i | ($ids|split(",")|index($i))!=null)) | .runId=$r | .config.settings=$s | .config.arm="gemmathink"' "$src" > "$out"
  echo "requests $(wc -l < "$out") runId $run settings $(head -1 "$out" | jq -c .config.settings) seed $(head -1 "$out" | jq .seed) sha $(shasum -a 256 "$out" | cut -c1-12)";;
launch) req=$1 run=$2 arm=$3
  ssh -T -n $H "test -e ~/$T/be-repo/runs/$run/STATUS" && { echo "REFUSE: $run already has a STATUS (a run started or finished); pick a new run id"; exit 2; }
  ssh -T -n $H "mkdir -p ~/$T/be-repo/runs/$run" && scp -q "$req" "$H:$T/be-repo/runs/$run/requests.jsonl" || exit 1
  ssh -T -n -f $H "nohup bash -l <runner>/kiln/gemmathink-remote-run.sh $run $arm > <runner>/kiln/gemmathink-$run.nohup.log 2>&1 < /dev/null &"
  echo "launched $run ($arm) at $(date +%H:%M)";;
status) run=$1
  ssh -T -n $H "cat ~/$T/be-repo/runs/$run/STATUS 2>/dev/null; echo progress \$(grep -cE ' (success|error|declined|fail)' ~/$T/be-repo/runs/$run/run.log 2>/dev/null) lines; tail -1 <runner>/heavy.log";;
fetch) run=$1 out=$2 req=$3
  scp -q "$H:$T/be-repo/runs/$run/traces.jsonl" "$out" || exit 1
  scp -q "$H:$T/be-repo/runs/$run/run.log" "${out%.jsonl}.log"; scp -q "$H:$T/be-repo/runs/$run/traces.server.log" "${out%.jsonl}.server.log" 2>/dev/null
  scp -q "$H:$T/be-repo/runs/$run/STATUS" "${out%.jsonl}.status"
  pnpm -s -C $E/adapters/desktop-node exec tsx scripts/validate.ts "$out" --requests "$req" | grep -v '^{' | head -3
  python3 - "$out" <<'PY'
import json, sys, collections, statistics as st
T = [json.loads(l) for l in open(sys.argv[1])]
rc = lambda t: t.get("route", {}).get("reasonCodes", [])
deep = [t["itemId"] for t in T if any(c.startswith("generate:deep-model-") for c in rc(t))]
gen = collections.Counter(next((c for c in rc(t) if c.startswith("generate:")), "none") for t in T)
task = collections.Counter(next((c for c in rc(t) if c.startswith("task:")), "none") for t in T)
tier = collections.Counter(t.get("route", {}).get("tier") for t in T)
med = lambda k: st.median([t["timing"][k] for t in T if t.get("timing", {}).get(k) is not None] or [float("nan")])
det = sum(any(c.startswith("detector:p=") for c in rc(t)) for t in T)
gate = sum(any(e.get("kind") == "route-gate" for e in t.get("events", [])) for t in T)
print(json.dumps({"n": len(T), "errors": sum(bool(t.get("error")) for t in T), "errorCodes": dict(collections.Counter((t.get("error") or {}).get("code") for t in T if t.get("error"))),
  "deepRouted": len(deep), "detectorConsulted": det, "gateEvents": gate, "generate": dict(gen), "task": dict(task), "tier": dict(tier),
  "ttftMedMs": med("ttftMs"), "totalMedMs": med("totalMs"), "firstVisibleMedMs": med("firstVisibleMs"), "totalSumS": round(sum(t["timing"].get("totalMs") or 0 for t in T) / 1000),
  "deepModel": T[0]["runtime"]["versions"].get("deep.model"), "deepSha": (T[0]["runtime"]["versions"].get("deep.model.sha256") or "")[:12],
  "adapter": T[0]["runtime"]["versions"].get("adapter"), "backend": T[0]["runtime"].get("backend")}))
PY
  echo "traces sha $(shasum -a 256 "$out" | cut -c1-12)";;
think) tr=$1; idf=${2:-}; out=${3:-}   # per-item thinking stats from a trace file (numbers only); optional judged ids + JSON out
  python3 - "$tr" "$idf" "$out" <<'PY'
import json, sys, statistics as st
T=[json.loads(l) for l in open(sys.argv[1])]; want=set(open(sys.argv[2]).read().split()) if sys.argv[2] else None
MSG="I have thought enough"; rows=[]
for t in T:
    if want is not None and t["itemId"] not in want: continue
    rc=t.get("route",{}).get("reasonCodes",[]); g=[e for e in t.get("events",[]) if e.get("kind")=="generation"]
    tm=t.get("timing",{}); raw=json.dumps(t)
    rows.append({"id":t["itemId"],"deepThinking":"generate:deep-thinking" in rc,"gens":len(g),
      "reasoningTokens":tm.get("reasoningTokens", sum(e.get("reasoningTokens") or 0 for e in g)),
      "maxGenReasoning":max([e.get("reasoningTokens") or 0 for e in g] or [0]),
      "budgetHitGen":sum(1 for e in g if (e.get("reasoningTokens") or 0)>=1024),
      "budgetExceeded":any(e.get("thinkingBudgetExceeded") for e in g),
      "budgetMsgInTrace":raw.count(MSG),
      "outputTokens":sum(e.get("outputTokens") or 0 for e in g),
      "answerTokens":sum(max((e.get("outputTokens") or 0)-(e.get("reasoningTokens") or 0),0) for e in g),
      "totalMs":tm.get("totalMs"),"ttftMs":tm.get("ttftMs"),"reasoningMs":tm.get("reasoningMs"),"error":bool(t.get("error"))})
md=lambda k:st.median([r[k] for r in rows if r[k] is not None]) if rows else None
q=lambda k,p:sorted(r[k] for r in rows if r[k] is not None)[int(p*(len(rows)-1))]
th=[r for r in rows if r["deepThinking"]]
agg={"n":len(rows),"deepThinkingRouted":len(th),"errors":sum(r["error"] for r in rows),
 "reasoningTokens":{"median":md("reasoningTokens"),"p10":q("reasoningTokens",.1),"p90":q("reasoningTokens",.9),"max":max(r["reasoningTokens"] for r in rows),"zero":sum(r["reasoningTokens"]==0 for r in th)},
 "budgetHitItems_ge1024":sum(r["budgetHitGen"]>0 for r in rows),"budgetExceededItems":sum(r["budgetExceeded"] for r in rows),"budgetMsgItems":sum(r["budgetMsgInTrace"]>0 for r in rows),
 "answerTokensMedian":md("answerTokens"),"outputTokensMedian":md("outputTokens"),"totalMsMedian":md("totalMs"),"totalMsP90":q("totalMs",.9),"ttftMsMedian":md("ttftMs"),"reasoningMsMedian":md("reasoningMs"),
 "totalSumS":round(sum(r["totalMs"] or 0 for r in rows)/1000)}
print(json.dumps(agg))
if sys.argv[3]: json.dump({"aggregate":agg,"perItem":rows},open(sys.argv[3],"w"),indent=1)
PY
  ;;
esac
