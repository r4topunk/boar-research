from pathlib import Path
import json,subprocess,time
r=Path('<workspace>'); o=r/'blind/bench-v02/runs-xfam'; c=json.loads((o/'run-config.json').read_text())
runs=[('runs-cut6','cut6-v02-s42'),('runs-cut6','cut6-v02-s43'),('runs-dt512v02','dhv-H-v02-s42')]
s={'state':'running','completed':0}
for folder,name in runs:
    s.update(current=name); (o/'progress.json').write_text(json.dumps(s))
    a=['node',str(r/'boar-eval/harness/judge-codex.mjs'),'--bench',c['bench'],'--refs',c['refs'],'--traces',str(r/'blind/bench-v02'/folder/(name+'.traces.jsonl')),'--out',str(o/(name+'.codex.judgments.jsonl')),'--strict','--concurrency','4','--gap-ms','5000']
    while True:
        with (o/(name+'.run.log')).open('a') as f:p=subprocess.run(a,stdout=f,stderr=subprocess.STDOUT)
        if p.returncode==3:
            s.update(state='rate_limited'); (o/'progress.json').write_text(json.dumps(s)); time.sleep(300); continue
        if p.returncode:
            s.update(state='failed',exit=p.returncode); (o/'progress.json').write_text(json.dumps(s)); raise SystemExit(p.returncode)
        rows=[json.loads(l) for l in (o/(name+'.codex.judgments.jsonl')).read_text().splitlines() if l.strip()]
        assert len(rows)==220 and len({(x['queryId'],x['order']) for x in rows if x['ok']})==220
        s.update(state='running',completed=s['completed']+1); (o/'progress.json').write_text(json.dumps(s)); break
s.update(state='judged'); (o/'progress.json').write_text(json.dumps(s))
