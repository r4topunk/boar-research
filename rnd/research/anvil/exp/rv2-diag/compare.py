"""rv2 (R) vs bounty1 (A) vs Anvil Q450 oracle contexts, item by item (v0.1 EN). Output: rows.jsonl + summary."""
import json, re, statistics as st, collections, os
K="<workspace>/boar-eval/runs/kiln/rv2-l1/"; O="<workspace>/rnd/research/anvil/exp/oracle/"
H=os.path.dirname(os.path.abspath(__file__))
rub=lambda d: st.mean([d['correctness'],d['completeness'],d['usefulness']])
def judged(files):
    per={}
    for f in files:
        for l in open(f):
            r=json.loads(l)
            if r.get('ok'): per.setdefault(r['queryId'],[]).append(r['mapped'])
    return {i:(st.mean(rub(m['boar']) for m in v), st.mean(rub(m['ref']) for m in v)) for i,v in per.items()}
A=judged([K+'rv2l1-A-s42.v01.judgments.jsonl',K+'rv2l1-A-s43.v01.judgments.jsonl']) if os.path.exists(K+'rv2l1-A-s42.v01.judgments.jsonl') else judged([K+'rv2l1-A-s43.v01.judgments.jsonl'])
R=judged([K+'rv2l1-R-s42.v01.judgments.jsonl',K+'rv2l1-R-s43.v01.judgments.jsonl'])
Q=judged([O+'runs/qwen3-4b-Q450.judgments.jsonl'])
gold=collections.defaultdict(set)
for l in open(O+'articles.jsonl'):
    a=json.loads(l)
    if a['kind']=='wiki': gold[a['id']].add(a['title'].lower())
qctx={json.loads(l)['id']:json.loads(l) for l in open(O+'ctx-Q450.jsonl')}
def traces(f): return {json.loads(l)['itemId']:json.loads(l) for l in open(f)}
RT=traces(K+'rv2l1-R-s42.v01.traces.jsonl')
rows=[]
for i,t in RT.items():
    if i not in R or i not in Q: continue
    src=next((e['sources'] for e in t['events'] if e['type']=='sources'),[])
    titles=[s['title'] for s in src]
    norm=lambda x: re.sub(r'^(wikivoyage|wikipedia):\s*','',x.lower()).strip()
    g=gold.get(i,set())
    isg=[norm(x) in g for x in titles]
    ctxcode=next((c for c in t['route']['reasonCodes'] if c.startswith('context:')),'')
    m=re.search(r'-(\d+)w$',ctxcode) or re.search(r'->(\d+)$',ctxcode)
    words=int(m.group(1)) if m and ctxcode.endswith('w') else (int(m.group(1))*0.75 if m else 0)
    gc=[c for c in t['route']['reasonCodes'] if c.startswith(('grounding:','citations:','instant:'))]
    q=qctx[i]
    rows.append({'id':i,'A':round(A[i][0]/A[i][1],3) if i in A else None,'R':round(R[i][0]/R[i][1],3),'Q450':round(Q[i][0]/Q[i][1],3),
      'R_titles':titles,'R_gold_any':any(isg),'R_gold_share':round(sum(isg)/len(isg),2) if isg else 0,'R_first_gold_rank':(isg.index(True)+1) if any(isg) else None,
      'R_ctx':ctxcode,'R_ctx_words':round(words),'R_codes':gc,'has_gold_articles':bool(g),
      'Q_titles':[p['title'] for p in q['passages']],'Q_words':sum(len(p['text'].split()) for p in q['passages']),'Q_topsim':q['passages'][0]['sim'] if q['passages'] else None})
with open(H+'/rows.jsonl','w') as f:
    for r in rows: f.write(json.dumps(r)+'\n')
n=len(rows); wg=[r for r in rows if r['has_gold_articles']]
print('items',n,'with gold wiki articles',len(wg))
print('ratio mean A %.3f R %.3f Q450 %.3f'%(st.mean(r['A'] for r in rows if r['A'] is not None),st.mean(r['R'] for r in rows),st.mean(r['Q450'] for r in rows)))
print('R context: gold article among sources %d/%d; gold share p50 %.2f; first-gold-rank dist %s'%(sum(r['R_gold_any'] for r in wg),len(wg),st.median(r['R_gold_share'] for r in wg),collections.Counter(r['R_first_gold_rank'] for r in wg)))
print('R ctx words p50 %d (Q450 %d)'%(st.median(r['R_ctx_words'] for r in rows),st.median(r['Q_words'] for r in rows)))
print('R ctx codes',collections.Counter(re.sub(r'\d+','N',r['R_ctx']) for r in rows).most_common(6))
print('R grounding codes',collections.Counter(c for r in rows for c in r['R_codes'] if not c.startswith('grounding:off-topic')).most_common(10))
# where Q450 beats R by >=0.2
big=[r for r in rows if r['Q450']-r['R']>=0.2]; print('Q450 >= R+0.2 on',len(big),'items; R had gold article on',sum(r['R_gold_any'] for r in big))
for r in sorted(big,key=lambda r:r['R']-r['Q450'])[:12]: print(f"  {r['id']:13} R {r['R']:.2f} Q {r['Q450']:.2f} A {r['A']} goldR={r['R_gold_any']} share={r['R_gold_share']} ctx={r['R_ctx']} codes={[c for c in r['R_codes'] if 'off-topic' not in c][:3]} R_titles={r['R_titles'][:4]}")
