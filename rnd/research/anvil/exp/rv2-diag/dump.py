import json,sys,statistics as st
K="<workspace>/boar-eval/runs/kiln/rv2-l1/"
def tr(f): return {json.loads(l)['itemId']:json.loads(l) for l in open(K+f)}
RT={s:tr(f'rv2l1-R-{s}.traces.jsonl') for s in ('s42','s43')}; AT=tr('rv2l1-A-s43.traces.jsonl')
def jud(f):
    d={}
    for l in open(K+f):
        r=json.loads(l)
        if r.get('ok'): d.setdefault(r['queryId'],[]).append(r)
    return d
RJ={s:jud(f'rv2l1-R-{s}.v01.judgments.jsonl') for s in ('s42','s43')}; AJ=jud('rv2l1-A-s43.v01.judgments.jsonl')
rub=lambda d: st.mean([d['correctness'],d['completeness'],d['usefulness']])
def sc(js): return f"{st.mean(rub(r['mapped']['boar']) for r in js):.2f}/c{st.mean(r['mapped']['boar']['correctness'] for r in js):.1f}" if js else '-'
for i in sys.argv[1].split(','):
    t=RT['s42'][i]; print(f"######## {i}: {t['question']}")
    print(f"A s43 [{sc(AJ.get(i,[]))}]: {AT[i]['answer']['text'][:330]!r}")
    for s in ('s42','s43'):
        tt=RT[s][i]; src=[e for e in tt['events'] if e['type']=='sources' and any('text' in x for x in e['sources'])]
        print(f"R {s} [{sc(RJ[s].get(i,[]))}] codes={[c for c in tt['route']['reasonCodes'] if c.startswith(('context','grounding:uncited','grounding:health','citations'))]}: {tt['answer']['text'][:330]!r}")
    src=[e for e in RT['s42'][i]['events'] if e['type']=='sources' and any('text' in x for x in e['sources'])]
    if src:
        for x in src[-1]['sources'][:5]: print(f"   SAW[{x['title'][:40]}]: {x.get('text','')[:170]!r}")
    rj=RJ['s42'].get(i,[])
    if rj: print("   JUDGE R s42:", (rj[0]['verdict'].get('rationale') or '')[:260])
    print()
