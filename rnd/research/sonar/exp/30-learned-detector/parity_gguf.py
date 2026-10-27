"""Forge ship gate: HF fp32 vs llama.cpp GGUF (b11010, llama-server, pooling mean, n_parallel 1) + the JS-equivalent head.
Gates: token ids identical 100%; decision agreement >= 99%; report max |dp| and pooled cos. Inputs: Compass 300 + Sonar dev 903.
usage: parity_gguf.py <tag> <server_url> <thr> [kind=mmbert|e5]"""
import json, sys, numpy as np, requests, torch
from common2 import detector_text
tag, url, thr = sys.argv[1], sys.argv[2], float(sys.argv[3]); kind = sys.argv[4] if len(sys.argv) > 4 else 'mmbert'
cd = [json.loads(l) for l in open('<workspace>/rnd/research/compass/exp/emergency-dev/dev.jsonl')]
sets = {'compass300': [[t['text'] for t in d['turns'] if t['role'] == 'user'] for d in cd],
        'sonar903': [x['turns'] for x in json.load(open('dev/pool.raw.json'))],
        'terse30': [json.loads(l)['turns'] for l in open('probes/terse-live.heldout.jsonl')],
        'long45': json.load(open('probes/long-adversarial.json'))}  # Forge review: > 128-token multi-turn, emoji, leading-space cuts, typed control tokens
H = json.load(open(f'results/{tag}.head.json'))
def post(path, body): r = requests.post(url + path, json=body, timeout=60); r.raise_for_status(); return r.json()
def emb(text, norm):
    j = post('/embedding', {'content': text, 'embd_normalize': norm}); e = j[0]['embedding'] if isinstance(j, list) else j['embedding']
    return np.array(e[0] if isinstance(e[0], list) else e, dtype=np.float64)
def gelu(x):
    from math import erf
    return np.array([0.5 * v * (1 + erf(v / np.sqrt(2))) for v in x])
def head_mm(p):
    d = H['dim']; z = gelu(np.array(H['dense']).reshape(d, d) @ p); z = (z - z.mean()) / np.sqrt(z.var() + H['eps']) * np.array(H['norm'])
    l = np.array(H['cls_w']).reshape(2, d) @ z + np.array(H['cls_b']); return 1 / (1 + np.exp(l[0] - l[1]))
def head_e5(a, b): return 1 / (1 + np.exp(-(np.array(H['w']) @ np.concatenate([a, b]) + H['b'])))
out = {}
if kind == 'mmbert':
    from transformers import AutoTokenizer, AutoModel
    tok = AutoTokenizer.from_pretrained(f'results/{tag}.encoder'); tok.truncation_side = 'left'; enc = AutoModel.from_pretrained(f'results/{tag}.encoder').eval()
else:
    from sentence_transformers import SentenceTransformer
    st = SentenceTransformer('intfloat/multilingual-e5-small', device='cpu'); tok = st.tokenizer
for name, U in sets.items():
    tid_ok = 0; cos = []; ph = []; pg = []
    for u in U:
        if kind == 'mmbert':
            text = detector_text(u); ids = tok(text)['input_ids']  # no HF truncation: detector_text already fits 126 + 2
            gids = post('/tokenize', {'content': text, 'add_special': True})['tokens']; tid_ok += ids == gids
            with torch.no_grad():
                h = enc(input_ids=torch.tensor([ids])).last_hidden_state[0].double().numpy()
            hp = h.mean(0); gp = emb(text, -1)
            ph.append(head_mm(hp)); pg.append(head_mm(gp)); cos.append(hp @ gp / np.linalg.norm(hp) / np.linalg.norm(gp))
        else:
            q, t = 'query: ' + u[-1], 'query: ' + detector_text(u)
            ids = tok(q)['input_ids']; gids = post('/tokenize', {'content': q, 'add_special': True})['tokens']; tid_ok += ids == gids
            a, b = st.encode([q, t], normalize_embeddings=True).astype(np.float64); ga, gb = emb(q, 2), emb(t, 2)
            ph.append(head_e5(a, b)); pg.append(head_e5(ga, gb)); cos.append(min(a @ ga, b @ gb))
    ph, pg = np.array(ph), np.array(pg)
    out[name] = {'n': len(U), 'token_ids_identical': f'{tid_ok}/{len(U)}', 'decision_agreement': f'{((ph > thr) == (pg > thr)).sum()}/{len(U)}',
                 'max_abs_dp': round(float(np.abs(ph - pg).max()), 4), 'min_pooled_cos': round(float(min(cos)), 5)}
    json.dump({'hf': ph.tolist(), 'gguf': pg.tolist()}, open(f'results/{tag}.parity.{name}.json', 'w'))
print(json.dumps(out, indent=1))
