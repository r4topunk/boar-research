"""Export a fine-tuned ModernBertForSequenceClassification head to JSON for the JS head (src/routing/emergencyHead.ts).
pooled (mean over final_norm hidden states = llama.cpp pooling mean, embd_normalize -1) -> dense(no bias) -> GELU(erf) -> LayerNorm(no bias, eps) -> linear(2) -> softmax[1].
usage: export_head.py <tag>"""
import json, sys
from transformers import AutoModelForSequenceClassification
tag = sys.argv[1]; m = AutoModelForSequenceClassification.from_pretrained(f'results/{tag}.model'); sd = m.state_dict()
r = lambda t: [round(float(v), 7) for v in t.flatten().tolist()]
json.dump({'kind': 'mmbert-cls', 'dim': 384, 'eps': m.config.norm_eps, 'dense': r(sd['head.dense.weight']), 'norm': r(sd['head.norm.weight']),
           'cls_w': r(sd['classifier.weight']), 'cls_b': r(sd['classifier.bias'])}, open(f'results/{tag}.head.json', 'w'))
print('ok', tag)
