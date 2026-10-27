"""Score any JSONL/JSON of {turns: [str | {role,text}]} with a trained detector (user turns only).
usage: score.py <tag> <input> <out.json>   tag in {bge-head, e5-head, mmbert-ft}"""
import json, sys, numpy as np
tag, inp, out = sys.argv[1:4]
items = json.load(open(inp)) if inp.endswith('.json') else [json.loads(l) for l in open(inp) if l.strip()]
U = [[t if isinstance(t, str) else t['text'] for t in x['turns'] if isinstance(t, str) or t.get('role') == 'user'] for x in items]
if tag.endswith('-head'):
    from sentence_transformers import SentenceTransformer
    mid, pre = {'bge-head': ('BAAI/bge-small-en-v1.5', ''), 'e5-head': ('intfloat/multilingual-e5-small', 'query: ')}[tag]
    m = SentenceTransformer(mid, device='cpu'); h = np.load(f'results/{tag}.head.npz')
    a = m.encode([pre + u[-1] for u in U], normalize_embeddings=True); b = m.encode([pre + ' | '.join(u) for u in U], normalize_embeddings=True)
    z = np.hstack([a, b]) @ h['coef'][0] + h['intercept'][0]; s = (1 / (1 + np.exp(-z))).tolist()
else:
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    d = f'results/{tag}.model'; tok = AutoTokenizer.from_pretrained(d); m = AutoModelForSequenceClassification.from_pretrained(d).eval()
    s = []
    with torch.no_grad():
        for i in range(0, len(U), 32):
            b = U[i:i + 32]
            e = tok([u[-1] for u in b], [' | '.join(u[:-1]) for u in b], truncation=True, max_length=160, padding=True, return_tensors='pt')
            s += torch.softmax(m(**e).logits, -1)[:, 1].tolist()
json.dump(s, open(out, 'w'))
print(tag, len(s))
