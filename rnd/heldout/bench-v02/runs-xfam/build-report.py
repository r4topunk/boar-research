#!/usr/bin/env python3
"""v0.2 adaptation of the copied XFAM reporter; emits aggregate numbers and IDs only."""
import json, math, sys
from pathlib import Path
ROOT=Path('<workspace>')
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'boar-eval'))
from harness.report import build
from harness.common import pair_scores
from scorers.score import judge_pairs
from scorers.bench import Bench
from scorers import stats
OUT=ROOT/'blind/bench-v02/runs-xfam'
CFG=json.loads((OUT/'run-config.json').read_text())
class V02Bench(Bench):
    def _first(self,*names):
        found=super()._first(*names)
        if found:return found
        manifest=self.dir/'refs/MANIFEST.json'
        if manifest.exists():
            q=self.dir/json.loads(manifest.read_text())['questions_file']
            if q.exists():return q
        return None
BENCH=V02Bench(CFG['bench'],refs=CFG['refs'])
RUNS={'K':[('runs-cut6','cut6-v02-s42'),('runs-cut6','cut6-v02-s43')], 'H':[('runs-dt512v02','dhv-H-v02-s42')]}

def ranks(xs):
    order=sorted(range(len(xs)),key=lambda i:xs[i]); result=[0.0]*len(xs); start=0
    while start<len(xs):
        end=start+1
        while end<len(xs) and xs[order[end]]==xs[order[start]]:end+=1
        for k in range(start,end):result[order[k]]=(start+end-1)/2+1
        start=end
    return result

def spearman(xs,ys):
    a,b=ranks(xs),ranks(ys); ma,mb=stats.mean(a),stats.mean(b)
    den=math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))
    return sum((x-ma)*(y-mb) for x,y in zip(a,b))/den if den else None

def mean_runs(runs):
    ids=list(runs[0]); assert all(set(r)==set(ids) for r in runs)
    return {i:tuple(stats.mean(r[i][j] for r in runs) for j in range(2)) for i in ids}

def row(values):return '| '+' | '.join(str(v) if isinstance(v,(str,int)) else f'{v:.6f}' for v in values)+' |'

def nums(values):return ' '.join(str(v) if isinstance(v,int) else f'{v:.6f}' for v in values)

D={}; lines=['| arm | judge | runs | n | raw | lo95 | hi95 | floor_adj | lo95 | hi95 |','|---|---|---|---|---|---|---|---|---|---|']
for arm,runs in RUNS.items():
    for judge in ['Codex','Claude']:
        traces=[ROOT/'blind/bench-v02'/folder/(name+'.traces.jsonl') for folder,name in runs]
        judgments=[OUT/(name+'.codex.judgments.jsonl') if judge=='Codex' else ROOT/'blind/bench-v02'/folder/(name+'.judgments.jsonl') for folder,name in runs]
        for t,j in zip(traces,judgments):
            rows=[json.loads(l) for l in j.read_text().splitlines() if l.strip()]
            assert len({(r['queryId'],r['order']) for r in rows if r.get('ok')})==220
        report=build(traces[0],BENCH,judgments=judgments[0],repeats=traces[1:],repeat_judgments=judgments[1:],seed=11)
        ids=[q['id'] for q in BENCH.items_for(report['_traces'])]
        pairs=[judge_pairs(j,ids,11) for j in judgments]; scores=[pair_scores(p) for p in pairs]
        assert all(len(s)==110 for s in scores)
        raw=stats.two_level_ratio(scores,seed=11,n=2000)
        adjusted=stats.two_level_ratio([stats.floor_adjust(s) for s in scores],seed=11,n=2000)
        assert abs(raw['ratio']-report['run_budget']['two_level']['ratio'])<1e-12
        fa=report['floor_adjusted']['pooled'] or report['floor_adjusted']['run1']
        assert abs(adjusted['ratio']-fa['ratio'])<1e-12
        winners=[p['winner'] for result in pairs for p in result['pairs']]
        wtl=[sum(w==v for w in winners)/len(winners) for v in ['boar','tie','ref']]
        D[arm,judge]={'raw':raw,'adj':adjusted,'wtl':wtl,'wtl_counts':[sum(w==v for w in winners) for v in ['boar','tie','ref']],'n_pairs':len(winners),'scores':mean_runs(scores),'runs':scores}
        lines.append(row([arm,judge,len(scores),110,raw['ratio'],*raw['ci95'],adjusted['ratio'],*adjusted['ci95']]))
