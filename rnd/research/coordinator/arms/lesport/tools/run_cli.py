#!/usr/bin/env python3
"""LESPORT-THINK fork via llama-cli (chat template + reasoning-budget sampler). usage: run_cli.py TAG N BUDGET id..."""
import json, os, subprocess, sys, time, re
H=os.path.expanduser("~"); D=f"{H}/boar/kiln/lesport-think"; OUT=f"{D}/out"
GGUF=f"{H}/boar/shared-models/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf"
BIN=f"{H}/boar/spikes/llama-omni/src/build-cpu/bin/llama-cli"; EXP=f"{H}/boar/spikes/llama-omni/experts"
tag,n,bud=sys.argv[1:4]; ids=sys.argv[4:]
env=dict(os.environ, LLAMA_MOE_LOOKAHEAD_PREFETCH="1")
for key in ids:
    sysm=open(f"{D}/msgs/{key}.sys").read(); usr=open(f"{D}/msgs/{key}.usr").read()
    cmd=["/usr/bin/time","-l",BIN,"-m",GGUF,"--moe-experts",EXP,"--moe-slot-bank","1280","--no-mmap","-t","4","-c","4096","--temp","0.7","--top-k","40","--top-p","0.95","--min-p","0.05","--seed","42","-n",n,
         "--jinja","-st","--simple-io","--no-display-prompt","--reasoning","on","--reasoning-format","none","-sys",sysm,"-p",usr]
    if bud!="-1": cmd+=["--reasoning-budget",bud,"--reasoning-budget-message","\nI have thought enough; answering now.\n"]
    t0=time.time(); r=subprocess.run(cmd,capture_output=True,env=env,timeout=1500,stdin=subprocess.DEVNULL); w=time.time()-t0
    txt=r.stdout.decode("utf-8","replace"); err=r.stderr.decode("utf-8","replace")
    open(f"{OUT}/{tag}-{key}.raw.txt","w").write(txt); open(f"{OUT}/{tag}-{key}.err","w").write(err)
    print(key,"rc",r.returncode,"wall",round(w,1),repr(txt[:80]),flush=True)
