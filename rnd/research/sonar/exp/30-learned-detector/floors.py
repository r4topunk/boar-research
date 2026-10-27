"""Engine-route health predicate variants (offline): V0 = det | isCardEmergency | followUp (health11 as frozen);
V1 = det | single card condition (conversationCondition) | followUp; V2 = det | health9 lexical (isHealthQuestion | followUp | isCardEmergency).
usage: floors.py <compass gguf scores json> <sonar gguf scores json> <thr>"""
import json, sys, numpy as np
from eval_compass import D
yc=np.array([d['emergency'] for d in D]); hw=np.array([d['howto'] for d in D]); strict=(yc==0)&(hw==0); crit=np.array([d.get('sev')=='critical' for d in D])
L=[json.loads(l) for l in open('dev/labels.sonar.jsonl')]; P=json.load(open('dev/pool.raw.json'))
ys=np.array([x['label'] for x in L]); hn=np.array([x['cls']=='hard_negative' for x in L]); real=np.array([p['src']!='firstaidqa' for p in P])
def parts(f):
    x=json.load(open(f)); g=lambda k: np.array([bool(v[k]) for v in x]); return g('hq'), g('fu'), g('card'), np.array([v['cond'] is not None for v in x])
cq,cf,cc,ccond=parts('compassdev/lexical.h9.json'); sq,sf,sc,scond=parts('dev/lexical.h9.parts.json')
cs=np.array(json.load(open(sys.argv[1]))['gguf']); ss=np.array(json.load(open(sys.argv[2]))['gguf']); t=float(sys.argv[3])
for name,pc,ps in (('V0 det|cardEmergency|fu',(cs>=t)|cc|cf,(ss>=t)|sc|sf),('V1 det|cardCondition|fu',(cs>=t)|ccond|cf,(ss>=t)|scond|sf),('V2 det|health9 lexical',(cs>=t)|cq|cf|cc,(ss>=t)|sq|sf|sc),('lexical health9 alone',cq|cf|cc,sq|sf|sc)):
    print(f"{name:26s} Compass rec {(pc&(yc==1)).sum()}/180 strictFF {(pc&strict).sum()}/100 howto {(pc&(hw==1)).sum()}/20 critMiss {(~pc&crit&(yc==1)).sum()} | Sonar realistic rec {(ps&(ys==1)&real).sum()}/246 FF {(ps&(ys==0)&real).sum()}/457 hardneg {(ps&hn).sum()}/57 | all-dev FF {(ps&(ys==0)).sum()}/490")
