"""DETECTOR-FT2 recall screen on HF fp32 scores (results/<ckpt>.hf_small2.json) vs v3b GGUF fires (data/v3b_ref.json) @0.2:
lost Compass/terse/PT positives, Sonar dev recall vs v3b's, probe health-strict routes kept (of v3b's 47), cm fires. usage: ft2_screen.py <ckpt> [...]"""
import json, sys
ref = json.load(open('data/v3b_ref.json')); out = {}
for t in sys.argv[1:]:
    P = json.load(open(f'results/{t}.hf_small2.json')); f = lambda s, i: P[f'{s}/{i}'] >= 0.2; r = {}
    for s in ('compass300', 'terse30', 'ptmirror28', 'sonar903'):
        r[s + '_lost'] = [i for i in ref[s]['fired_pos'] if not f(s, i)]; r[s + '_kept'] = len(ref[s]['fired_pos']) - len(r[s + '_lost'])
    r['probes_kept'] = sum(f('probes65', i) for i in ref['probes65']['fired']); r['probes_lost'] = [i for i in ref['probes65']['fired'] if not f('probes65', i)]
    r['cm_fires'] = [k.split('/')[1] for k, v in P.items() if k.startswith('main97/st-qa-') and v >= 0.2]
    r['exact_lost'] = len(r['compass300_lost']) + len(r['terse30_lost']) + len(r['ptmirror28_lost'])
    r['sonar_ratio'] = round(r['sonar903_kept'] / len(ref['sonar903']['fired_pos']), 4)
    r['pass_hf'] = r['exact_lost'] == 0 and r['sonar_ratio'] >= 0.98
    out[t] = r; print(t, 'exact_lost', r['exact_lost'], 'sonar', r['sonar903_kept'], r['sonar_ratio'], 'probes', r['probes_kept'], 'cm', len(r['cm_fires']), 'PASS' if r['pass_hf'] else '', flush=True)
    json.dump(r, open(f'results/{t}.screen.json', 'w'), indent=1)
