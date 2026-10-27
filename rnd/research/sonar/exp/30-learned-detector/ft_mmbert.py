"""(b) Fine-tune a small multilingual encoder (default jhu-clsp/mmBERT-small) as a binary emergency classifier.
Input: text = last user turn, text_pair = earlier user turns joined (empty if none).
usage: ft_mmbert.py <hf id> <tag> [epochs] [seed]"""
import json, sys, glob, random, numpy as np, torch, time
from transformers import AutoTokenizer, AutoModelForSequenceClassification, get_linear_schedule_with_warmup
from sklearn.metrics import roc_auc_score
mid, tag = sys.argv[1], sys.argv[2]
EP = int(sys.argv[3]) if len(sys.argv) > 3 else 4
SEED = int(sys.argv[4]) if len(sys.argv) > 4 else 30
torch.manual_seed(SEED); random.seed(SEED); np.random.seed(SEED)
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
rng = random.Random(30); rng.shuffle(synth)  # same split as embed_head.py
val_ids = set()
for lang in ('en', 'pt', 'es'):
    xs = [x['id'] for x in synth if x['lang'] == lang]; val_ids |= set(xs[:int(len(xs) * .15)])
tr = [x for x in synth if x['id'] not in val_ids]; va = [x for x in synth if x['id'] in val_ids]
dev_ = 'mps' if torch.backends.mps.is_available() else 'cpu'
tok = AutoTokenizer.from_pretrained(mid)
model = AutoModelForSequenceClassification.from_pretrained(mid, num_labels=2).to(dev_)
def enc(items):
    return tok([x['turns'][-1] for x in items], [' | '.join(x['turns'][:-1]) for x in items],
               truncation=True, max_length=160, padding=True, return_tensors='pt')
def score(items, bs=64):
    model.eval(); out = []
    with torch.no_grad():
        for i in range(0, len(items), bs):
            b = {k: v.to(dev_) for k, v in enc(items[i:i + bs]).items()}
            out += torch.softmax(model(**b).logits.float(), -1)[:, 1].cpu().tolist()
    return out
opt = torch.optim.AdamW(model.parameters(), lr=3e-5, weight_decay=0.01)
BS = 16; steps = EP * ((len(tr) + BS - 1) // BS)
sch = get_linear_schedule_with_warmup(opt, int(.06 * steps), steps)
yv = [x['label'] for x in va]; best = (-1, None)
t0 = time.time()
for ep in range(EP):
    model.train(); random.shuffle(tr)
    for i in range(0, len(tr), BS):
        b = tr[i:i + BS]; e = {k: v.to(dev_) for k, v in enc(b).items()}
        loss = torch.nn.functional.cross_entropy(model(**e).logits, torch.tensor([x['label'] for x in b], device=dev_))
        loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step(); sch.step(); opt.zero_grad()
    pv = score(va); auc = roc_auc_score(yv, pv)
    print(f'epoch {ep+1} synth-val AUC {auc:.4f} ({time.time()-t0:.0f}s)', flush=True)
    if auc > best[0]:
        best = (auc, ep + 1); json.dump({'auc': auc, 'epoch': ep + 1, 'ids': [x['id'] for x in va], 'scores': pv}, open(f'results/{tag}.synthval.json', 'w'))
        json.dump(score(dev), open(f'results/{tag}.dev_scores.json', 'w'))
        model.save_pretrained(f'results/{tag}.model'); tok.save_pretrained(f'results/{tag}.model')
print('best', best)
