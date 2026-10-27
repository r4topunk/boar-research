#!/usr/bin/env python3
"""FIRSTAID wording check (criterion): strip the inserted '<topic>: ' prefixes and repeated heading lines -> token sequence must
equal the original's for every article; every shaped token must exist in the source article. python3 -I check_words_fa.py <dir>"""
import json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import fbread, shape_firstaid as S
O = [a["text"] for a in fbread.articles(S.F)]  # in article order (titles repeat across sources); T = json.load(open(sys.argv[1] + "/topics.json"))
tok = lambda t: re.findall(r"\S+", t)
bad, newtok, n = [], [], 0
for l in open(sys.argv[1] + "/firstaid.jsonl"):
    d = json.loads(l); n += 1; tp = S.topic_of(d["title"]); t = d["text"]
    def dedup(x):  # drop a heading line equal to the current section heading (F3 repeats); applied to BOTH texts
        seen, lines = [], []
        for ln in x.split("\n"):
            if re.match(r"^#{1,6} ", ln):
                if seen and ln == seen[-1] and not ln.startswith("# "): continue
                seen.append(ln)
            lines.append(ln)
        return "\n".join(lines)
    t2 = dedup(t).replace(tp + ": ", "")
    o = O[n - 1]
    o2 = dedup(o).replace(tp + ": ", "")  # an original sentence that already started with '<topic>: ' is stripped the same way
    if tok(t2) != tok(o2): bad.append(d["title"])
    ot = set(tok(o)) | set(tok(tp + ":"))
    nt = set(tok(t)) - ot
    if nt: newtok.append((d["title"], sorted(nt)[:5]))
r = dict(articles=n, token_sequence_mismatch=len(bad), mismatch_titles=bad[:20], articles_with_new_tokens=len(newtok), new_tokens=newtok[:20])
json.dump(r, open(sys.argv[1] + "/check_words.json", "w"), indent=1); print(json.dumps(r)[:1500]); sys.exit(1 if bad or newtok else 0)
