#!/usr/bin/env python3
"""Raw WDQS JSON (data/raw, from fetch_wikidata.py) -> the engine's compact table src/rag/facts.v1.json.
Usage: python3 -I build_asset.py <raw_dir> <out.json>. Deterministic; rules: population = latest dated statement (any
non-deprecated rank); other quantities: preferred rank, else the largest value (area/length/height/elevation/depth);
ended statements (P582) dropped; BCE dates dropped; plug items mapped to IEC letter names."""
import json, sys
from pathlib import Path

raw, out = Path(sys.argv[1]), Path(sys.argv[2])
SNAPSHOT = "2026-10-06"
L = lambda name: json.loads((raw / f"{name}.json").read_text())["results"]["bindings"]
qid = lambda iri: iri.rsplit("/", 1)[1]
val = lambda b, k: b[k]["value"] if k in b else None

def top(name, n):
    return [qid(b["item"]["value"]) for b in L(name)][:n]

kind = {}
def put(ids, k):
    for i in ids:
        kind.setdefault(i, k)
put(top("sel_countries", 1000), "country")
caps = [qid(b["item"]["value"]) for b in L("sel_capitals")]
put(top("sel_cities", 300) + caps, "city")
put(top("sel_lakes", 100), "lake")
put(top("sel_rivers", 100), "river")
put(top("sel_mountains", 100), "mountain")
put(top("sel_buildings", 100), "building")
put(["Q155", "Q159", "Q189"], "country"); put(["Q12495"], "building"); put(["Q5513"], "lake"); put(["Q7296"], "mountain")
put(["Q5086"], "other"); put(["Q8613"], "event"); put(["Q37922"], "award")

lab, qty, itm, tim = {}, {}, {}, {}
for f in sorted(raw.glob("lab_*.json")):
    for b in json.loads(f.read_text())["results"]["bindings"]:
        lab[qid(b["item"]["value"])] = b
for f in sorted(raw.glob("qty_*.json")):
    for b in json.loads(f.read_text())["results"]["bindings"]:
        qty.setdefault((qid(b["item"]["value"]), qid(b["prop"]["value"])), []).append(b)
for f in sorted(raw.glob("pop_*.json")):
    for b in json.loads(f.read_text())["results"]["bindings"]:
        qty.setdefault((qid(b["item"]["value"]), "P1082"), []).append(b)
for f in sorted(raw.glob("itm_*.json")):
    for b in json.loads(f.read_text())["results"]["bindings"]:
        itm.setdefault((qid(b["item"]["value"]), qid(b["prop"]["value"])), []).append(b)
for f in sorted(raw.glob("tim_*.json")):
    for b in json.loads(f.read_text())["results"]["bindings"]:
        tim.setdefault((qid(b["item"]["value"]), qid(b["prop"]["value"])), []).append(b)

# IEC letter names for Wikidata's plug items (World Plugs / IEC TR 60083 naming)
PLUG = {"Europlug": "Type C (Europlug)", "Schuko": "Type F (Schuko)", "BS 1363": "Type G (BS 1363)", "NEMA 1-15": "Type A (NEMA 1-15)",
        "NEMA 5-15": "Type B (NEMA 5-15)", "AC power plugs and sockets: British and related types": "British-related types (D/G/M)",
        "AS/NZS 3112": "Type I (AS/NZS 3112)", "BS 546": "Type D/M (BS 546)", "SN 441011": "Type J (SN 441011)",
        "IEC 60906-1": "Type N (IEC 60906-1)"}
pref = lambda rows: [r for r in rows if r["rank"]["value"].endswith("PreferredRank")] or rows

def number(i, p, scale=1.0, latest=False):
    if latest:
        # population: the latest dated figure over all non-deprecated statements (the preferred rank is often stale:
        # Iceland preferred 2019 vs a 2022 statement); ties -> preferred rank
        rows = qty.get((i, p), [])
        if not rows:
            return None
        rows = sorted(rows, key=lambda r: (val(r, "time") or "", r["rank"]["value"].endswith("PreferredRank"), float(r["amount"]["value"])))
        r = rows[-1]
        t = val(r, "time")
        return [round(float(r["amount"]["value"])), int(t[:4]) if t else None]
    rows = pref(qty.get((i, p), []))
    if not rows:
        return None
    v = max(float(r["amount"]["value"]) for r in rows) * scale
    return round(v, 1) if v < 100 else round(v)

