"""HF-level eval of a fine-tuned mmBERT tag on every dev probe, with the shipped input builder (common2.detector_text).
Reports at the given thresholds: Compass (recall, strict FF, howto, critical missed, ES), Sonar dev realistic (recall, FF, hard neg),
terse held-out probes (recall, FF). usage: eval_suite.py <tag> [thr ...]"""
import json, sys, numpy as np, torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from common2 import detector_text
from eval_compass import D
tag = sys.argv[1]; thrs = [float(t) for t in sys.argv[2:]] or [0.2, 0.5]
tok = AutoTokenizer.from_pretrained(f'results/{tag}.model'); m = AutoModelForSequenceClassification.from_pretrained(f'results/{tag}.model').eval()
def score(U):
    out = []
    with torch.no_grad():
        for i in range(0, len(U), 32):
            e = tok([detector_text(u) for u in U[i:i + 32]], truncation=True, max_length=128, padding=True, return_tensors='pt')
            out += torch.softmax(m(**e).logits, -1)[:, 1].tolist()
    return np.array(out)
cU = [[t['text'] for t in d['turns'] if t['role'] == 'user'] for d in D]; cs = score(cU)
yc = np.array([d['emergency'] for d in D]); hw = np.array([d['howto'] for d in D]); strict = (yc == 0) & (hw == 0)
crit = np.array([d.get('sev') == 'critical' for d in D]); es = np.array([d['lang'] == 'es' for d in D])
P = json.load(open('dev/pool.raw.json')); L = [json.loads(l) for l in open('dev/labels.sonar.jsonl')]
ss = score([p['turns'] for p in P]); ys = np.array([x['label'] for x in L]); real = np.array([p['src'] != 'firstaidqa' for p in P]); hn = np.array([x['cls'] == 'hard_negative' for x in L])
T = [json.loads(l) for l in open('probes/terse-live.heldout.jsonl')]; ts = score([t['turns'] for t in T]); yt = np.array([t['label'] for t in T])
json.dump({'compass': cs.tolist(), 'sonar': ss.tolist(), 'terse': ts.tolist()}, open(f'results/{tag}.suite.json', 'w'))
for t in thrs:
    pc, ps, pt = cs >= t, ss >= t, ts >= t
    print(f"{tag} @{t}: Compass rec {(pc&(yc==1)).sum()}/180 strictFF {(pc&strict).sum()}/100 howto {(pc&(hw==1)).sum()}/20 critMiss {(~pc&crit&(yc==1)).sum()} ES {(pc&es&(yc==1)).sum()}/54"
          f" | Sonar realistic rec {(ps&(ys==1)&real).sum()}/246 FF {(ps&(ys==0)&real).sum()}/457 hardneg {(ps&hn).sum()}/57 | terse held-out rec {(pt&(yt==1)).sum()}/20 FF {(pt&(yt==0)).sum()}/10")
