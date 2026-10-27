import json, sys, collections
import terms, terms_v1
E=[json.loads(l) for l in open("../health-embed/eval.jsonl")]
M=[json.loads(l) for l in open("../pt-recall/pt-mirror.jsonl")]
F=json.load(open("../firstaidqa/sample400.json"))
items=[(e["id"],e["q"],e["label"]) for e in E]+[(m["id"],m["q"],"danger") for m in M]+[(f"faqa-{i}",q,"faqa") for i,q in enumerate(F)]
C=collections.Counter(); changed=[]
for i,q,lab in items:
    a,b=terms.regex_condition(q),terms_v1.regex_condition(q)
    if a!=b: changed.append((lab,i,a,b,q[:90]))
    C[(lab, "v1 fires" if b and not b.startswith("MULTI") else ("multi" if b else "none"))]+=1
print(sorted(C.items()))
print("\nchanges vs v0.1 (label, id, v0.1 -> v1):")
for c in changed: print("  ",c)
