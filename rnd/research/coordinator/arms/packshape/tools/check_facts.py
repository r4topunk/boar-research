#!/usr/bin/env python3
"""PACKSHAPE no-new-facts check (criterion): every number token of a shaped article occurs in its original article text,
and every non-template word of the shaped text occurs in the original (report). python3 -I check_facts.py <shaped dir>"""
import json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import fbread
O = {a["title"]: a for a in fbread.articles()}
num = lambda t: set(re.findall(r"\d[\d,.]*\d|\d", t))
wd = lambda t: set(re.findall(r"[a-z]{3,}", t.lower()))
TPL = wd("is are was were note on continued with capital population area and in a of the factbook entry languages religions people government currency economy climate internet code background date independence")
bad_n, bad_w, n = {}, {}, 0
for l in open(sys.argv[1] + "/factbook.jsonl"):
    d = json.loads(l); o = O[d["title"]]["text"]; n += 1
    d["text"] = re.sub(r"(?m)^(## .*) \(\d+\)$", r"\1", d["text"])  # R6 continuation part numbers are labels, not facts
    extra = num(d["text"]) - num(o)
    if extra: bad_n[d["title"]] = sorted(extra)[:10]
    ew = wd(d["text"]) - wd(o) - TPL
    if ew: bad_w[d["title"]] = sorted(ew)[:10]
r = dict(articles=n, articles_with_new_numbers=len(bad_n), new_numbers=bad_n, articles_with_new_words=len(bad_w), new_words_sample=dict(list(bad_w.items())[:10]))
json.dump(r, open(sys.argv[1] + "/check_facts.json", "w"), indent=1); print(json.dumps({k: v for k, v in r.items() if k != "new_words_sample"})[:1500]); print(r["new_words_sample"])
sys.exit(1 if bad_n else 0)
