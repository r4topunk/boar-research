import json,re,collections
rd=lambda f:[json.loads(l) for l in open(f) if l.strip()]
C=json.load(open('classes.json')); FC=json.load(open('factchunks.json'))
H={r['id']:r for r in rd('hk3.jsonl')}
TOP={'firstaid-en-002':'CPR compression depth, rate, ratio','firstaid-en-003':'twisted ankle, possibly broken','firstaid-en-004':'why not rewarm hypothermia fast','firstaid-en-005':'object stuck in eye','firstaid-en-006':'injured person on busy road','firstaid-en-008':'confused climber at altitude','firstaid-en-009':'dragging crash victim from car','firstaid-en-011':'dirty bomb, outdoors, what to do','firstaid-en-012':'electric fans in heat wave','firstaid-en-013':'safe campfire spot survival','firstaid-en-014':'warming center, who can use','firstaid-en-015':'expedition mental health safety','firstaid-en-016':'slow sand filter, role of sand','firstaid-en-018':'sunlight disinfects bottle water','firstaid-en-020':'ventilated pit latrine design rules',
'medlineplus-en-003':'vitamin D units for adults','medlineplus-en-006':'elderly patient sudden confusion causes','medlineplus-en-007':'Zika risk when pregnant travelling','medlineplus-en-008':'high blood sugar warning signs','medlineplus-en-009':'radon risk and home testing','medlineplus-en-010':'antibiotics, diarrhea, fever, C. diff','medlineplus-en-011':'shaking hand tremor types, causes','medlineplus-en-014':'cataract risk factors, symptoms','medlineplus-en-017':'stomach bug, when to call','medlineplus-en-018':'PSA test limits, prostate cancer','medlineplus-en-019':'winter storm car kit','medlineplus-en-020':'vaccine side effects, autism link'}
def pk(c): 
    m=re.match(r'pack:local-(.+):\d+$',c); return (m[1] if m else 'wiki-vital5').replace('boar-','').replace('-en','')
rows=[]; CL={}
for i,v in C.items():
    if v['cls']=='OK': continue
    r=H[i]; codes=r['reasonCodes']; short=i.replace('st-boar-','').replace('st-','')
    cv=lambda k:[x for c in codes if c.startswith('HK:'+k+':') for x in c[len('HK:'+k+':'):].split('|') if x]
    pn=re.search(r'detector:p=([\d.]+)',' '.join(codes)); p=pn[1] if pn else '-'
    topic=','.join(v['topic']) if v['topic'] is not None else 'n/a (not health)'
    if v['topic']==[]: topic='EMPTY'
    # dropped by
    d=[]
    m=re.search(r'grounding:(?:health-)?off-topic-dropped-(\d+)',' '.join(codes))
    kind='H-STRICT' if v['health'] else 'GENERIC'
    if m: 
        cnt=collections.Counter(pk(c) for c in cv('drop')) if v['health'] else None
        d.append(f"{kind} off-topic -{m[1]}"+(' ('+', '.join(f'{n} {p_}' for p_,n in cnt.items())+')' if cnt else ''))
    m=re.search(r'headpass:health-dropped-(\d+)',' '.join(codes)); 
    if m: d.append(f"X1-neighbour health -{m[1]}")
    m=re.search(r'headpass:dense:health-dropped-(\d+)',' '.join(codes)); 
    if m: d.append(f"dense-append health -{m[1]}")
    m=re.search(r'headpass:selead:health-dropped-(\d+)',' '.join(codes)); 
    if m: d.append(f"SE-lead health -{m[1]}")
    nb=len(re.findall(r'headpass:budget:dropped:',' '.join(codes)))
    if nb: d.append(f"X2b dropped -{nb}")
    if 'grounding:health-no-source' in codes: d.append('=> health-no-source (decline)')
    fi=v['fact_in']; where=[]
    if fi['raw']:
        sc=[c['score'] for c in r['rawFull'] if c['chunkId'] in fi['raw']][0]; rk=[k+1 for k,c in enumerate(r['rawFull']) if c['chunkId'] in fi['raw']][0]; where.append(f"raw #{rk} (score {sc})")
    elif fi['wide']: where.append(f"wide #{v['wr'][0]}")
    if v['rank']: where.append(f"dense rank {v['rank'][0]}/{len(r['reasonCodes']) and len([c for c in codes if c.startswith('HK:densecand:')][0][len('HK:densecand:'):].split('|'))}")
    if fi['app']: where.append('appended')
    if fi['bud']: where.append('budget-dropped')
    if not where: where.append('never retrieved')
    own='own art. '+('raw' if v['own_raw'] else 'wide' if v['own_wide'] else 'absent')+('+kept' if v['own_kept'] else '')
    cls=v['cls']
    if cls=='C2' and v['rank'] and v['rank'][0]<=12 and v['picks_other']>=1: cls='D'
    rows.append((short,TOP.get(short,''),f"{p}{'F' if v['fire'] else ''}",topic,v['nkept'],'; '.join(where),own,'; '.join(d),cls,v['picks_other'],v['raw_other'],len(r['rawFull'])))
for r in rows: print('| '+' | '.join(map(str,r[:9]))+' |'); CL[r[0].split('-')[0]+'/'+r[8]]=CL.get(r[0].split('-')[0]+'/'+r[8],0)+1
print()
cnt=collections.Counter(); 
for i,v in C.items():
    if v['cls']!='OK': cnt[(i.split('-')[1],v['cls'])]+=1
print(cnt)
print('crowd (raw all other pack) among misses:',sum(1 for r in rows if r[10]==r[11]),'of',len(rows))

print(sorted(CL.items()))
