#!/usr/bin/env python3
"""Local XFAM analysis. Never writes question, answer, reference, or rationale text to reports."""
from pathlib import Path
import sys,json,math,hashlib,subprocess,contextlib,io
ROOT=Path('<workspace>'); REPO=ROOT/'boar-eval'; BENCH=ROOT/'blind/vitalik-para1'; OUT=BENCH/'runs-xfam'
sys.path.insert(0,str(REPO))
from harness import report
from harness.common import pair_scores
from scorers.bench import Bench
from scorers.score import judge_pairs
from scorers import stats


class XfamBench(Bench):
 def _first(self,*names):
  found=super()._first(*names)
  return found or ((self.dir/'items.jsonl') if (self.dir/'items.jsonl').exists() else None)
 def items_for(self,trace_ids):
  return [q for q in super().items_for(trace_ids) if q.get('grading',{}).get('type')!='venue-list']

ARMS={'K':('runs-cut6','cut6-vpara'),'H':('runs-dt512','dh-H-vpara')}
def jsonl(p):return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ranks(xs):
 xs=[round(v,12) for v in xs]  # Preserve mathematical ties across equivalent rubric averages.
 out=[0.0]*len(xs);order=sorted(range(len(xs)),key=lambda i:xs[i]);i=0
 while i<len(xs):
  j=i+1
  while j<len(xs) and xs[order[j]]==xs[order[i]]:j+=1
  for k in range(i,j):out[order[k]]=(i+j-1)/2+1
  i=j
 return out
def corr(x,y):
 a=ranks(x);b=ranks(y);ma=stats.mean(a);mb=stats.mean(b)
 den=math.sqrt(sum((v-ma)**2 for v in a)*sum((v-mb)**2 for v in b))
 return sum((u-ma)*(v-mb) for u,v in zip(a,b))/den if den else None

