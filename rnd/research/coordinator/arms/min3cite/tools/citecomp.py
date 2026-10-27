#!/usr/bin/env python3
"""MIN3CITE citation compliance + length from traces (no judge).
Usage: citecomp.py <traces.jsonl> [ids file] [--rows]
source-present = answer.shown non-empty and not declined (sources the engine showed);
compliant = final answer.cited non-empty (>= 1 [n] the engine kept, after CT-1 removal and attribution);
model_cited = the model's streamed text contains a [n] (token events), before engine checks;
kept_model = compliant without any citations:added reason code (the model's own [n] survived);
warned = text starts with the released-decline warning line; outTok = timing.outputTokens."""
import json, re, sys, statistics as S
WARN = "Not found in this phone's offline library."
args = [a for a in sys.argv[1:] if not a.startswith("--")]
ids = set(open(args[1]).read().split()) if len(args) > 1 else None
rows = []
for l in open(args[0]):
    t = json.loads(l)
    if ids and t["itemId"] not in ids: continue
    a = t["answer"]; rc = t["route"]["reasonCodes"]
    raw = "".join(e.get("text", "") for e in t["events"] if e.get("type") == "token")
    shown = len(a.get("shown") or [])
    r = dict(id=t["itemId"], src=shown, declined=bool(a.get("declined")), cited=a.get("cited") or [],
             model_cited=bool(re.search(r"\[\d+\]", raw)), added=any(c.startswith("citations:added") for c in rc),
             removed=any(c.startswith("citations:removed") for c in rc), warned=a["text"].startswith(WARN),
             outTok=t["timing"].get("outputTokens") or 0, totalMs=t["timing"].get("totalMs") or 0,
             prefillMs=t["timing"].get("prefillMs") or 0, decode=t["timing"].get("decodeTokPerSec"),
             promptTok=t["timing"].get("promptTokens") or 0, sents=len(re.findall(r"[.!?](\s|$)", re.sub(r"^"+re.escape(WARN)+r".*\n", "", a["text"]))))
    rows.append(r)
sp = [r for r in rows if r["src"] > 0 and not r["declined"]]
comp = [r for r in sp if r["cited"]]
kept = [r for r in comp if not r["added"]]
gen = [r for r in rows if r["outTok"] > 0]
print(f"n {len(rows)} | source-present {len(sp)} | compliant {len(comp)}/{len(sp)} = {len(comp)/max(1,len(sp)):.2f} | model-own [n] kept {len(kept)} | "
      f"model wrote [n] {sum(r['model_cited'] for r in sp)} | engine-added {sum(r['added'] for r in sp)} | removed-any {sum(r['removed'] for r in sp)} | "
      f"warned(source-present) {sum(r['warned'] for r in sp)} | outTok median {S.median([r['outTok'] for r in gen]) if gen else 0} mean {S.mean([r['outTok'] for r in gen]) if gen else 0:.1f} | "
      f"sentences median {S.median([r['sents'] for r in gen]) if gen else 0} | totalMs sum {sum(r['totalMs'] for r in rows)/1000:.1f}s")
if "--rows" in sys.argv:
    for r in rows: print(json.dumps(r))
