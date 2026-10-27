#!/usr/bin/env python3
"""DEEPHEDGE step-0 gate: jev 'hedged' classification of answers (E vs H) on the hedged-11 ids (+ all generated ids for context).
usage: hedge_gate.py <E.traces> <H.traces> <hedged.ids> <out.json>   (0 Claude calls; caches under <E traces dir>/hedge-cache/; ids/probs only)"""
import json, os, sys, hashlib, urllib.request, time
GATEWAY="https://ai-gateway.vercel.sh/v1/evaluate"; KEY=os.environ.get("VERCEL_AI_GATEWAY") or os.environ.get("AI_GATEWAY_API_KEY")
Q={"hedged":{"type":"boolean","instructions":"Does `answer` decline, defer to a professional, website or authority, or stay generic and cautious INSTEAD OF giving the substantive content (facts, numbers, steps, a comparison) the question would need?",
   "criteria":{"true":"the answer's main content is a referral, a refusal, a generic caution or a statement that it cannot say; substantive facts are absent or token","false":"the answer gives substantive facts, numbers, steps or a comparison, even if a safety note is attached"}},
   "substantive_first":{"type":"boolean","instructions":"Does `answer` start with substantive content (a fact, number, step or direct answer) rather than with a caution, disclaimer or referral?"}}
def call(body,cdir):
    raw=json.dumps(body,sort_keys=True,ensure_ascii=False); h=hashlib.sha256(raw.encode()).hexdigest(); cp=os.path.join(cdir,h+".json")
    if os.path.exists(cp): return json.load(open(cp))
    req=urllib.request.Request(GATEWAY,data=raw.encode(),headers={"authorization":"Bearer "+KEY,"content-type":"application/json"}); d=1
    for a in range(6):
        try:
            with urllib.request.urlopen(req,timeout=90) as r: res=json.load(r)
            json.dump(res,open(cp,"w")); return res
        except Exception as e:
            if a==5: raise
            time.sleep(d); d=min(d*2,8)
E,H,IDS,OUT=sys.argv[1:5]; load=lambda f:{json.loads(l)["itemId"]:json.loads(l) for l in open(f)}
e,h=load(E),load(H); hed=[l.strip() for l in open(IDS) if l.strip()]; cdir=os.path.join(os.path.dirname(os.path.abspath(E)),"hedge-cache"); os.makedirs(cdir,exist_ok=True)
rows=[]
for i in e:
    if i not in h: continue
    rec={"id":i,"hedged11":i in hed,"err":bool(e[i].get("error")),"words_E":len((e[i]["answer"]["text"] or "").split()),"words_H":len((h[i]["answer"]["text"] or "").split()),"on":"deephedge:on" in e[i]["route"]["reasonCodes"]}
    for lab,R in (("E",e),("H",h)):
        res=call({"model":"typesafe-ai/jev","state":{"answer":(R[i]["answer"]["text"] or "")[:3000]},"questions":Q},cdir)["answers"]
        rec[f"p_hedged_{lab}"]=round(res["hedged"]["probability"],3); rec[f"p_first_{lab}"]=round(res["substantive_first"]["probability"],3)
    rows.append(rec)
th=0.6; sub=[r for r in rows if r["hedged11"]]
summ={"n":len(rows),"n_hedged11":len(sub),"on":sum(r["on"] for r in rows),"errors":sum(r["err"] for r in rows),
      "hedged11_hedged_H":sum(r["p_hedged_H"]>=th for r in sub),"hedged11_hedged_E":sum(r["p_hedged_E"]>=th for r in sub),
      "all_hedged_H":sum(r["p_hedged_H"]>=th for r in rows),"all_hedged_E":sum(r["p_hedged_E"]>=th for r in rows),
      "first_substantive_H":sum(r["p_first_H"]>=th for r in rows),"first_substantive_E":sum(r["p_first_E"]>=th for r in rows),
      "words_p50_E":sorted(r["words_E"] for r in rows)[len(rows)//2],"words_p50_H":sorted(r["words_H"] for r in rows)[len(rows)//2]}
summ["gate"]="PASS" if summ["errors"]==0 and summ["hedged11_hedged_E"]<=max(0,summ["hedged11_hedged_H"]//2) and summ["words_p50_E"]<=2*summ["words_p50_H"] else "FAIL"
json.dump({"summary":summ,"items":rows},open(OUT,"w"),indent=1); print(json.dumps(summ))
