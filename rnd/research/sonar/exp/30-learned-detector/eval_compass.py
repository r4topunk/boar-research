"""Compass emergency-dev v1 metrics (SPEC §5): recall on emergency=1 (by named/lang/sev/multi), strict FF on emergency=0&howto=0, tolerated howto rate.
usage: eval_compass.py <scores.json|lexical.json> [thr]"""
import json, sys, numpy as np
D = [json.loads(l) for l in open('<workspace>/rnd/research/compass/exp/emergency-dev/dev.jsonl')]
def metrics(pred):
    y = np.array([d['emergency'] for d in D]); hw = np.array([d['howto'] for d in D]); pred = np.asarray(pred, bool)
    multi = np.array([sum(t['role'] == 'user' for t in d['turns']) > 1 for d in D])
    r = {'recall': f"{(pred & (y == 1)).sum()}/{(y == 1).sum()}", 'strictFF': f"{(pred & (y == 0) & (hw == 0)).sum()}/{((y == 0) & (hw == 0)).sum()}", 'howtoFire': f"{(pred & (hw == 1)).sum()}/{(hw == 1).sum()}"}
    for k in ('lang', 'named', 'sev'):
        for v in sorted({str(d.get(k)) for d in D if d['emergency'] == 1}):
            m = np.array([str(d.get(k)) == v for d in D]) & (y == 1); r[f'rec_{k}={v}'] = f"{(pred & m).sum()}/{m.sum()}"
    for v in ('en', 'pt', 'es'):
        m = np.array([d['lang'] == v for d in D]) & (y == 0) & (hw == 0); r[f'FF_{v}'] = f"{(pred & m).sum()}/{m.sum()}"
    m = multi & (y == 1); r['rec_multi'] = f"{(pred & m).sum()}/{m.sum()}"
    r['critical_missed'] = [d['id'] for d, p in zip(D, pred) if d['emergency'] == 1 and d.get('sev') == 'critical' and not p]
    return r
if __name__ == '__main__':
    s = np.array(json.load(open(sys.argv[1]))); thr = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
    print(json.dumps(metrics(s > thr if s.dtype != bool and s.max() <= 1 and len(sys.argv) > 2 else s.astype(bool) if set(np.unique(s)) <= {0, 1} else s > thr), ensure_ascii=False))
