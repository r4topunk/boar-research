"""Compare detectors on the labelled dev pool: lexical (health9 predicate) vs learned scores.
Operating point = recall at the lexical detector's false-fire count on dev negatives (matched FP), plus
the threshold fixed on the synthetic val split (FP rate <= 5% there) so one number is not tuned on dev.
usage: evaluate.py tag [tag...]"""
import json, sys, re, collections, numpy as np
P = json.load(open('dev/pool.raw.json')); L = [json.loads(l) for l in open('dev/labels.sonar.jsonl')]
lex = np.array(json.load(open('dev/lexical.h9.json'))); y = np.array([x['label'] for x in L])
PT = re.compile(r"\b(não|nao|você|voce|está|tá|meu|minha|filho|filha|bebê|criança|crianca|que|com|uma|ele|ela|o que|isso|pra|para|fazer|tem|dor|é)\b", re.I)
ES = re.compile(r"\b(¿|qué|que hago|mi|hijo|hija|bebé|niño|niña|está|tiene|una|con|para|cómo|el|la|los|las|hay|muy|se|y)\b|[¿¡ñ]", re.I)
def lang(t):
    p = len(PT.findall(t)); e = len(ES.findall(t))
    if re.search(r"[ãõç]|\bnão\b|\bvocê\b", t): return 'pt'
    if re.search(r"[¿¡ñ]", t): return 'es'
    return 'pt' if p >= 2 and p >= e else ('es' if e >= 3 else 'en')
langs = np.array([lang(' '.join(x['turns'])) for x in P]); srcs = np.array([x['src'] for x in P])
neg = y == 0; pos = y == 1
def rep(name, pred):
    r = {'recall': f"{(pred & pos).sum()}/{pos.sum()}", 'false_fires': f"{(pred & neg).sum()}/{neg.sum()}"}
    for g, arr in (('lang', langs), ('src', srcs)):
        for v in sorted(set(arr)):
            m = arr == v
            if (pos & m).sum(): r[f'rec_{v}'] = f"{(pred & pos & m).sum()}/{(pos & m).sum()}"
            if (neg & m).sum() and (pred & neg & m).sum(): r[f'ff_{v}'] = f"{(pred & neg & m).sum()}/{(neg & m).sum()}"
    hn = np.array([x['cls'] == 'hard_negative' for x in L])
    r['ff_hard_negative'] = f"{(pred & hn).sum()}/{hn.sum()}"
    print(f"\n## {name}"); print(json.dumps(r, ensure_ascii=False))
    return r
out = {'lexical_h9': rep('lexical health9', lex.astype(bool))}
k = int((lex.astype(bool) & neg).sum())
for tag in sys.argv[1:]:
    s = np.array(json.load(open(f'results/{tag}.dev_scores.json')))
    sv = json.load(open(f'results/{tag}.synthval.json'))
    from sklearn.metrics import roc_auc_score
    auc = roc_auc_score(y, s)
    # matched FP: highest threshold set so that false fires on dev negatives <= lexical's
    thr_m = np.sort(s[neg])[::-1][k] if k < neg.sum() else 0
    pred_m = s > thr_m
    # synth-val threshold: smallest t with FP rate <= 5% on synthetic val negatives
    ids = sv['ids']; sc = np.array(sv['scores'])
    lab = {}
    import glob
    for p in glob.glob('data/synth-*.jsonl'):
        for l in open(p):
            try: x = json.loads(l); lab[x['id']] = x['label']
            except (ValueError, KeyError): pass
    yv = np.array([lab[i] for i in ids]); t5 = np.quantile(sc[yv == 0], .95)
    print(f"\n# {tag}: dev AUC {auc:.4f}; synth-val AUC {sv['auc']:.4f}; matched-FP thr {thr_m:.3f}; synth-val thr {t5:.3f}")
    out[f'{tag}@matchedFP'] = rep(f'{tag} @ matched FP (thr {thr_m:.3f})', pred_m)
    out[f'{tag}@synthval5'] = rep(f'{tag} @ synth-val FP5% (thr {t5:.3f})', s > t5)
    tl = np.quantile(sc[yv == 0], 1 - k / neg.sum())  # synth-val threshold at lexical's dev false-fire RATE (not tuned on dev labels of the learned model)
    out[f'{tag}@synthvalLexRate'] = rep(f'{tag} @ synth-val thr at lexical FP rate (thr {tl:.3f})', s > tl)
    # union with lexical (augment): learned at matched-FP-of-union
    for t in (0.5, 0.7, 0.9):
        out[f'{tag}@{t}+lex'] = rep(f'{tag} >{t} OR lexical', (s > t) | lex.astype(bool))
json.dump(out, open('results/eval.' + '_'.join(sys.argv[1:] or ['lex']) + '.json', 'w'), indent=1, ensure_ascii=False)
