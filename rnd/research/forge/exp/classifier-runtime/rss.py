import subprocess, resource, sys, re
for args in [["-b","512","-ub","512"],["-b","64","-ub","64"],["-b","64","-ub","64","-np","1"],["-b","512","-ub","512","-np","8"]]:
  for m in ["mmbert-small-cls-q8_0.gguf","<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf"]:
    before=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    out=subprocess.run(["llama.cpp/build/bin/llama-embedding","-m",m,"-p","Meu filho foi picado por um escorpião","-c","512","-t","2","--pooling","mean","-lv","4"]+args,capture_output=True,text=True).stderr
    ob=re.findall(r"output buffer size =\s*([\d.]+) MiB",out); nseq=re.findall(r"n_seq_max\s*=\s*(\d+)",out)
    print(m.split('/')[-1][:12], args, "n_seq_max",nseq, "output MiB",ob)