lines+=['','| judge | n | H-K_raw | lo95 | hi95 | H-K_floor_adj | lo95 | hi95 | resamples | seed |','|---|---|---|---|---|---|---|---|---|---|']
DELTA={}
for judge in ['Codex','Claude']:
    k,h=D['K',judge]['scores'],D['H',judge]['scores']
    a=stats.paired_ratio_diff(k,h,seed=1,n=2000)
    b=stats.paired_ratio_diff(stats.floor_adjust(k),stats.floor_adjust(h),seed=1,n=2000)
    DELTA[judge]=(a,b)
    lines.append(row([judge,a['n'],a['diff'],*a['diff_ci95'],b['diff'],*b['diff_ci95'],2000,1]))
lines+=['','| arm | judge | n_pairs | win_n | tie_n | loss_n | win | tie | loss |','|---|---|---|---|---|---|---|---|---|']
for arm in RUNS:
    for judge in ['Codex','Claude']:lines.append(row([arm,judge,D[arm,judge]['n_pairs'],*D[arm,judge]['wtl_counts'],*D[arm,judge]['wtl']]))
lines+=['','| arm | n | Spearman_score | Spearman_ratio | offset_raw | offset_floor_adj | Vpara_raw | Vpara_floor_adj | offset_change_raw | offset_change_floor_adj |','|---|---|---|---|---|---|---|---|---|---|']
CORR={}
for arm,prior in [('K',(0.084,0.100)),('H',(0.115,0.141))]:
    a,b=D[arm,'Codex']['scores'],D[arm,'Claude']['scores']; ids=list(a); assert set(a)==set(b)
    rho=spearman([a[i][0] for i in ids],[b[i][0] for i in ids]); rr=spearman([a[i][0]/a[i][1] for i in ids],[b[i][0]/b[i][1] for i in ids])
    offsets=[D[arm,'Codex'][m]['ratio']-D[arm,'Claude'][m]['ratio'] for m in ['raw','adj']]
    CORR[arm]=[rho,rr,*offsets,*prior,offsets[0]-prior[0],offsets[1]-prior[1]]
    lines.append(row([arm,110,*CORR[arm]]))
lines+=['',row(['offset_comparison','K',*CORR['K'][2:],'H',*CORR['H'][2:]])]
lines+=['','| arm | id | Codex_score | Claude_score | Codex_ref | Claude_ref |','|---|---|---|---|---|---|']
for arm in RUNS:
    for i,(b,r) in D[arm,'Codex']['scores'].items():
        cb,cr=D[arm,'Claude']['scores'][i]; lines.append(row([arm,i,b,cb,r,cr]))
summary=[]
for arm in ['K','H']:
    for judge in ['Codex','Claude']:
        d=D[arm,judge]; summary.append(nums([d['raw']['ratio'],*d['raw']['ci95'],d['adj']['ratio'],*d['adj']['ci95']]))
for judge in ['Codex','Claude']:
    a,b=DELTA[judge];summary.append(nums([a['diff'],*a['diff_ci95'],b['diff'],*b['diff_ci95']]))
for arm in ['K','H']:summary.append(nums([*D[arm,'Codex']['wtl'],*D[arm,'Claude']['wtl']]))
for arm in ['K','H']:summary.append(nums(CORR[arm]))
assert len(summary)==10
(OUT/'XFAM-V02-REPORT.md').write_text('\n'.join(lines)+'\n')
(OUT/'summary-10.txt').write_text('\n'.join(summary)+'\n')
(OUT/'summary-key.txt').write_text('1 K Codex; 2 K Claude; 3 H Codex; 4 H Claude: raw, CI95 low/high, floor-adjusted, CI95 low/high.\n5 Codex; 6 Claude: paired H-K raw, CI95 low/high, floor-adjusted, CI95 low/high (2000 item resamples, seed 1; K averaged over seeds).\n7 K; 8 H: Codex win/tie/loss rates, Claude win/tie/loss rates (both orders combined, pooled seeds).\n9 K; 10 H: Spearman BOAR score, Spearman BOAR/reference ratio, Codex-Claude raw/floor-adjusted offsets, V-para raw/floor-adjusted offsets, v0.2-minus-V-para raw/floor-adjusted offset changes.\nArm CIs: two-level item/run bootstrap, 2000 resamples, seed 11; K 2 seeds, H 1 seed; each run 110 items, 2 orders.\n')
