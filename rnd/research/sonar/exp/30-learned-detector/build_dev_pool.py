"""Build the non-blind dev pool (questions only; labels come from label_dev). Skips blind/, veil, v1/v2-fresh, v02-*."""
import json, glob, collections
B = '<workspace>/'
jl = lambda p: [json.loads(l) for l in open(p) if l.strip()]
out, seen = [], set()
def add(src, id_, turns, extra=None):
    turns = [t for t in turns if t and t.strip()]
    key = tuple(t.strip() for t in turns)
    if not turns or key in seen: return
    seen.add(key); out.append({"src": src, "id": id_, "turns": turns, **(extra or {})})
def users(item):
    h = item.get('history') or {}
    ts = h.get('turns', []) if isinstance(h, dict) else h
    return [t['text'] for t in ts if isinstance(t, dict) and t.get('role') == 'user']
BAD = ('v1-', 'v02-', 'v2-')
for p in [B+'boar-eval/bench/v0.1/questions.public.jsonl', B+'boar-eval/bench/v0.1/safety/track.v0.3.jsonl']:
    for x in jl(p): add('v0.1', x['id'], [x['question']], {"danger_meta": x.get('danger'), "cat": x.get('category')})
for x in jl(B+'rnd/research/compass/chat-slice/slice.v0.jsonl'):
    us = [t['text'] for t in x['turns'] if t['role'] == 'user']
    for i in range(len(us)): add('chat-v0', f"{x['id']}#{i}", us[:i+1], {"kind": x.get('kind')})
files = glob.glob(B+'boar-eval/runs/night-2026-10-01/**/*.requests.jsonl', recursive=True)
files += glob.glob(B+'rnd/research/sonar/exp/29-instant-offtopic/**/*requests*.jsonl', recursive=True)
for f in sorted(files):
    if any(k in f for k in ('fresh', 'blind', 'veil')): continue
    src = 'night' if 'night-2026' in f else 'exp29'
    for r in jl(f):
        it = r['item']
        if it['id'].startswith(BAD): continue
        add(src, it['id'], users(it) + [it['question']])
for p in glob.glob(B+'rnd/kiln/exp-05-bge-query-prefix/questions.*.jsonl'):
    if 'retrieval-v1' in p or 'vitalik58' in p:
        for x in jl(p): add('retr', x.get('id', ''), [x.get('question') or x.get('query')])
S = '<scratch>'
for i, q in enumerate(json.load(open(S))):
    if '[1]' in q: continue  # answer texts in the parity set, not questions
    add('parity516', f'p{i}', [q])
for i, x in enumerate(jl('dev/firstaidqa.sample.jsonl')): add('firstaidqa', f'faq{i}', [x['question']])
print(len(out), collections.Counter(o['src'] for o in out), 'multi-turn', sum(len(o['turns']) > 1 for o in out))
json.dump(out, open('dev/pool.raw.json', 'w'), ensure_ascii=False, indent=0)
