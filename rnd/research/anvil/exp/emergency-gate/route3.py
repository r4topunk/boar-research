import json,sys
rows=[json.loads(l) for l in open(sys.argv[1])]
for st in ['v0','v01']:
    R=[r for r in rows if r['set']==st and r['route']!='EITHER']
    wrong=[];fs=ms=0
    for r in R:
        srch=(r['pS']+r['pE'])>=r['pA']
        if srch!=(r['route']=='SEARCH'):
            wrong.append(f"{r['id']}:{r['pA']:.2f}"); 
            if r['route']=='SEARCH': ms+=1
            else: fs+=1
    print(st,f"{len(R)-len(wrong)}/{len(R)} false-search {fs} missed {ms}",' '.join(wrong))
    em=[r['id'] for r in rows if r['set']==st and r['pE']/(r['pE']+r['pS']+r['pA'])>=0.5]
    print('  EMERGENCY fired on',len(em),em[:12])
