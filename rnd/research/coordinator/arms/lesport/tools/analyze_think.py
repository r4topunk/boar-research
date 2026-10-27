import json,os,re,urllib.request,statistics as st
D=os.path.expanduser("<runner>/kiln/lesport-think"); OUT=D+"/out"; P=8097
def tok(s):
    if not s.strip(): return 0
    r=urllib.request.Request(f"http://127.0.0.1:{P}/tokenize",json.dumps({"content":s,"add_special":False}).encode(),{"Content-Type":"application/json"})
    return len(json.load(urllib.request.urlopen(r))["tokens"])
ctl={}
for l in open(OUT+"/ctl.results.jsonl"): r=json.loads(l); ctl[r["id"]]=r
rows=[]
for k in [f"{i:02d}" for i in range(10)]:
    t=open(f"{OUT}/cliB-{k}.raw.txt").read(); usr=open(f"{D}/msgs/{k}.usr").read().strip()
    e=t.find("available commands"); s=t.find(usr[-40:],e)+40 if usr[-40:] in t else e
    body=t[s:]; i=body.find("I have thought enough"); j=body.find("[End thinking]"); m=re.search(r"\n\[ Prompt: ([\d.]+) t/s \| Generation: ([\d.]+) t/s \]",body)
    rea=body[:i].strip(); ans=body[j+len("[End thinking]"):m.start() if m else None].strip()
    err=open(f"{OUT}/cliB-{k}.err").read(); g=lambda rx:int(re.search(rx,err).group(1))
    n=ctl[k]["n_prompt"]
    rows.append(dict(id=k,reason_tok=tok(rea),ans_tok=tok(ans),closed=j>0,forced=i>0,ans_ne=bool(ans),pp_tps=float(m.group(1)),tg_tps=float(m.group(2)),prefill_s=n/float(m.group(1)),n_prompt=n,rss=g(r"(\d+)\s+maximum resident")/2**30,fp=g(r"(\d+)\s+peak memory")/2**30))
for r in rows: print(r)
M=lambda key,rs=rows: round(st.median([r[key] for r in rs]),2)
print("FORK median reason",M("reason_tok"),"ans",M("ans_tok"),"tg",M("tg_tps"),"prefill",M("prefill_s"),"rss",M("rss"),"fp",M("fp"),"closed",sum(r["closed"] for r in rows),"ans_ne",sum(r["ans_ne"] for r in rows),"max reason",max(r["reason_tok"] for r in rows))
c=list(ctl.values())
print("CTL reasoning",[r["reasoning_tok"] for r in c],"content",[r["content_tok"] for r in c],"finish",[r["finish"] for r in c])
print("CTL median reason",st.median(r["reasoning_tok"] for r in c),"tps",st.median(r["pred_tps"] for r in c),"prefill",st.median(r["prefill_s"] for r in c),"atmatch",sum(r["apply_template_match"] for r in c),"nonempty",sum(r["content_nonempty"] for r in c))
json.dump(rows,open(OUT+"/fork-analysis.json","w"))
