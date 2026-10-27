"""Card picker = multinomial logistic regression on the detector's own pooled vector (mmBERT v3b encoder, mean pooling over
detector_text = llama.cpp `embedding(text, embd_normalize -1)`), so it costs ~0 ms on the phone (one 384x33 matvec).
usage: train.py <tag> [extra train jsonl ...]   -> picker/<tag>.head.json, picker/<tag>.eval_probs.json"""
import json, sys, glob, numpy as np, torch
from transformers import AutoTokenizer, AutoModel
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_predict
sys.path.insert(0, '.')
from common2 import detector_text
tag = sys.argv[1]
train = json.load(open('picker/train.json')); ev = json.load(open('picker/eval.json'))
for p in sys.argv[2:]:
    for x in map(json.loads, open(p)):
        if 'card' in x: train.append({'id': x['id'], 'turns': x['turns'], 'y': x['card'], 'src': 'cards'})
tok = AutoTokenizer.from_pretrained('results/mmbert-v3b.encoder'); enc = AutoModel.from_pretrained('results/mmbert-v3b.encoder').eval()
def embed(items):
    out = []
    with torch.no_grad():
        for x in items:
            ids = tok(detector_text(x['turns']))['input_ids']
            out.append(enc(input_ids=torch.tensor([ids])).last_hidden_state[0].mean(0).numpy())
    return np.array(out)
Xtr, Xev = embed(train), embed(ev)
classes = sorted({x['y'] for x in train}); ytr = np.array([classes.index(x['y']) for x in train])
mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-6
import os
best = None
if os.environ.get('PICKER_MLP'):
    from sklearn.neural_network import MLPClassifier
    clf = MLPClassifier(hidden_layer_sizes=(256,), alpha=1e-3, max_iter=400, random_state=30, early_stopping=True)
    pr = cross_val_predict(clf, (Xtr - mu) / sd, ytr, cv=5, method='predict_proba'); print('MLP 5-fold acc', (pr.argmax(1) == ytr).mean())
    clf.fit((Xtr - mu) / sd, ytr); P = clf.predict_proba((Xev - mu) / sd)
    json.dump([{'id': x['id'], 'y': x['y'], 'src': x['src'], 'probs': {c: round(float(p), 5) for c, p in zip(classes, P[i]) if p > 0.01}} for i, x in enumerate(ev)], open(f'picker/{tag}.eval_probs.json', 'w'), ensure_ascii=False)
    sys.exit(0)
for C in (0.1, 0.3, 1.0):
    clf = LogisticRegression(C=C, max_iter=4000, class_weight='balanced')
    pr = cross_val_predict(clf, (Xtr - mu) / sd, ytr, cv=5, method='predict_proba')
    acc = (pr.argmax(1) == ytr).mean(); print(f'C={C} 5-fold acc {acc:.3f}', flush=True)
    if best is None or acc > best[0]: best = (acc, C)
clf = LogisticRegression(C=best[1], max_iter=4000, class_weight='balanced').fit((Xtr - mu) / sd, ytr)
# fold the standardization into the weights: z = W((x-mu)/sd)+b = (W/sd)x + (b - (W/sd)mu)
W = clf.coef_ / sd; b = clf.intercept_ - W @ mu
json.dump({'kind': 'card-linear', 'classes': classes, 'W': np.round(W, 7).tolist(), 'b': np.round(b, 7).tolist()}, open(f'picker/{tag}.head.json', 'w'))
P = clf.predict_proba((Xev - mu) / sd)
json.dump([{'id': x['id'], 'y': x['y'], 'src': x['src'], 'probs': {c: round(float(p), 5) for c, p in zip(classes, P[i]) if p > 0.01}} for i, x in enumerate(ev)], open(f'picker/{tag}.eval_probs.json', 'w'), ensure_ascii=False)
print('done', tag, 'C', best[1], 'classes', len(classes))
