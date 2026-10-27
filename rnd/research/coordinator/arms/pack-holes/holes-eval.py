#!/usr/bin/env python3 -I
"""usage: holes-eval.py <render-whitelist.jsonl> : strong-hole share per ~1000-char window, builder cleaner vs whitelist renderer."""
import sys, json, os, importlib.util
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("holes", os.path.join(here, "holes.py")); h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
def windows(t, n=1000):
    return [t[i:i + n] for i in range(0, len(t), n)]
def rate(texts):
    tot = hit = fact = 0; per = {}
    for t in texts:
        for w in windows(t):
            tot += 1
            hs = [k for k in h.STRONG if h.PATTERNS[k].search(w)]
            if hs: hit += 1
            if any(k in h.FACT for k in hs): fact += 1
            for k in hs: per[k] = per.get(k, 0) + 1
    return tot, hit, fact, per
rows = [json.loads(l) for l in open(sys.argv[1])]
for key in ("base", "wl"):
    tot, hit, fact, per = rate(r[key] for r in rows)
    print(f"{key:5} windows {tot} strong {hit} ({hit/tot:.2%}) fact {fact} ({fact/tot:.2%}) {per}")
# a few before/after examples
import random; random.seed(1); n = 0
for r in rows:
    if r["base"] != r["wl"] and n < 6:
        b, w = r["base"], r["wl"]
        for k in h.FACT + ["empty_paren"]:
            m = h.PATTERNS[k].search(b)
            if m and not h.PATTERNS[k].search(w[max(0, m.start() - 200):m.end() + 200]):
                print("BASE:", b[max(0, m.start() - 50): m.end() + 30].replace("\n", " ")); 
                key = b[max(0, m.start() - 30): m.start()]
                j = w.find(key)
                print("WL  :", (w[j: j + 90] if j >= 0 else "?").replace("\n", " ")); n += 1; break