def build():
 manifest=json.loads((BENCH/'refs/MANIFEST.json').read_text())
 refs=next(p for p in (BENCH/'refs').glob('*.jsonl') if sha(p)==(manifest.get('refs_jsonl_sha256') or manifest.get('jsonl_sha256')))
 bench=XfamBench(BENCH,refs=refs); ids=[q['id'] for q in bench.questions if q.get('grading',{}).get('type')!='venue-list']; assert len(ids)==51
 results={};input_hashes={}
 for arm,(folder,stem) in ARMS.items():
  traces=[BENCH/folder/f'{stem}-s{s}.traces.jsonl' for s in [42,43]]
  for judge in ['Codex','Claude']:
   js=[OUT/f'{stem}-s{s}.codex.judgments.jsonl' if judge=='Codex' else BENCH/folder/f'{stem}-s{s}.judgments.jsonl' for s in [42,43]]
   for p in [*traces,*js,bench.questions_path,refs]:input_hashes[str(p.resolve().relative_to(BENCH))]=sha(p)
   for n,p in enumerate(js):
    rows=jsonl(p); assert len(rows)==102 and all(r['ok'] for r in rows)
    assert len({(r['queryId'],r['order']) for r in rows})==102
    if judge=='Codex':
     for r in rows:
      assert r['judgeVersion']=='judge.v1-codex' and r['judgeModel']==r['requestedModel']=='gpt-5.6-sol' and r['seed']==7
      assert r['tracesSha256']==sha(traces[n]) and r['questionsSha256']==sha(bench.questions_path) and r['refsSha256']==sha(refs)
      assert r['sampling']=={'temperature':None,'temperatureControl':'unavailable in codex exec','reasoningEffort':'high'}
   # Run the requested reporter CLI with --repeat, retaining stdout privately. Remove
   # its detailed item notes immediately; published per-arm reports contain metrics only.
   raw=OUT/f'.{arm}-{judge}.report.raw.md'
   cmd=[sys.executable,str(Path(__file__).resolve()),'--reporter',str(traces[0]),'--judgments',str(js[0]),'--bench',str(BENCH),'--refs',str(refs),'--repeat',str(traces[1]),'--repeat-judgments',str(js[1]),'--seed','11','--title',f'XFAM {arm} {judge}','--out',str(raw)]
   with (OUT/'reporter.log').open('a') as log:
    p=subprocess.run(cmd,stdout=log,stderr=log)
   assert p.returncode==0,'reporter failed; see private log'
   with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
    rep=report.build(traces[0],bench,js[0],None,[traces[1]],[js[1]],seed=11)
   scored=[judge_pairs(p,ids,11) for p in js]; runs=[pair_scores(s) for s in scored]
   assert all(set(run)==set(ids) for run in runs)
   pooled={i:tuple(stats.mean(run[i][n] for run in runs) for n in [0,1]) for i in ids}
   pairs=[p for s in scored for p in s['pairs']]
   win=sum(p['winner']=='boar' for p in pairs)/len(pairs);tie=sum(p['winner']=='tie' for p in pairs)/len(pairs)
   results[arm,judge]={'raw':rep['run_budget']['two_level'],'floor':rep['floor_adjusted']['pooled'],'win':win,'tie':tie,'loss':1-win-tie,'win_score':win+tie/2,'scores':pooled}
   r=results[arm,judge]
   assert abs(r['raw']['ratio']-stats.ratio(list(pooled.values())))<1e-12
   safe=[f'# XFAM {arm} {judge}','','| Metric | Value | 95% CI |','|---|---|---|',
    f"| Raw ratio | {r['raw']['ratio']:.8f} | {r['raw']['ci95'][0]:.8f}, {r['raw']['ci95'][1]:.8f} |",
    f"| Floor-adjusted ratio | {r['floor']['ratio']:.8f} | {r['floor']['ci95'][0]:.8f}, {r['floor']['ci95'][1]:.8f} |",
    f"| Win / tie / loss | {win:.8f} / {tie:.8f} / {r['loss']:.8f} | |",f"| Win score | {r['win_score']:.8f} | |",'| Items / seeds / orders | 51 / 2 / 2 | |','| Bootstrap seed / resamples | 11 / 2000 | |','']
   (OUT/f'{arm}-{judge}.report.md').write_text('\n'.join(safe));raw.unlink()
 deltas={}
 for judge in ['Codex','Claude']:
  a,b=[results[arm,judge]['scores'] for arm in ['K','H']]
  deltas[judge]={'raw':stats.paired_ratio_diff(a,b,seed=1,n=2000),'floor':stats.paired_ratio_diff(stats.floor_adjust(a),stats.floor_adjust(b),seed=1,n=2000)}
 correlations={arm:{'score':corr([results[arm,'Codex']['scores'][i][0] for i in ids],[results[arm,'Claude']['scores'][i][0] for i in ids]),'ratio':corr([results[arm,'Codex']['scores'][i][0]/results[arm,'Codex']['scores'][i][1] for i in ids],[results[arm,'Claude']['scores'][i][0]/results[arm,'Claude']['scores'][i][1] for i in ids])} for arm in ARMS}
 calls=[r for p in OUT.glob('*.calls.jsonl') for r in jsonl(p)]
 assert sum(r['ok'] for r in calls)==408 and all(r['toolCalls']==0 for r in calls)
 lines=['# XFAM comparison','','Reporter uses an in-memory Bench compatibility subclass for the manifest-based items layout and excludes the seven venue-list items, which are outside the 51-item judge comparison. The original reporter, scorers and inputs remain unchanged. Model: `gpt-5.6-sol`; CLI: `codex-cli 0.144.3`; judge: `judge.v1-codex`. Fixed high reasoning effort; CLI temperature control unavailable. Seed 7 for A/B start order; two generation seeds (42, 43), 51 items, both orders, 408 successful calls. Pilot rows reused. No new answer generation.','',
  'Ratios and their CIs are from unmodified `harness/report.py`, with `--repeat`, seed 11 and 2000 two-level bootstrap resamples. Both orders are combined with the unmodified vendored judge core; scores are averaged and winner disagreement becomes a tie. Two-seed point estimates use per-item seed means. Win rates average the two seed-specific combined-order outcomes; a win scores 1, tie 0.5, loss 0.','',
  'Call audit: one completed CLI attempt was discarded by an adapter false positive that scanned successful output for 429. The classifier was corrected to inspect only failed-call diagnostics (local commit 4c4d379); the missing pair was rerun with identical judging settings. The 408 stored verdicts exclude that discarded attempt. All attempts remain in the call logs.', '',
  '| Arm | Judge | Raw ratio | Raw 95% CI | Floor-adjusted ratio | Floor 95% CI | Win rate | Tie rate | Loss rate | Win score |',
  '|---|---|---|---|---|---|---|---|---|---|']
 for arm in ARMS:
  for judge in ['Codex','Claude']:
   r=results[arm,judge]
   lines.append(f"| {arm} | {judge} | {r['raw']['ratio']:.8f} | {r['raw']['ci95'][0]:.8f}, {r['raw']['ci95'][1]:.8f} | {r['floor']['ratio']:.8f} | {r['floor']['ci95'][0]:.8f}, {r['floor']['ci95'][1]:.8f} | {r['win']:.8f} | {r['tie']:.8f} | {r['loss']:.8f} | {r['win_score']:.8f} |")
 lines+=['','Paired H − K uses shared item draws, averaging seeds within each item first; percentile bootstrap over items, 2000 resamples, seed 1. This interval represents item variation conditional on these two generation seeds.','',
 '| Judge | Raw H − K | Raw 95% CI | Floor-adjusted H − K | Floor 95% CI |','|---|---|---|---|---|']
 for judge,d in deltas.items():
  a,b=d['raw'],d['floor'];lines.append(f"| {judge} | {a['diff']:.8f} | {a['diff_ci95'][0]:.8f}, {a['diff_ci95'][1]:.8f} | {b['diff']:.8f} | {b['diff_ci95'][0]:.8f}, {b['diff_ci95'][1]:.8f} |")
 lines+=['','Spearman correlations use midranks for ties (12-decimal rounding removes floating-point averaging noise) across 51 items, after averaging both orders and both generation seeds. Score correlation compares BOAR mean rubric scores; ratio correlation compares BOAR/reference per-item ratios.','',
 '| Arm | Score Spearman rho | Ratio Spearman rho |','|---|---|---|']
 for arm,c in correlations.items():lines.append(f"| {arm} | {c['score']:.8f} | {c['ratio']:.8f} |")
 lines+=['','## Numeric summary key','',
 'Lines 1–2: successful verdicts, attempts, failed attempts, tool calls; then items, generation seeds, arms, order seed, reporter bootstrap seed, paired bootstrap seed, resamples.',
 'Lines 3–6: K Codex, K Claude, H Codex, H Claude; columns raw ratio, floor-adjusted ratio, win, tie, loss.',
 'Lines 7–8: Codex, Claude; columns raw H−K, lower CI, upper CI, floor-adjusted H−K, lower CI, upper CI.',
 'Lines 9–10: K, H; columns score Spearman rho, ratio Spearman rho.','',
 '## Numeric summary','', '```']
 summary=[f"408 {len(calls)} {sum(not r['ok'] for r in calls)} {sum(r['toolCalls'] for r in calls)}",'51 2 2 7 11 1 2000']
 for arm,judge in [('K','Codex'),('K','Claude'),('H','Codex'),('H','Claude')]:
  r=results[arm,judge];summary.append(' '.join(f'{v:.8f}' for v in [r['raw']['ratio'],r['floor']['ratio'],r['win'],r['tie'],r['loss']]))
 for judge in ['Codex','Claude']:
  d=deltas[judge];summary.append(' '.join(f'{v:.8f}' for v in [d['raw']['diff'],*d['raw']['diff_ci95'],d['floor']['diff'],*d['floor']['diff_ci95']]))
 for arm in ARMS:summary.append(' '.join(f'{v:.8f}' for v in correlations[arm].values()))
 lines+=summary+['```','','## Per-item scores','','| Id | K Codex score | K Claude score | H Codex score | H Claude score |','|---|---|---|---|---|']
 for i in ids:lines.append('| '+i+' | '+' | '.join(f"{results[arm,judge]['scores'][i][0]:.8f}" for arm,judge in [('K','Codex'),('K','Claude'),('H','Codex'),('H','Claude')])+' |')
 lines+=['','## Input fingerprints','','| Input | SHA256 |','|---|---|']+[f'| {p} | {h} |' for p,h in input_hashes.items()]
 (OUT/'XFAM-REPORT.md').write_text('\n'.join(lines)+'\n');(OUT/'summary.txt').write_text('\n'.join(summary)+'\n')
 # Numeric fields and identifiers only; rationales and source text never enter this artifact.
 safe={'results':{f'{a}-{j}':r for (a,j),r in results.items()},'deltas':deltas,'correlations':correlations,'inputs':input_hashes}
 (OUT/'XFAM-STATS.json').write_text(json.dumps(safe,indent=2)+'\n')
 assert all(sha(BENCH/p)==h for p,h in input_hashes.items())
 print('Report completed; validated 408 verdicts and unchanged input fingerprints.')

if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='--reporter':
  report.Bench=XfamBench
  report.main(sys.argv[2:])
  raise SystemExit(0)
 try:build()
 except Exception:
  # Do not print exception payloads, which may contain source material.
  print('Report failed; inspect privately.',file=sys.stderr);raise SystemExit(1)
