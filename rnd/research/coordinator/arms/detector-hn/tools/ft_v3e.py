#!/usr/bin/env python3
"""DETECTOR-FT2 (v3e): ft_v3d.py with (a) every epoch checkpoint saved to results/<tag>.e<k>.model + results/<tag>.e<k>.synthval.json, (b) optional positive-class CE weight (posw, default 1 = v3b recipe). Original doc follows.
DETECTOR-FT step 1b: v3b's recipe (sonar/exp/30-learned-detector/ft_mmbert2.py, unchanged hyper-parameters) on ft/train.jsonl
(v3b's 3,153 + 3,129 hard negatives) with v3b's val 555: jhu-clsp/mmBERT-small AutoModelForSequenceClassification(2), left truncation,
max_length 128, AdamW lr 3e-5 wd 0.01, batch 16, linear schedule 6 % warmup, clip 1.0, CE, 3 epochs (as v3b ran), seed 30, MPS,
best epoch by synthetic-val AUC. Only difference vs ft_mmbert2: texts are precomputed (same detector_text) and the train list is longer.
usage: ft_v3e.py <tag> <dir with train.jsonl val.jsonl> [posw=1] [epochs=3] [seed=30]"""
import json, sys, random, time, platform, torch, transformers
from transformers import AutoTokenizer, AutoModelForSequenceClassification, get_linear_schedule_with_warmup
from sklearn.metrics import roc_auc_score
tag, d = sys.argv[1], sys.argv[2]; POSW = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0; EP = int(sys.argv[4]) if len(sys.argv) > 4 else 3; SEED = int(sys.argv[5]) if len(sys.argv) > 5 else 30
torch.manual_seed(SEED); random.seed(SEED)
rd = lambda p: [json.loads(l) for l in open(p) if l.strip()]
tr, va = rd(f'{d}/train.jsonl'), rd(f'{d}/val.jsonl'); print('train', len(tr), 'val', len(va), flush=True)
dev = 'mps' if torch.backends.mps.is_available() else 'cpu'
tok = AutoTokenizer.from_pretrained('jhu-clsp/mmBERT-small'); tok.truncation_side = 'left'
model = AutoModelForSequenceClassification.from_pretrained('jhu-clsp/mmBERT-small', num_labels=2).to(dev)
enc = lambda b: tok([x['text'] for x in b], truncation=True, max_length=128, padding=True, return_tensors='pt')
def score(items):
    model.eval(); out = []
    with torch.no_grad():
        for i in range(0, len(items), 64):
            e = {k: v.to(dev) for k, v in enc(items[i:i + 64]).items()}
            out += torch.softmax(model(**e).logits.float(), -1)[:, 1].cpu().tolist()
    return out
CW = torch.tensor([1.0, POSW], device=dev)
opt = torch.optim.AdamW(model.parameters(), lr=3e-5, weight_decay=0.01); BS = 16
steps = EP * ((len(tr) + BS - 1) // BS); sch = get_linear_schedule_with_warmup(opt, int(.06 * steps), steps)
yv = [x['y'] for x in va]; best = -1; t0 = time.time(); log = {'tag': tag, 'device': dev, 'seed': SEED, 'epochs': EP, 'lr': 3e-5, 'wd': 0.01, 'bs': BS, 'warmup': .06, 'clip': 1.0, 'posw': POSW,
      'max_length': 128, 'n_train': len(tr), 'n_val': len(va), 'torch': torch.__version__, 'transformers': transformers.__version__, 'python': platform.python_version(), 'auc': []}
for ep in range(EP):
    model.train(); random.shuffle(tr)
    for i in range(0, len(tr), BS):
        b = tr[i:i + BS]; e = {k: v.to(dev) for k, v in enc(b).items()}
        loss = torch.nn.functional.cross_entropy(model(**e).logits, torch.tensor([x['y'] for x in b], device=dev), weight=CW)
        loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step(); sch.step(); opt.zero_grad()
    pv = score(va); auc = roc_auc_score(yv, pv); log['auc'].append(round(auc, 5)); print(f'epoch {ep+1} val AUC {auc:.4f} ({time.time()-t0:.0f}s)', flush=True)
    json.dump({'auc': auc, 'epoch': ep + 1, 'ids': [x['id'] for x in va], 'labels': yv, 'scores': pv}, open(f'results/{tag}.e{ep+1}.synthval.json', 'w'))
    model.save_pretrained(f'results/{tag}.e{ep+1}.model'); tok.save_pretrained(f'results/{tag}.e{ep+1}.model')
    if auc > best: best = auc; log['best_epoch'] = ep + 1
log['best_auc'] = round(best, 5); log['wall_s'] = round(time.time() - t0); json.dump(log, open(f'results/{tag}.train.json', 'w'), indent=1); print('best', best)
