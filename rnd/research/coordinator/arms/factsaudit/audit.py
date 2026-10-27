#!/usr/bin/env python3
"""FACTSAUDIT (criterion 9710b996): table countries vs the Factbook archive. Usage: python3 -I audit.py <facts.json> <factbook_dir> <out.json>"""
import json, sys, re, unicodedata, glob, os
facts, fbdir, out = sys.argv[1:4]
fold = lambda s: re.sub(r"[^a-z0-9 ]+", " ", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()).split()
key = lambda s: " ".join(w for w in fold(s) if w != "the")
def txt(d, *path):
    for p in path:
        if not isinstance(d, dict) or p not in d: return ""
        d = d[p]
    return d.get("text", "") if isinstance(d, dict) else str(d)
def num(s):
    m = re.search(r"(\d[\d,]*(?:\.\d+)?)\s*(million|billion)?", s.replace(" ", " "))
    if not m: return None
    v = float(m.group(1).replace(",", "")); return v * {"million": 1e6, "billion": 1e9}.get(m.group(2), 1)
fb = {}
for f in glob.glob(os.path.join(fbdir, "*", "*.json")):
    if "/meta/" in f: continue
    d = json.load(open(f)); g = d.get("Government", {})
    names = {txt(g, "Country name", "conventional short form"), txt(g, "Country name", "conventional long form")}
    rec = {"file": os.path.relpath(f, fbdir), "capital": txt(g, "Capital", "name"),
           "currency": txt(d, "Economy", "Exchange rates", "Currency") or txt(d, "Economy", "Exchange rates"),
           "pop": num(txt(d, "People and Society", "Population", "total") or txt(d, "People and Society", "Population")),
           "area": num(txt(d, "Geography", "Area", "total ") or txt(d, "Geography", "Area", "total"))}
    for n in names:
        if n and n.lower() != "none": fb.setdefault(key(n), rec)
rows, unmatched = [], []
for e in json.load(open(facts))["entities"]:
    if e.get("k") != "country": continue
    r = next((fb[key(n)] for n in [e["n"], *e.get("a", [])] if key(n) in fb), None)
    if not r: unmatched.append(e["n"]); continue
    flags = {}
    capw = {w for w in fold(r["capital"]) if len(w) >= 4}
    if e.get("cap") and capw and not any(capw & {w for w in fold(c) if len(w) >= 4} for c in e["cap"]): flags["capital"] = [e.get("cap"), r["capital"][:120]]
    if not e.get("cap") and r["capital"]: flags["capital-missing"] = [None, r["capital"][:120]]
    ct = " ".join(fold(r["currency"]))
    heads = [re.sub(r"s$", "", fold(c)[-1]) for c in e.get("cur", []) if fold(c)]
    if heads and ct and not any(h in ct for h in heads): flags["currency"] = [e.get("cur"), r["currency"][:120]]
    pop = e["pop"][0] if isinstance(e.get("pop"), list) else e.get("pop")
    if pop and r["pop"] and not 0.80 <= pop / r["pop"] <= 1.25: flags["population"] = [e["pop"], r["pop"]]
    if e.get("area") and r["area"] and not 0.90 <= e["area"] / r["area"] <= 1.11: flags["area"] = [e["area"], r["area"]]
    if flags: rows.append({"q": e["q"], "n": e["n"], "fb": r["file"], "flags": flags})
json.dump({"matched": 197 - len(unmatched), "unmatched": unmatched, "flagged": rows}, open(out, "w"), indent=1, ensure_ascii=False)
from collections import Counter
print("matched", 197 - len(unmatched), "unmatched", len(unmatched), "flagged rows", len(rows), Counter(k for r in rows for k in r["flags"]))
