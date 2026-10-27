"""v2: e5-small linear head on SPEC-aligned data. Features = emb('query: '+last) ⊕ emb('query: '+detector_text), L2-normalized
(= llama.cpp embd_normalize 2). usage: embed_head2.py <tag>"""
import json, sys, numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from common2 import detector_text, load_aligned, split
tag = sys.argv[1]; tr, va = split(load_aligned())
m = SentenceTransformer('intfloat/multilingual-e5-small', device='cpu')
F = lambda xs: np.hstack([m.encode(['query: ' + x['turns'][-1] for x in xs], normalize_embeddings=True, batch_size=64),
                          m.encode(['query: ' + detector_text(x['turns']) for x in xs], normalize_embeddings=True, batch_size=64)])
Xtr, Xva = F(tr), F(va); ytr = np.array([x['y'] for x in tr]); yv = np.array([x['y'] for x in va]); best = None
for C in (1, 3, 10, 30):
    clf = LogisticRegression(C=C, max_iter=5000, class_weight='balanced').fit(Xtr, ytr); pv = clf.predict_proba(Xva)[:, 1]; auc = roc_auc_score(yv, pv)
    print(f'C={C} val AUC {auc:.4f}');
    if best is None or auc > best[0]: best = (auc, C, clf, pv)
auc, C, clf, pv = best
json.dump({'auc': auc, 'C': C, 'ids': [x['id'] for x in va], 'labels': yv.tolist(), 'scores': pv.tolist()}, open(f'results/{tag}.synthval.json', 'w'))
json.dump({'kind': 'e5-linear', 'w': clf.coef_[0].tolist(), 'b': float(clf.intercept_[0])}, open(f'results/{tag}.head.json', 'w'))
print('done', tag, C)
