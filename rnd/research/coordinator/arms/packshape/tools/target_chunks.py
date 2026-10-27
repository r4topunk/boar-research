#!/usr/bin/env python3
"""PACKSHAPE: stats of the original chunks that hold the 20 self-tests' in_pack_facts (0 LLM). -> ../target_chunks.json"""
import json, re, sys
sys.path.insert(0, "<workspace>/rnd/research/coordinator/arms/packshape/tools"); import fbread
D = "<workspace>/rnd/research/coordinator/arms/packshape/"
ST = [json.loads(l) for l in open("<workspace>/rnd/research/packs/selftest/boar-factbook.jsonl")]
A = {a["id"]: a for a in fbread.articles()}; CH = {}
for cid, aid, s, e in fbread.chunks(): CH.setdefault(aid, []).append((cid, s, e))
DIAG = json.load(open(D + "diagnose.json")); out = []
for q in ST:
    aid = q["source"]["article_id"]; a = A[aid]
    for f in q["in_pack_facts"]:
        cid, s, e = CH[aid][f["chunk_index"]]; body = a["text"][s:e]
        rows = [l for l in body.split("\n") if re.match(r"^[A-Z][^:]{1,90}: ", l)]
        nums = re.findall(r"\d[\d,.]*", body)
        out.append(dict(id=q["id"], country=a["title"], fact=f["fact"], quote_in_body=f["quote"] in body, chunk_index=f["chunk_index"], chars=len(body), words=len(body.split()),
                        rows=len(rows), numbers=len(nums), name_in_body=a["title"].lower() in body.lower(), keyfacts=body.startswith("Key facts:"),
                        label=DIAG[q["id"]]["label"], own_kept=DIAG[q["id"]]["kept"], fact_kept=DIAG[q["id"]]["fact"]))
json.dump(out, open(D + "target_chunks.json", "w"), indent=1)
n = len(out); g = lambda k: sum(1 for x in out if x[k])
print("facts", n, "in Key facts chunk", g("keyfacts"), "country name in chunk body", g("name_in_body"), "quote found", g("quote_in_body"))
import statistics as S
print("words median", S.median(x["words"] for x in out), "rows median", S.median(x["rows"] for x in out), "numbers median", S.median(x["numbers"] for x in out))
for x in out: print(x["id"][-3:], x["country"][:18], x["fact"][:28], "ci", x["chunk_index"], "w", x["words"], "rows", x["rows"], "nums", x["numbers"], "name", int(x["name_in_body"]), x["label"])
