"""(a) Linear head on a frozen sentence embedder. Features = emb(last turn) ⊕ emb(all user turns joined).
usage: embed_head.py <hf model id> <tag>   -> results/<tag>.dev_scores.json + results/<tag>.synthval.json"""
import json, sys, glob, random, numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
mid, tag = sys.argv[1], sys.argv[2]
prefix = sys.argv[3] if len(sys.argv) > 3 else ""
def jl(p):
    out = []
    for l in open(p):
        try:
            x = json.loads(l)
            if {'lang', 'label', 'turns'} <= set(x): out.append(x)
        except ValueError: pass  # a line still being written
    return out
synth = [x for p in sorted(glob.glob('data/synth-*.jsonl')) for x in jl(p)]
dev = json.load(open('dev/pool.raw.json'))
# synthetic split: 85% train / 15% val, stratified by lang, fixed seed
rng = random.Random(30); rng.shuffle(synth)
val_ids = set()
for lang in ('en', 'pt', 'es'):
    xs = [x['id'] for x in synth if x['lang'] == lang]; val_ids |= set(xs[:int(len(xs) * .15)])
tr = [x for x in synth if x['id'] not in val_ids]; va = [x for x in synth if x['id'] in val_ids]
m = SentenceTransformer(mid, device='cpu')
def feats(items):
    last = [prefix + x['turns'][-1] for x in items]
    allt = [prefix + ' | '.join(x['turns']) for x in items]
    a = m.encode(last, batch_size=64, normalize_embeddings=True); b = m.encode(allt, batch_size=64, normalize_embeddings=True)
    return np.hstack([a, b])
Xtr, Xva, Xdev = feats(tr), feats(va), feats(dev)
ytr = np.array([x['label'] for x in tr])
best = None
for C in (0.3, 1, 3, 10):
    clf = LogisticRegression(C=C, max_iter=3000, class_weight='balanced').fit(Xtr, ytr)
    pv = clf.predict_proba(Xva)[:, 1]
    yv = np.array([x['label'] for x in va])
    from sklearn.metrics import roc_auc_score
    auc = roc_auc_score(yv, pv)
    print(f'C={C} synth-val AUC {auc:.4f}')
    if best is None or auc > best[0]: best = (auc, C, clf, pv)
auc, C, clf, pv = best
json.dump({'C': C, 'auc': auc, 'ids': [x['id'] for x in va], 'scores': pv.tolist()}, open(f'results/{tag}.synthval.json', 'w'))
json.dump(clf.predict_proba(Xdev)[:, 1].tolist(), open(f'results/{tag}.dev_scores.json', 'w'))
np.savez(f'results/{tag}.head.npz', coef=clf.coef_, intercept=clf.intercept_)
print('done', tag, 'C', C)
