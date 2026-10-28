from pathlib import Path
import subprocess,json,time,sys
root=Path('<workspace>');b=root/'blind/vitalik-para1';d=b/'runs-xfam'
for arm,folder,stem in [('K','runs-cut6','cut6-vpara'),('H','runs-dt512','dh-H-vpara')]:
 for seed in [42,43]:
  t=b/folder/f'{stem}-s{seed}.traces.jsonl';out=d/f'{stem}-s{seed}.codex.judgments.jsonl'
  cmd=['node',str(root/'boar-eval/harness/judge-codex.mjs'),'--bench',str(b),'--traces',str(t),'--out',str(out),'--seed','7','--judge-model','gpt-5.6-sol','--strict','--concurrency','4','--gap-ms','1000']
  with (d/f'{arm}-s{seed}.log').open('a') as log:
   result=subprocess.run(cmd,stdout=log,stderr=log)
  print(f'{arm} {seed} exit {result.returncode}',flush=True)
  if result.returncode:sys.exit(result.returncode)
  rows=[json.loads(l) for l in out.read_text().splitlines() if l.strip()]
  assert len(rows)==102 and len({(x['queryId'],x['order']) for x in rows})==102
print('All 408 verdicts complete.',flush=True)
