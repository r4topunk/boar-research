# cmp.py base.traces sel.traces : which items' placed contexts changed; reason codes; per-item sources
import json,sys
def load(p):
    d={}
    for l in open(p):
        r=json.loads(l); ev=[e for e in r["events"] if e.get("type")=="sources" and any(x.get("text") for x in e.get("sources",[]))]
        src=ev[-1]["sources"] if ev else []
        d[r["itemId"]]=(json.dumps([(x["title"],x.get("text")) for x in src]), r["route"].get("reasonCodes"), r["timing"] if "timing" in r else None, r["question"], src)
    return d
a=load(sys.argv[1]); b=load(sys.argv[2]); ch=[i for i in a if a[i][0]!=b[i][0]]
print("changed:",len(ch),ch)
if "-v" in sys.argv:
  for i in ch:
    print("=====",i,a[i][3]); 
    for lab,d in(("BASE",a),("SEL",b)):
        print(" ",lab,[c for c in d[i][1] if c.startswith(("context","grounding"))])
        for x in d[i][4]: print("    >",x["title"][-50:],"|",(x.get("text") or "")[:700].replace("\n","\\n"))
