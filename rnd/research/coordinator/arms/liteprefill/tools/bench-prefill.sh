#!/bin/bash
# LITEPREFILL-DESKTOP: 0-call prefill/decode measurement, CPU build, -t 4. Output: raw/*.json + items.csv + summary.txt
set -u
B=<scratch>
ROOT=<workspace>
A=$ROOT/rnd/research/coordinator/arms/liteprefill
PORT=8181
cd "$A" || exit 1
mkdir -p raw
log(){ echo "$(date '+%H:%M:%S') $*" | tee -a raw/run.log; }
# 1. idle rule
t0=$(date +%s)
while :; do
  L=$(sysctl -n vm.loadavg | awk '{print $2}')
  if awk "BEGIN{exit !($L < 4.0)}"; then break; fi
  if [ $(( $(date +%s) - t0 )) -ge 2700 ]; then log "NOT RUN (load $L >= 4.0 for 45 min)"; echo "not run (load)" > summary.txt; exit 2; fi
  sleep 60
done
log "start load=$L free=$(df -g / | tail -1 | awk '{print $4}')G others=$(pgrep -fl 'llama-server' | grep -v 8094 | wc -l | tr -d ' ')"
# 2. prompts: cut BOUNTY_31.md to ~450 and ~850 tokens (4 chars/token approx), 5 offsets each
python3 - <<'PY'
import json,re
t=open('<workspace>/BOUNTY_31.md').read()
t=re.sub(r'\s+',' ',t)
ps=[]
for L,chars in (('s',1800),('l',3400)):
    for i in range(5):
        off=(i*700)%max(1,len(t)-chars)
        ps.append({'id':f'{L}{i}','prompt':'Summarize the following text in two sentences.\n\n'+t[off:off+chars]+'\n\nSummary:'})
json.dump(ps,open('raw/prompts.json','w'))
print('prompts',len(ps),'text chars',len(t))
PY
echo "model,item,prompt_n,prompt_ms,pp_tok_s,predicted_n,predicted_ms,tg_tok_s" > items.csv
for M in "4b:$ROOT/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf" "1.7b:$ROOT/shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf"; do
  name=${M%%:*}; path=${M#*:}
  log "server $name"
  "$B/llama-server" -m "$path" -t 4 -c 4096 -np 1 --host 127.0.0.1 --port $PORT > raw/server-$name.log 2>&1 &
  SP=$!
  ok=0; for i in $(seq 1 60); do sleep 2; curl -sf http://127.0.0.1:$PORT/health >/dev/null && { ok=1; break; }; done
  if [ $ok = 0 ]; then log "FAIL health $name"; kill $SP; exit 3; fi
  python3 - "$name" $PORT <<'PY'
import json,sys,urllib.request
name,port=sys.argv[1],sys.argv[2]
ps=json.load(open('raw/prompts.json'))
rows=[]
for p in ps:
    body=json.dumps({'prompt':p['prompt'],'n_predict':64,'temperature':0,'cache_prompt':False}).encode()
    req=urllib.request.Request(f'http://127.0.0.1:{port}/completion',data=body,headers={'Content-Type':'application/json'})
    r=json.load(urllib.request.urlopen(req,timeout=600))
    t=r['timings']
    open(f"raw/{name}-{p['id']}.json",'w').write(json.dumps(r)[:20000])
    rows.append((name,p['id'],t['prompt_n'],t['prompt_ms'],t['prompt_per_second'],t['predicted_n'],t['predicted_ms'],t['predicted_per_second']))
    print(name,p['id'],'pp',round(t['prompt_per_second'],1),'tg',round(t['predicted_per_second'],2),flush=True)
with open('items.csv','a') as f:
    for r in rows: f.write(','.join(str(x) for x in r)+'\n')
PY
  kill $SP; wait $SP 2>/dev/null; sleep 3
done
python3 - <<'PY'
import csv,statistics as st
rows=list(csv.DictReader(open('items.csv')))
def med(m,L,k): return st.median(float(r[k]) for r in rows if r['model']==m and r['item'].startswith(L))
out=['model length pp_tok_s tg_tok_s prompt_n']
for m in ('4b','1.7b'):
    for L in ('s','l'):
        out.append(f"{m} {L} {med(m,L,'pp_tok_s'):.1f} {med(m,L,'tg_tok_s'):.2f} {med(m,L,'prompt_n'):.0f}")
rp=[med('1.7b',L,'pp_tok_s')/med('4b',L,'pp_tok_s') for L in ('s','l')]
rt=[med('1.7b',L,'tg_tok_s')/med('4b',L,'tg_tok_s') for L in ('s','l')]
out.append(f"pp_ratio_1.7b/4b s={rp[0]:.2f} l={rp[1]:.2f}; tg_ratio s={rt[0]:.2f} l={rt[1]:.2f}")
out.append(f"projected X2b TTFT on the POCO: 4B +8.7 s; 1.7B +{413/(47.6*rp[1]):.1f} s (pp ratio {rp[1]:.2f} on the long prompts)")
open('summary.txt','w').write('\n'.join(out)+'\n'); print('\n'.join(out))
PY
log "done"
