"""v2: fine-tune mmBERT-small on SPEC-aligned data, single-text input (common2.detector_text), left truncation.
usage: ft_mmbert2.py <tag> [epochs] [seed]"""
import json, sys, random, numpy as np, torch, time
from transformers import AutoTokenizer, AutoModelForSequenceClassification, get_linear_schedule_with_warmup
from sklearn.metrics import roc_auc_score
from common2 import detector_text, load_aligned, split
tag = sys.argv[1]; EP = int(sys.argv[2]) if len(sys.argv) > 2 else 4; SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 30
torch.manual_seed(SEED); random.seed(SEED)
tr, va = split(load_aligned()); print('train', len(tr), 'val', len(va), flush=True)
dev = 'mps' if torch.backends.mps.is_available() else 'cpu'
tok = AutoTokenizer.from_pretrained('jhu-clsp/mmBERT-small'); tok.truncation_side = 'left'
model = AutoModelForSequenceClassification.from_pretrained('jhu-clsp/mmBERT-small', num_labels=2).to(dev)
enc = lambda b: tok([detector_text(x['turns']) for x in b], truncation=True, max_length=128, padding=True, return_tensors='pt')
def score(items):
    model.eval(); out = []
    with torch.no_grad():
        for i in range(0, len(items), 64):
            e = {k: v.to(dev) for k, v in enc(items[i:i + 64]).items()}
            out += torch.softmax(model(**e).logits.float(), -1)[:, 1].cpu().tolist()
    return out
opt = torch.optim.AdamW(model.parameters(), lr=3e-5, weight_decay=0.01); BS = 16
steps = EP * ((len(tr) + BS - 1) // BS); sch = get_linear_schedule_with_warmup(opt, int(.06 * steps), steps)
yv = [x['y'] for x in va]; best = -1; t0 = time.time()
for ep in range(EP):
    model.train(); random.shuffle(tr)
    for i in range(0, len(tr), BS):
        b = tr[i:i + BS]; e = {k: v.to(dev) for k, v in enc(b).items()}
        loss = torch.nn.functional.cross_entropy(model(**e).logits, torch.tensor([x['y'] for x in b], device=dev))
        loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step(); sch.step(); opt.zero_grad()
    pv = score(va); auc = roc_auc_score(yv, pv); print(f'epoch {ep+1} val AUC {auc:.4f} ({time.time()-t0:.0f}s)', flush=True)
    if auc > best:
        best = auc; json.dump({'auc': auc, 'epoch': ep + 1, 'ids': [x['id'] for x in va], 'labels': yv, 'scores': pv}, open(f'results/{tag}.synthval.json', 'w'))
        model.save_pretrained(f'results/{tag}.model'); tok.save_pretrained(f'results/{tag}.model')
print('best', best)
