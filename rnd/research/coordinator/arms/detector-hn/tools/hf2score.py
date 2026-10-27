"""DETECTOR-FT2: HF fp32 (CPU) P(emergency) of results/<ckpt>.model on ft2/small2.jsonl (small_sets + sonar903) -> results/<ckpt>.hf_small2.json.
usage: hf2score.py <ckpt> [...]"""
import json, sys, torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
R = [json.loads(l) for l in open('data/small2.jsonl')]
for t in sys.argv[1:]:
    tok = AutoTokenizer.from_pretrained(f'results/{t}.model'); tok.truncation_side = 'left'
    m = AutoModelForSequenceClassification.from_pretrained(f'results/{t}.model').eval(); out = {}
    with torch.no_grad():
        for i in range(0, len(R), 32):
            b = R[i:i+32]; e = tok([x['text'] for x in b], truncation=True, max_length=128, padding=True, return_tensors='pt')
            for x, p in zip(b, torch.softmax(m(**e).logits.float(), -1)[:, 1].tolist()): out[x['set'] + '/' + x['id']] = round(p, 5)
    json.dump(out, open(f'results/{t}.hf_small2.json', 'w')); print(t, len(out), flush=True)
