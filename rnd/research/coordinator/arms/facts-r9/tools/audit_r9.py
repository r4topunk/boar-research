#!/usr/bin/env python3
"""FACTS-R9 audit (criterion FACTS-R9-criterion.md a4fd8b92). Part A full scan + Part B seeded sample of the r9 travel fields
vs S1 (Factbook pack) and S2 (Wikivoyage pack). Usage: python3 -I audit_r9.py <facts.json> <factbook.sqlite> <wikivoyage.sqlite> <out.json>
Output: per country x field: table value, reference evidence (snippets), flag (bool), sampled (bool). Adjudication is by hand."""
import json, sys, re, sqlite3, subprocess, random
facts, fbp, wvp, out = sys.argv[1:5]

def opener(path):
    db = sqlite3.connect(path); cache = {}
    def art(title):
        a = db.execute("select block_id,off,len from articles where title = ? collate nocase", (title,)).fetchone()
        if not a:
            r = db.execute("select * from redirects limit 0").description and None
            return None
        if a[0] not in cache:
            z = db.execute("select zdata from blocks where id=?", (a[0],)).fetchone()[0]
            cache[a[0]] = subprocess.run(["zstd", "-dc"], input=z, capture_output=True, check=True).stdout
        return cache[a[0]][a[1]:a[1] + a[2]].decode("utf8", errors="replace").replace("&nbsp;", " ")
    return art
fb, wv = opener(fbp), opener(wvp)
first = lambda f, names: next(((n, t) for n in names if (t := f(n))), (None, None))
snip = lambda t, m, w=160: re.sub(r"\s+", " ", t[max(0, m.start() - w):m.end() + w])

SIDE = {s: re.compile(rf"(?i)\b(drives? on the {s}|driving is on the {s}|drive on the {s}[- ]hand|traffic (?:drives |moves |keeps )?(?:on the )?{s}|{s}[- ]hand traffic|keep {s}\b|driving on the {s})") for s in ("left", "right")}
VOLT = re.compile(r"(?i)\b(\d{3})\s*(?:-|–|/)?\s*(?:v\b|volts?\b|-volt)")
HZ = re.compile(r"(?i)\b(50|60)\s*(?:hz|hertz|cycles)")
PLUG = re.compile(r"(?i)\btypes?\s+([A-N](?:\s*(?:,|/|and|or|&)\s*[A-N])*)\b")
CALL_WV = re.compile(r"(?i)(?:country code (?:is |of |for \w+ is )?\+?(\d{1,4})|\+(\d{1,4})[ -]\d)")
CALL_FB = re.compile(r"Diplomatic representation from the US \(telephone\):\s*\[(\d+)\]")
LETTERS = lambda p: set(re.findall(r"Type ([A-N])\b", p)) | ({"D", "G", "M"} if "British-related" in p else set()) | ({"D", "M"} if "D/M" in p else set())

rows = []
countries = [e for e in json.load(open(facts))["entities"] if e["k"] == "country"]
unmatched_wv, unmatched_fb = [], []
for e in countries:
    names = [e["n"], *e.get("a", [])]
    wn, w = first(wv, names); fn, f = first(fb, names)
    if not w: unmatched_wv.append(e["n"])
    if not f: unmatched_fb.append(e["n"])
    w = w or ""; f = f or ""
    # drive
    if "drive" in e:
        ev = {s: [snip(w, m) for m in SIDE[s].finditer(w)][:3] for s in SIDE}
        opp = "left" if e["drive"] == "right" else "right"
        flag = (bool(ev[opp]) and not ev[e["drive"]]) or (not ev["left"] and not ev["right"])
        rows.append({"q": e["q"], "n": e["n"], "field": "drive", "table": e["drive"], "ref": ev, "flag": flag})
    if "call" in e:
        fbc = CALL_FB.findall(f)
        wvc = sorted({a or b for a, b in CALL_WV.findall(w)})
        codes = [c.replace(" ", "") for c, _ in e["call"]]
        if fbc: flag = not any(c.startswith("+" + fbc[0]) for c in codes)
        elif wvc: flag = not any(("+" + x) in codes or c.startswith("+" + x) for x in wvc for c in codes)
        else: flag = True
        rows.append({"q": e["q"], "n": e["n"], "field": "call", "table": e["call"], "ref": {"S1": fbc[:2], "S2": wvc[:6],
                     "S2snip": [snip(w, m, 80) for m in CALL_WV.finditer(w)][:2]}, "flag": flag})
    if "volt" in e:
        vs = [int(x) for x in VOLT.findall(w)]
        hz = sorted({int(x) for x in HZ.findall(w)})
        flag = not any(abs(v - t) <= 10 for v in vs for t in e["volt"])
        hflag = bool(e.get("hz")) and bool(hz) and not set(hz) & set(e["hz"])
        rows.append({"q": e["q"], "n": e["n"], "field": "volt", "table": [e["volt"], e.get("hz")], "ref": {"S2volts": sorted(set(vs)), "S2hz": hz,
                     "S2snip": [snip(w, m, 100) for m in VOLT.finditer(w)][:2]}, "flag": flag or hflag, "hzflag": hflag})
    if "plug" in e:
        got = set()
        for m in PLUG.finditer(w): got |= set(re.findall(r"[A-N]", m.group(1).upper()))
        flag = not (LETTERS(" ".join(e["plug"])) & got)
        rows.append({"q": e["q"], "n": e["n"], "field": "plug", "table": e["plug"], "ref": {"S2letters": sorted(got),
                     "S2snip": [snip(w, m, 100) for m in PLUG.finditer(w)][:2]}, "flag": flag})
rnd = random.Random(919)
for fld in ("drive", "call", "volt", "plug"):
    pool = sorted((r for r in rows if r["field"] == fld), key=lambda r: r["q"])
    for r in rnd.sample(pool, 12): r["sampled"] = True
from collections import Counter
json.dump({"unmatched_wv": unmatched_wv, "unmatched_fb": unmatched_fb, "rows": rows}, open(out, "w"), indent=1, ensure_ascii=False)
print("rows", len(rows), "wv unmatched", len(unmatched_wv), unmatched_wv, "fb unmatched", len(unmatched_fb))
print("flags", Counter(r["field"] for r in rows if r["flag"]), "sampled", sum(1 for r in rows if r.get("sampled")),
      "hz flags", sum(1 for r in rows if r.get("hzflag")))
