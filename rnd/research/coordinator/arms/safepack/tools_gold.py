import json, sys
Q={json.loads(l)['id']:json.loads(l) for l in open('boar-eval/bench/selftest/safepack/questions.jsonl')}
for f in sys.argv[1:]:
    R=[json.loads(l) for l in open(f)]; s=dict(n=len(R), raw_empty=0, gold_raw=0, gold_src=0, any_readygov_raw=0)
    for r in R:
        g=Q[r['id']]['selftest']['source']['title'].replace(' (Ready.gov)','').lower(); raw=[x['title'].lower() for x in r.get('raw',[])]; src=[x.lower() for x in r.get('sources',[])]
        s['raw_empty']+=not raw; s['gold_raw']+=any(g in x for x in raw); s['gold_src']+=any(g in x for x in src); s['any_readygov_raw']+=any('ready.gov' in x or 'us army' in x for x in raw)
    print(f.rsplit('/',1)[-1], s)
