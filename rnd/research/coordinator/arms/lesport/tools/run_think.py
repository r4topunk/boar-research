#!/usr/bin/env python3
"""LESPORT-THINK fork driver: thinking-ON rendered prompts, one llama-completion per item. usage: run_think.py TAG N_TOKENS [extra flags...] -- id1 id2 ..."""
import json, os, subprocess, sys, time, re
H=os.path.expanduser("~"); D=f"{H}/boar/kiln/lesport-think"; OUT=f"{D}/out"
GGUF=f"{H}/boar/shared-models/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf"
BIN=f"{H}/boar/spikes/llama-omni/src/build-cpu/bin/llama-completion"; EXP=f"{H}/boar/spikes/llama-omni/experts"
tag=sys.argv[1]; n=sys.argv[2]; rest=sys.argv[3:]; i=rest.index("--"); extra=rest[:i]; ids=rest[i+1:]
env=dict(os.environ, LLAMA_MOE_LOOKAHEAD_PREFETCH="1")
allp=sorted(os.listdir(f"{D}/rendered"))
for iid in ids:
    f=[p for p in allp if p.startswith(iid)][0]; key=f[:2]
    cmd=["/usr/bin/time","-l",BIN,"-m",GGUF,"--moe-experts",EXP,"--moe-slot-bank","1280","--no-mmap","-t","4","-c","4096","--temp","0.7","--top-k","40","--top-p","0.95","--min-p","0.05","--seed","42","-n",n,"-f",f"{D}/rendered/{f}","-no-cnv","--no-display-prompt"]+extra
    t0=time.time(); r=subprocess.run(cmd,capture_output=True,env=env,timeout=1500); w=time.time()-t0
    txt=r.stdout.decode("utf-8","replace"); err=r.stderr.decode("utf-8","replace")
    open(f"{OUT}/{tag}-{key}.raw.txt","w").write(txt); open(f"{OUT}/{tag}-{key}.err","w").write(err)
    pe=re.search(r"prompt eval time =\s+([\d.]+) ms /\s+(\d+) tokens",err)
    ev=re.search(r"\n[^\n]*\beval time =\s+([\d.]+) ms /\s+(\d+) runs.*?([\d.]+) tokens per second",err.split("prompt eval time")[-1]) if pe else None
    g=lambda rx:(lambda m:float(m.group(1)) if m else 0)(re.search(rx,err))
    row=dict(id=key,rc=r.returncode,wall=round(w,1),prefill_s=float(pe.group(1))/1000 if pe else None,out_tokens=int(ev.group(2)) if ev else None,tok_s=float(ev.group(3)) if ev else None,rss_gib=g(r"(\d+)\s+maximum resident set size")/2**30,fp_gib=g(r"(\d+)\s+peak memory footprint")/2**30,has_close="</think>" in txt,chars=len(txt))
    open(f"{OUT}/{tag}.results.jsonl","a").write(json.dumps(row)+"\n"); print(row,flush=True)
