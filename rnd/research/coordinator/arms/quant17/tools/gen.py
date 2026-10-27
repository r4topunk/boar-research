# gen.py <items dir> <port> <out jsonl>: greedy generation via llama-server /completion (raw rendered prompt)
import json,sys,urllib.request
d,port,out=sys.argv[1],sys.argv[2],sys.argv[3]
with open(out,'w') as f:
    for i in range(30):
        p=open(f"{d}/{i:02d}.prompt.txt").read()
        req=urllib.request.Request(f"http://127.0.0.1:{port}/completion",json.dumps({"prompt":p,"n_predict":512,"temperature":0,"seed":42,"cache_prompt":False,"return_tokens":True}).encode(),{"Content-Type":"application/json"})
        r=json.load(urllib.request.urlopen(req,timeout=900))
        f.write(json.dumps({"i":i,"id":open(f"{d}/{i:02d}.id").read(),"text":r["content"],"tokens":r.get("tokens"),"n_prompt":r["timings"]["prompt_n"] if "timings" in r else None,"n_pred":r.get("tokens_predicted"),"stop":r.get("stop_type")})+"\n"); f.flush()
