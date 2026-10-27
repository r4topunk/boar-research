import json
C="<workspace>/rnd/research/coordinator/arms/coverage-map/"
K=json.load(open(C+"compose/kfull.json"))["items"]; CMS=json.load(open(C+"compose/cmstage.json")); O=json.load(open(C+"aggregates/cm-oracle.json"))
ORDER={"S1":0,"S2":1,"S3":2,"K":3}; lab="N10.gidf"
out={}
for i,v in K.items():
    s=v[lab]["stage"]; src="lex"
    if i in O:
        o=CMS[lab]["items"].get(i)
        if o and ORDER[o]>ORDER[s]: s=o; src="oracle"
    out[i]=dict(stage=s, lexstage=v[lab]["stage"], oracle=CMS[lab]["items"].get(i), set=v["set"], tag=v["tag"], inpack=v[lab]["inpack"])
sel={i:e for i,e in out.items() if e["stage"] in("S2","S3")}
json.dump(sel,open(C+"autopsy52/work/list52.json","w"),indent=1)
from collections import Counter
print(len(sel), Counter((e["set"],e["stage"]) for e in sel.values()))
for i,e in sel.items(): print(i,e["stage"],e["lexstage"],e["oracle"],e["inpack"])
