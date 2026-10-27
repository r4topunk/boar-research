import json,sys
D='<workspace>/rnd/research/coordinator/arms/topics27/replay/'
L=lambda n:{json.loads(l)['id']:json.loads(l) for l in open(D+f'misses.{n}.jsonl')}
EXP={'b13':['Mosquito-borne disease','Mosquito'],'b15':['Kyoto','Heian-kyō'],'b19':['AC power plugs and sockets','Mains electricity'],'b20':['Japan','Germany','Population density','Population ageing']}
OTHER='q1 q2 q4 q7 q8 q9 b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 b14 b16 b17 b18 b21'.split()
HEALTH='q2 q4 b2 b8 b13 b14 b21'.split()
A0=L('A0'); res={}
off=L('A1off'); print('A1off identity raw/kept/codes', sum([r['title'] for r in A0[i]['raw']]==[r['title'] for r in off[i]['raw']] for i in A0), sum(A0[i]['sources']==off[i]['sources'] for i in A0), sum(A0[i]['reasonCodes']==off[i]['reasonCodes'] for i in A0))
for arm in ['A0','A1','A1d']:
  X=L(arm)
  rec={k:[t for t in v if t in X[k]['sources']] for k,v in EXP.items()}
  ch=[i for i in OTHER if X[i]['sources']!=A0[i]['sources']]
  hl={i:[t for t in A0[i]['sources'] if t not in X[i]['sources']] for i in HEALTH}
  hl={i:v for i,v in hl.items() if v}
  n=sum(bool(v) for v in rec.values())
  ok= n>=2 and len(ch)<=2 and not hl
  res[arm]=dict(recovered=rec,n=n,changed=ch,healthLoss=hl,fix=ok)
  print(arm,'recovered',n,rec,'changed',ch,'healthLoss',hl,'FIX' if ok else 'no')
  for i in ch: print('   ',i,A0[i]['sources'],'->',X[i]['sources'],[c for c in X[i]['reasonCodes'] if 'noproper' in c])
for arm in ['A1','A1d']:
  X=L(arm); print(arm,'reason-code noproper fired on',[i for i in X if any('noproper' in c for c in X[i]['reasonCodes'])])
for arm in ['D1base','D1sefix']:
  X=L(arm)
  for i,r in X.items(): print(arm,i,r['task'],r['tier'],[(x['title'],x['similarity']) for x in r['raw']],'K:',r['sources'],[c for c in r['reasonCodes'] if c.startswith(('grounding','context','answer','instant:off','task'))])
json.dump(res,open(D+'misses.score.json','w'),indent=1,ensure_ascii=False)
