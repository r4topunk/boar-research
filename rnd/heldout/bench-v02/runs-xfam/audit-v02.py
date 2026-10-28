from pathlib import Path
import json,hashlib
ROOT=Path('<workspace>'); OUT=ROOT/'blind/bench-v02/runs-xfam'
cfg=json.loads((OUT/'run-config.json').read_text()); bench=Path(cfg['bench']); refs=Path(cfg['refs'])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
man=json.loads((bench/'refs/MANIFEST.json').read_text()); questions=bench/man['questions_file']
ids={json.loads(l)['id'] for l in questions.read_text().splitlines() if l.strip()}; assert len(ids)==110
runs=[('runs-cut6','cut6-v02-s42'),('runs-cut6','cut6-v02-s43'),('runs-dt512v02','dhv-H-v02-s42')]
total=0; attempts=0
for folder,name in runs:
    trace=ROOT/'blind/bench-v02'/folder/(name+'.traces.jsonl')
    out=OUT/(name+'.codex.judgments.jsonl'); rows=[json.loads(l) for l in out.read_text().splitlines() if l.strip()]
    expected={(i,o) for i in ids for o in ['boarA','boarB']}
    assert len(rows)==220 and {(r['queryId'],r['order']) for r in rows}==expected
    for r in rows:
        assert r['ok'] and r['judgeVersion']=='judge.v1-codex'
        assert r['requestedModel']==r['judgeModel']=='gpt-5.6-sol'
        assert r['seed']==7 and r['sampling']=={'temperature':None,'temperatureControl':'unavailable in codex exec','reasoningEffort':'high'}
        assert r['questionsSha256']==sha(questions) and r['refsSha256']==sha(refs) and r['tracesSha256']==sha(trace)
        v=r['verdict'];assert set(v)=={'scores_A','scores_B','winner','rationale'}
        assert v['winner'] in ['A','B','tie'] and isinstance(v['rationale'],str)
        for side in ['scores_A','scores_B']:
            assert set(v[side])=={'correctness','completeness','usefulness'}
            assert all(isinstance(s,int) and 1<=s<=5 for s in v[side].values())
        a=r['order']=='boarA'
        assert r['mapped']['boar']==v['scores_A' if a else 'scores_B']
        assert r['mapped']['ref']==v['scores_B' if a else 'scores_A']
    calls=[json.loads(l) for l in Path(str(out)+'.calls.jsonl').read_text().splitlines() if l.strip()]
    assert all(c['toolCalls']==0 for c in calls)
    assert sum(c['ok'] for c in calls)==220
    total+=len(rows);attempts+=len(calls)
assert total==660
report=(OUT/'XFAM-V02-REPORT.md').read_text()
assert 'offset_comparison' in report and 'Spearman_score' in report
summary=(OUT/'summary-10.txt').read_text().splitlines();assert len(summary)==10
assert all(all(__import__('re').fullmatch(r'-?\d+(?:\.\d+)?',v) for v in line.split()) for line in summary)
result={'items':110,'files':3,'orders':2,'valid_verdicts':total,'call_attempts':attempts,'successful_calls':660,'tool_calls':0,'provenance_verified':True,'schema_verified':True,'summary_lines':10}
(OUT/'audit-v02.json').write_text(json.dumps(result,indent=2)+'\n')
print('Audit passed: 660 valid verdicts, 110 IDs per file, complete order coverage, fixed provenance, 0 tool calls, 10 numeric summary lines.')