def labels(i, p, keep_all=True):
    rows = [r for r in itm.get((i, p), []) if "end" not in r]
    rows = pref(rows) if not keep_all else rows
    out = []
    for r in rows:
        l = val(r, "valLabel")
        if l and not (l.startswith("Q") and l[1:].isdigit()) and l not in out:
            out.append(l)
    return sorted(out) if keep_all else out

def when(i, props):
    for p in props:
        rows = pref(tim.get((i, p), []))
        rows = [r for r in rows if not r["t"]["value"].startswith("-")]
        if rows:
            r = sorted(rows, key=lambda r: r["t"]["value"])[0]
            t, prec = r["t"]["value"], int(r["prec"]["value"])
            return t[:10] if prec >= 11 else t[:4]
    return None

aw = {}
for b in L("award_winners"):
    y = b["time"]["value"][:4]
    w = val(b, "wLabel")
    if w and w not in aw.setdefault(y, []):
        aw[y].append(w)

ents = []
for i, k in sorted(kind.items(), key=lambda x: (x[1], x[0])):
    b = lab.get(i)
    if not b or "label" not in b:
        continue
    name = b["label"]["value"]
    aliases = [a for a in (val(b, "aliases") or "").split("|") if a and a != name and (len(a) >= 3 or a.isupper())]
    e = {"q": i, "n": name}
    if aliases: e["a"] = sorted(set(aliases))
    e["k"] = k
    if val(b, "desc"): e["d"] = val(b, "desc")
    pop = number(i, "P1082", latest=True)
    if pop and k in ("country", "city"): e["pop"] = pop
    area = number(i, "P2046", 1e-6)
    if area and k in ("country", "city", "lake"): e["area"] = area
    if k in ("mountain", "city", "lake"):
        el = number(i, "P2044")
        if el: e["elev"] = el
    if k in ("building", "other"):
        h = number(i, "P2048")
        if h: e["height"] = h
    if k in ("river", "other"):
        ln = number(i, "P2043", 1e-3)
        if ln: e["len"] = ln
    if k == "lake":
        d = number(i, "P4511")
        if d: e["depth"] = d
    if k == "country":
        for key, p in (("cap", "P36"), ("cur", "P38")):
            v = labels(i, p, keep_all=False)
            if v: e[key] = v
        for key, p in (("lang", "P37"), ("cont", "P30"), ("bord", "P47"), ("plug", "P2853")):
            v = labels(i, p)
            if v: e[key] = v
        if "plug" in e: e["plug"] = sorted({PLUG.get(x, x) for x in e["plug"]})
        volts = sorted({round(float(r["amount"]["value"])) for r in qty.get((i, "P2884"), [])})
        if volts: e["volt"] = volts
        hz = sorted({round(float(r["amount"]["value"])) for r in qty.get((i, "P2885"), [])})
        if hz: e["hz"] = hz
    if k in ("country", "city", "building", "other", "event"):
        inc = when(i, ["P571", "P580", "P1619", "P729"])
        if inc: e["inc"] = inc
        end = when(i, ["P576", "P582"])
        if end: e["end"] = end
    if k == "event":
        loc = labels(i, "P276")
        if loc: e["loc"] = loc
    if k == "award" and i == "Q37922":
        e["win"] = {y: sorted(v) for y, v in sorted(aw.items())}
    if k == "mountain":
        t = labels(i, "P31")
        if t: e["t"] = t
    if k in ("mountain", "lake", "river", "building", "city", "other"):
        c = labels(i, "P17")
        if c: e["ctry"] = c
    ents.append(e)

doc = {"snapshot": SNAPSHOT, "source": "Wikidata (CC0 1.0), WDQS snapshot " + SNAPSHOT + "; builder rnd/research/coordinator/arms/facts/tools/build_asset.py",
       "entities": ents}
out.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")))
print(len(ents), "entities", out.stat().st_size, "bytes", {k: sum(1 for e in ents if e["k"] == k) for k in sorted(set(kind.values()))})
