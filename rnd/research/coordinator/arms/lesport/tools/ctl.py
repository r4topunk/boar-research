#!/usr/bin/env python3
import json, os, subprocess, time, urllib.request, sys
H=os.path.expanduser("~"); D=f"{H}/boar/kiln/lesport-think"; OUT=f"{D}/out"
SRV=f"{H}/boar/spikes/llama-b11010/build-cpu/bin/llama-server"; GGUF=f"{H}/boar/shared-models/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf"
P=8097
sp=subprocess.Popen([SRV,"-m",GGUF,"-t","4","-tb","4","-c","4096","-ngl","0","-np","1","--jinja","--no-webui","--cache-ram","0","--reasoning-format","deepseek","--host","127.0.0.1","--port",str(P)],stdout=open(f"{OUT}/ctl-server.log","w"),stderr=subprocess.STDOUT)
def post(path,body,t=900):
    r=urllib.request.Request(f"http://127.0.0.1:{P}{path}",json.dumps(body).encode(),{"Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(r,timeout=t))
for _ in range(300):
    try: urllib.request.urlopen(f"http://127.0.0.1:{P}/health",timeout=2); break
    except Exception: time.sleep(2)
rows=[]
for k in range(10):
    key=f"{k:02d}"; sysm=open(f"{D}/msgs/{key}.sys").read(); usr=open(f"{D}/msgs/{key}.usr").read()
    msgs=[{"role":"system","content":sysm},{"role":"user","content":usr}]
    ap=post("/apply-template",{"messages":msgs})["prompt"]
    rend=open(glob:=[f"{D}/rendered/{f}" for f in sorted(os.listdir(f"{D}/rendered")) if f.startswith(key)][0]).read()
    npt=len(post("/tokenize",{"content":rend,"add_special":False,"parse_special":True})["tokens"])
    t0=time.time()
    r=post("/v1/chat/completions",{"messages":msgs,"max_tokens":1024,"temperature":0.7,"top_k":40,"top_p":0.95,"min_p":0.05,"seed":42,"cache_prompt":False})
    w=time.time()-t0; m=r["choices"][0]["message"]; rc=m.get("reasoning_content") or ""; ct=m.get("content") or ""
    ntok=lambda s: len(post("/tokenize",{"content":s,"add_special":False})["tokens"]) if s else 0
    tm=r.get("timings",{})
    row=dict(id=key,apply_template_match=(ap==rend),apply_tail=ap[-30:],n_prompt=npt,reasoning_tok=ntok(rc),content_tok=ntok(ct),completion_tokens=r["usage"]["completion_tokens"],finish=r["choices"][0]["finish_reason"],
             wall=round(w,1),prefill_s=tm.get("prompt_ms",0)/1000,pred_tps=tm.get("predicted_per_second"),content_nonempty=bool(ct.strip()),reasoning=rc[:0])
    open(f"{OUT}/ctl.results.jsonl","a").write(json.dumps(row)+"\n"); print(row,flush=True)
sp.terminate()
