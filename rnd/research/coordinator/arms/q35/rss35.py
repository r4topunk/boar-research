import subprocess, sys, json, time, urllib.request, resource, os, signal
gguf=os.path.expanduser(sys.argv[1]); B=os.path.expanduser("<runner>/spikes/llama-b11010/build-cpu/bin/llama-server")
srv=subprocess.Popen([B,"-m",gguf,"--port","18441","-t","4","-c","4096","-np","1","--jinja","--no-webui"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
import threading
peak=[0]; stop=[False]
def poll():
    while not stop[0]:
        o=subprocess.run(["ps","-axo","rss=,command="],capture_output=True,text=True).stdout
        t=sum(int(l.split(None,1)[0]) for l in o.splitlines() if "llama-server" in l and "18441" in l)
        peak[0]=max(peak[0],t); time.sleep(0.3)
threading.Thread(target=poll,daemon=True).start()
base="http://127.0.0.1:18441"
for _ in range(300):
    try:
        if json.load(urllib.request.urlopen(base+"/health",timeout=2)).get("status")=="ok": break
    except Exception: time.sleep(1)
words=open(os.path.expanduser("<runner>/anvil-outofkit/anchors.mjs")).read().split()
txt=" ".join((words*40)[:int(os.environ.get("NW","1700"))])
body={"messages":[{"role":"user","content":"Summarize the following text in detail.\n"+txt}],"max_tokens":300,"temperature":0.7,"seed":1,"cache_prompt":False,"chat_template_kwargs":{"enable_thinking":False}}
try:
    r=json.load(urllib.request.urlopen(urllib.request.Request(base+"/v1/chat/completions",data=json.dumps(body).encode(),headers={"content-type":"application/json"}),timeout=900))
except urllib.error.HTTPError as e:
    print("HTTP",e.code,e.read()[:300]); srv.terminate(); sys.exit(1)
print(os.path.basename(gguf),"prompt",r["usage"]["prompt_tokens"],"out",r["usage"]["completion_tokens"],"decode",r.get("timings",{}).get("predicted_per_second"))
srv.send_signal(signal.SIGTERM); srv.wait(timeout=60)
stop[0]=True; print("peak RSS (ps, sum of llama-server procs) GiB %.3f"%(peak[0]/2**20))
