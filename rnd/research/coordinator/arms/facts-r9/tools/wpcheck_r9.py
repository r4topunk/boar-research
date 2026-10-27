#!/usr/bin/env python3
"""FACTS-R9 adjudication aid (criterion a4fd8b92: Wikipedia for adjudication only). Parses the two tables of the local
enwiki pack articles "Left- and right-hand traffic" and "Mains electricity by country" (CC BY-SA, read only) and compares
every audited row. Usage: python3 -I wpcheck_r9.py <audit-r9.json> <wp-lrht.txt> <wp-mains.txt> <out.json>"""
import json, sys, re, unicodedata
aud, lr, mains, out = sys.argv[1:5]
fold = lambda s: " ".join(re.sub(r"[^a-z0-9 ]+", " ", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()).replace(" the ", " ").split()).removeprefix("the ")
def table(path, ncols):
    rows = {}
    for l in open(path):
        if not l.startswith("| ") or set(l.strip()) <= set("|- "): continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if len(c) >= ncols: rows.setdefault(fold(re.sub(r"\[.*?\]|\(.*?\)", "", c[0])), c)
    return rows
LR, MA = table(lr, 3), table(mains, 6)
ALIAS = {"people s republic of china": "china", "kingdom of netherlands": "netherlands", "kingdom of denmark": "denmark", "bahamas": "bahamas",
         "gambia": "gambia", "federated states of micronesia": "micronesia", "republic of congo": "congo republic of", "democratic republic of congo": "congo democratic republic of",
         "czech republic": "czech republic", "ivory coast": "ivory coast", "east timor": "timor leste", "sao tome and principe": "sao tome and principe", "palestine": "palestine", "eswatini": "eswatini", "vatican city": "vatican city"}
def find(T, e):
    for n in [e["n"], *e.get("a", [])]:
        k = fold(n); k = ALIAS.get(k, k)
        if k in T: return T[k]
        hits = [v for kk, v in T.items() if kk.startswith(k + " ") or kk == k]
        if len(hits) == 1: return hits[0]
    return None
ents = {e["q"]: e for e in json.load(open(sys.argv[5]))["entities"]} if len(sys.argv) > 5 else {}
A = json.load(open(aud))
res = []
for r in A["rows"]:
    e = ents.get(r["q"], {"n": r["n"]})
    v = {"q": r["q"], "n": r["n"], "field": r["field"], "table": r["table"], "flag": r["flag"], "sampled": r.get("sampled", False)}
    if r["field"] == "drive":
        w = find(LR, e)
        if w: v["wp"] = w[2]; v["wp_agree"] = w[2].upper().startswith({"left": "LHT", "right": "RHT"}[r["table"]])
    elif r["field"] in ("volt", "plug"):
        w = find(MA, e)
        if w:
            if r["field"] == "volt":
                wv = [int(x) for x in re.findall(r"(\d{3})\s*V", w[3])]; wh = [int(x) for x in re.findall(r"(50|60)\s*Hz", w[5])]
                volts, hz = r["table"]
                v["wp"] = [w[3], w[5]]
                v["wp_agree"] = bool(wv) and all(any(abs(t - x) <= 10 for x in wv) for t in volts) and (not hz or not wh or set(hz) <= set(wh))
            else:
                wl = set(re.findall(r"\b([A-N])\b", w[1]))
                tl = set(re.findall(r"Type ([A-N])\b", " ".join(r["table"]))) | ({"D", "G", "M"} if any("British-related" in p for p in r["table"]) else set()) | ({"D", "M"} if any("D/M" in p for p in r["table"]) else set())
                v["wp"] = w[1]; v["wp_agree"] = bool(wl) and bool(tl & wl); v["wp_extra_in_table"] = sorted(tl - wl); v["wp_missing_in_table"] = sorted(wl - tl)
    res.append(v)
json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
from collections import Counter
print(Counter((x["field"], x.get("wp_agree", "no-wp")) for x in res))
