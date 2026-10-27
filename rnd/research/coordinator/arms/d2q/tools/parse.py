#!/usr/bin/env python3
"""D2Q parse (criterion 83b06185): gen.jsonl -> questions.json {chunk id: [<=4 questions]} + parse stats. usage: parse.py <gen.jsonl> <questions.json>"""
import json, re, sys
CJK = re.compile(r"[぀-ヿ㐀-鿿가-힯]")
def parse(raw):
    out = []
    for l in (raw or "").split("\n"):
        l = re.sub(r"^\s*(?:[-*•]+|\d+[.)]|Q\d*[:.])\s*", "", l).strip().strip('"“”').strip()
        if not l or CJK.search(l) or len(l.split()) < 3: continue
        out.append(l)
    return out[:4]
if __name__ == "__main__":
    rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
    Q = {}; st = dict(rows=len(rows), err=0, cut=0, n4=0, nlt4=0, zero=0, questions=0, dup_within=0)
    for r in rows:
        if r["err"] or r["raw"] is None: st["err"] += 1; continue
        if r["finish"] == "length": st["cut"] += 1
        q = parse(r["raw"]); st["dup_within"] += len(q) - len(set(x.lower() for x in q))
        if not q: st["zero"] += 1; continue
        Q[r["chunk"]] = q; st["questions"] += len(q); st["n4" if len(q) == 4 else "nlt4"] += 1
    json.dump(Q, open(sys.argv[2], "w")); print(json.dumps(st))
