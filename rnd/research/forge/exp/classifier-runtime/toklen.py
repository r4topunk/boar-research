import json, numpy as np
from transformers import AutoTokenizer
mm = AutoTokenizer.from_pretrained('mmbert-small-cls'); bg = AutoTokenizer.from_pretrained('BAAI/bge-small-en-v1.5')
msgs = {}
for l in open('<workspace>/rnd/research/anvil/exp/chat-routing/slice.items.jsonl'):
    d = json.loads(l); msgs.setdefault('chat-'+d['lang'], []).append(d['msg'])
for l in open('<workspace>/boar-eval/bench/v0.1/questions.public.jsonl'):
    d = json.loads(l); q = d.get('question') or d.get('prompt') or d.get('q'); lang = d.get('lang') or d.get('language') or 'en'
    if q: msgs.setdefault('v01-'+lang, []).append(q)
allm, allb = [], []
for k, v in sorted(msgs.items()):
    a = np.array([len(mm(x)['input_ids']) for x in v]); b = np.array([len(bg(x)['input_ids']) for x in v]); allm += a.tolist(); allb += b.tolist()
    print(f"{k:10s} n={len(v):3d} mmBERT p50/p90 {np.median(a):.0f}/{np.percentile(a,90):.0f}  bge p50/p90 {np.median(b):.0f}/{np.percentile(b,90):.0f}  ratio {b.sum()/a.sum():.2f}")
print('ALL', len(allm), 'mm p50/p90/max', np.median(allm), np.percentile(allm,90), max(allm), 'bge', np.median(allb), np.percentile(allb,90), max(allb))
