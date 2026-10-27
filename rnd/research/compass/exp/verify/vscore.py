import json, numpy as np
D=[d for d in json.load(open("verified.json")) if d["label"]!="unlabeled"]
good=lambda d:d["label"]=="pass"
def show(name,f):
    S=[d for d in D if f(d)]; g=sum(good(d) for d in S); cw=sum(d["label"]=="confident-wrong" for d in S)
    print(f"{name:28} shown {len(S):2}/{len(D)}  pass {g:2} ({g/len(S):.0%} of shown)  fail-missing {len(S)-g-cw:2}  cw {cw}  | pass recall {g}/{sum(map(good,D))}" if S else f"{name:28} shown 0")
show("A: show all (no verifier)",lambda d:True)
show("verifier Qwen2.5-1.5B yes",lambda d:d["v15"]=="yes")
show("verifier Qwen3-4B yes",lambda d:d["v4b"]=="yes")
for t in [.70,.75,.80,.85]: show(f"cosine >= {t}",lambda d,t=t:d["cos"]>=t)
show("1.5B yes AND cos>=.75",lambda d:d["v15"]=="yes" and d["cos"]>=.75)
from collections import Counter
print("cos by label:",{l:np.round(np.median([d['cos'] for d in D if d['label']==l]),3) for l in set(d['label'] for d in D)})
print("CW items:",[(d["id"],d["v15"],d["v4b"],round(d["cos"],2),d["draft"][:90]) for d in D if d["label"]=="confident-wrong"])
pt=[d for d in D if d["id"].endswith("-pt")]; print("PT drafts:",len(pt))
