import json,re,sys
A="<workspace>/rnd/research/coordinator/arms/gate17"
items=json.load(open(A+"/gate/items.json"))["items"]
q={}
for t in ("K0-main","K1-screen"):
    for l in open(f"{A}/traces/gate17dump-{t}-s42.traces.jsonl"):
        r=json.loads(l); q[("K0main" if t=="K0-main" else "K1screen")+":"+r["itemId"]]=r["question"]
out=[]
for x in items:
    ch=re.split(r"\n\n(?=\[\d+\] )",x["context"])
    strip=lambda c:re.sub(r"^\[\d+\] ","",c)
    rev="\n\n".join(f"[{i+1}] {strip(c)}" for i,c in enumerate(reversed(ch)))
    out.append({"key":x["key"],"question":q[x["key"]],"response":x["response"],"chunks":x["context"],"chunks_rev":rev,"n":len(ch)})
json.dump(out,open(sys.argv[1],"w"))
print(len(out))
