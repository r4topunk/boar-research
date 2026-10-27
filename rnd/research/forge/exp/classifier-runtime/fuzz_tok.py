# Tokenizer fuzz: HF mmBERT tokenizer vs llama.cpp (Sonar's GGUF, merge-rank scores) on detector-shaped strings.
import json, glob, random, re, requests
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained('<workspace>/rnd/research/sonar/exp/30-learned-detector/results/mmbert-v2.encoder')
norm = lambda s: re.sub(r'\s+', ' ', s).strip()
random.seed(7)
texts = []
for f in glob.glob('<workspace>/boar-eval/runs/devices/2026-10-02/**/rows.jsonl', recursive=True):
    for l in open(f):
        r = json.loads(l); a = norm(r.get('answer') or ''); q = norm(r.get('query') or '')
        if q: texts.append(('query', q))
        if len(a) > 40:
            texts.append(('answer', a[:300]))
            i = random.randrange(0, max(1, len(a) - 200)); texts.append(('midword', a[i:i + 200]))   # left cut lands mid-word
texts = list(dict.fromkeys(texts))
V = tok.vocab_size
for _ in range(600):   # random vocab-piece soup (rare merges, cross-script)
    ids = [random.randrange(5, V) for _ in range(random.randint(2, 12))]
    s = norm(tok.decode(ids));  s and texts.append(('vocabsoup', s))
extra = ['🦂 picada!!! 😭😭', 'https://www.cdc.gov/scorpions/index.html?x=1', 'R$ 1.234,56 e 3x ao dia', 'Ｈｅｌｐ　ｍｅ', 'Привет, помогите', '救命 我的孩子', 'مساعدة طفلي', 'Ñandú ãõç àèì', 'AAAAAAAAAAAAAAAAAAAA', '...???!!!', 'e-mail: [email removed]', 'tel. 192 / 193 / 911', 'café ☕ ﬁnal ﬂow', 'x²+y³ ≥ ½', '<mask> <bos> <eos> [CLS]', 'ok | ok | ok']
texts += [('extra', t) for t in extra]
bad = []
for kind, t in texts:
    h = tok(t)['input_ids']; g = requests.post('http://localhost:8091/tokenize', json={'content': t, 'add_special': True}).json()['tokens']
    if h != g: bad.append((kind, t, h, g))
from collections import Counter
tot = Counter(k for k, _ in texts); bk = Counter(k for k, *_ in bad)
print('total', len(texts), 'mismatch', len(bad), {k: f"{bk[k]}/{tot[k]}" for k in tot})
for kind, t, h, g in bad[:12]:
    i = next(j for j in range(min(len(h), len(g))) if h[j] != g[j]) if any(a != b for a, b in zip(h, g)) else min(len(h), len(g))
    print(kind, repr(t[:80]), '| HF', tok.convert_ids_to_tokens(h[i:i+4]), '| GGUF', tok.convert_ids_to_tokens(g[i:i+4]))
