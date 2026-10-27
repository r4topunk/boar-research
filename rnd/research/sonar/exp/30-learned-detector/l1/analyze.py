"""health11 L1 analysis: base (health9) vs arm (health11) per profile.
core = exp-29 L1 102 + leak 40 (base traces from exp-29/leak runs); cdev = Compass emergency-dev 300.
Prints health route, detector fires, non-Wikivoyage sources shown, safety v0.8.7 (unsafe/review) and writes every changed answer
to l1/<set>-<p>-changed.txt for hand read."""
import json, sys, importlib.util
from pathlib import Path
X = Path(__file__).resolve().parents[1]; R = X.parents[2]
sp = importlib.util.spec_from_file_location('sc', R / 'compass/exp/safety-v087/safety_check.v0.8.7.py'); sc = importlib.util.module_from_spec(sp); sp.loader.exec_module(sc)
S = sc.load(rules_path=R / 'compass/exp/safety-v087/rules.v0.8.7.json', overlay_path=R / 'compass/exp/safety-v087/overlay.v0.4.json')
st = lambda hs: 'unsafe' if any(h.get('status', 'unsafe') == 'unsafe' for h in hs) else 'review' if hs else 'clean'
jl = lambda f: {json.loads(l)['itemId']: json.loads(l) for l in open(f)}
CD = {json.loads(l)['id']: json.loads(l) for l in open(R / 'compass/exp/emergency-dev/dev.jsonl')}
E29 = R / 'sonar/exp/29-instant-offtopic/l1'
TP = {json.loads(l)['id']: json.loads(l)['label'] for l in open(X / 'probes/terse-live.heldout.jsonl')}
def base_core(p):
    d = jl(E29 / f'{p}-health9-h9.traces.jsonl'); d.update(jl(X / f'leak/leak-{p}-h9.traces.jsonl')); d.update(jl(X / f'leak/leak2-{p}-h9.traces.jsonl')); return d
def health(t): return any(r == 'grounding:health-strict' for r in t['route']['reasonCodes'])
def fire(t): return 'detector:fire' in t['route']['reasonCodes']
def offsrc(t): return any(not str(s).startswith('Wikivoyage') for s in (t['answer'].get('shown') or []))
def safety(t, i):
    q = CD.get(i) or {'id': i, 'question': t['question']}
    if 'turns' not in q and t.get('question'): q = {'id': i, 'question': t['question']}
    a = t['answer']; rs = sc.rules_for_v085(q, S)
    return st(sc.check(a.get('text') or '', rs, S)) if rs and a.get('text') else 'clean'
for p in ('and', 'ios'):
    sets = [('core2', lambda: jl(X / f'l1/core2-{p}-health9.traces.jsonl'), lambda: jl(X / f'l1/core2-{p}-health11.traces.jsonl')), ('cdev', lambda: jl(X / f'l1/cdev-{p}-health9.traces.jsonl'), lambda: jl(X / f'l1/cdev-{p}-health11.traces.jsonl'))]
    for name, fb, fa in sets:
        try: B, A = fb(), fa()
        except FileNotFoundError: continue
        ids = [i for i in A if i in B]; out = open(X / f'l1/{name}-{p}-changed.txt', 'w')
        c = dict(n=len(ids), changed=0, hb=0, ha=0, fire=0, offb=0, offa=0, unsafe_b=0, unsafe_a=0, review_b=0, review_a=0)
        grp = {}
        for i in ids:
            b, a = B[i], A[i]; c['hb'] += health(b); c['ha'] += health(a); c['fire'] += fire(a); c['offb'] += offsrc(b); c['offa'] += offsrc(a)
            sb, sa = safety(b, i), safety(a, i); c['unsafe_b'] += sb == 'unsafe'; c['unsafe_a'] += sa == 'unsafe'; c['review_b'] += sb == 'review'; c['review_a'] += sa == 'review'
            if name == 'core2' and i.startswith('tp-'):
                k = grp.setdefault('terse_pos' if TP[i] else 'terse_neg', [0, 0, 0]); k[0] += 1; k[1] += health(b); k[2] += health(a)
            if name == 'cdev':
                d = CD[i]; g = 'pos' if d['emergency'] else ('howto' if d['howto'] else 'neg')
                k = grp.setdefault(g, [0, 0, 0]); k[0] += 1; k[1] += health(b); k[2] += health(a)
            if b['answer']['text'] != a['answer']['text']:
                c['changed'] += 1
                lab = f" [{CD[i]['emergency']}/{CD[i]['howto']} {CD[i]['cat']} {CD[i].get('sev')}]" if i in CD else ''
                out.write(f"== {i}{lab} health {int(health(b))}->{int(health(a))} safety {sb}->{sa} offsrc {int(offsrc(b))}->{int(offsrc(a))}\nQ: {a['question']}\nB: {b['answer']['text'][:400]}\nA: {a['answer']['text'][:400]}\n\n")
        print(p, name, json.dumps(c), json.dumps({g: f'health {v[1]}->{v[2]} of {v[0]}' for g, v in grp.items()}))
