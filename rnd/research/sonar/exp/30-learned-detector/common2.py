"""v2 data (Compass SPEC-aligned) + the single-text input format shared by HF training, GGUF parity and the engine.
Text = up to 3 earlier user turns then the last turn, whitespace collapsed, joined by " | " (a newline is an added token
in mmBERT's HF tokenizer and llama.cpp tokenizes after it differently; " | " gives identical ids on 4,321/4,321 texts) (the engine builds the same string in
src/routing/emergencyHead.ts detectorText). howto=1 items are excluded from training (Compass: tolerated)."""
import json, glob, random, re, os
# v3: DETECTOR_HOWTO=pos trains howto=1 items as positives (product: a first-aid card for 'how do I stop a nosebleed' is wanted;
# Compass: a tolerated fire). DETECTOR_EXTRA=terse adds data/terse-live.jsonl.
HOWTO_POS = os.environ.get('DETECTOR_HOWTO') == 'pos'
MAX_PREV, MAX_CHARS, MAX_TOKENS = 3, 2000, 126   # 126 content tokens + <bos>/<eos> = 128 (training max_length)
CONTROL = re.compile(r"<(?:bos|eos|unk|pad|mask|start_of_turn|end_of_turn)>", re.I)  # typed literals parse as special tokens
_tok = None
def hf_count(text):
    global _tok
    if _tok is None:
        from transformers import AutoTokenizer
        _tok = AutoTokenizer.from_pretrained('jhu-clsp/mmBERT-small')
    return len(_tok(text, add_special_tokens=False)['input_ids'])
def _norm(u): return re.sub(r'\s+', ' ', CONTROL.sub(' ', u)).strip()
def _cut(t):  # left cut to MAX_CHARS code points, then no leading space (llama.cpp would emit '▁▁word', HF '▁word')
    return t[-MAX_CHARS:].lstrip()
def detector_text(user_turns, count=hf_count):
    """Same algorithm as emergencyHead.ts detectorText (Forge review 2026-10-03): up to 3 earlier user turns + the message,
    control literals stripped, whitespace collapsed, ' | '-joined; drop the oldest turns until <= 126 tokens, then the
    message's leading words (fewest that fit, binary search); never starts with a space."""
    prev = [p for p in map(_norm, user_turns[:-1]) if p][-MAX_PREV:]; msg = _norm(user_turns[-1])
    while True:
        t = _cut(' | '.join(prev + [msg]))
        if count(t) <= MAX_TOKENS or not prev: break
        prev = prev[1:]
    if count(t) <= MAX_TOKENS: return t
    words = t.split(' '); lo, hi = 1, len(words) - 1     # drop k leading words; smallest k that fits
    while lo < hi:
        mid = (lo + hi) // 2
        if count(' '.join(words[mid:])) <= MAX_TOKENS: hi = mid
        else: lo = mid + 1
    return ' '.join(words[lo:]).lstrip()
def load_aligned():
    out = []
    files = sorted(glob.glob('data/aligned-*.jsonl')) + (['data/terse-live.jsonl'] if os.environ.get('DETECTOR_EXTRA') == 'terse' else [])
    for p in files:
        for l in open(p):
            try: x = json.loads(l)
            except ValueError: continue
            if {'turns', 'emergency', 'howto'} <= set(x):
                x['y'] = int(x['emergency'] or (HOWTO_POS and x['howto'])); out.append(x)
    return out
def split(items, seed=30, frac=.15):
    items = [x for x in items if HOWTO_POS or not x['howto']]
    rng = random.Random(seed); rng.shuffle(items)
    va = set()
    for lang in ('en', 'pt', 'es'):
        ids = [x['id'] for x in items if x['lang'] == lang]; va |= set(ids[:int(len(ids) * frac)])
    return [x for x in items if x['id'] not in va], [x for x in items if x['id'] in va]
