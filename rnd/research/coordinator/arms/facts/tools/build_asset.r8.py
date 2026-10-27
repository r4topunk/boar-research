#!/usr/bin/env python3
"""r6 (2026-10-06, FACTS-r6-criterion.md A): coverage expansion from the sel_*_r6 selections (cities >= 300k, the 500
highest mountains + all with prominence >= 1,500 m, 300 longest rivers, 300 tallest skyscrapers + 300 tallest towers, 100
highest dams (kind "dam"), 200 largest lakes), unioned with the r2 selection; the r2 gates unchanged (r2 kept as build_asset.r2.py).
"Top N" counts only selection rows whose selection value passes the r2 unit range table.
r6 data-review gates (DATA-REVIEW-r6.md): (a) a place's country list (P17) keeps only current table countries when it names
at least one (drops Russian Empire / Soviet Union / Kingdom of Egypt …); (b) an entity queried in homonym_r6_*.json (the
r6-new entities) is dropped when another Wikidata item with the exact same English label has more sitelinks (Toyota → the
company, Gwangju → the metropolitan city, London → not London, Ontario); (c) a water tower's height above 200 m is dropped.
r2 (2026-10-06): + the DATA-REVIEW.md §4 data gates (see GATES below; r1 kept as build_asset.r1.py).
Raw WDQS JSON (data/raw, from fetch_wikidata.py) -> the engine's compact table src/rag/facts.v1.json.
Usage: python3 -I build_asset.py <raw_dir> <out.json>. Deterministic; rules: population = latest dated statement (any
non-deprecated rank); other quantities: preferred rank, else the largest value (area/length/height/elevation/depth);
ended statements (P582) dropped; BCE dates dropped; plug items mapped to IEC letter names.
r7 (2026-10-18, maintainer report): WDQS returned some labels as bare QIDs (the euro Q4916 on 30 countries, Kipling 1907,
5 capitals, 36 borders), which the label filter dropped; data/labels-r7.json (wbgetentities, en) now fills them in. Currency:
an ended or never-issued legal tender, or a Caribbean-only one for the Kingdom of the Netherlands, is dropped (CUR_ENDED), and a country with no
preferred-rank currency and more than 3 current ones gets no currency entry (Zimbabwe: 9), so the model answers instead."""
import json, re, sys, unicodedata
from pathlib import Path

raw, out = Path(sys.argv[1]), Path(sys.argv[2])
SNAPSHOT = "2026-10-06"
L = lambda name: bindings(raw / f"{name}.json")
qid = lambda iri: iri.rsplit("/", 1)[1]
val = lambda b, k: b[k]["value"] if k in b else None
_lf = raw.parent / "labels-r7.json"
LABELS = json.loads(_lf.read_text())["labels"] if _lf.exists() else {}

def fixb(b):
    """r7: a label that came back as its bare QID gets the wbgetentities English label, when there is one."""
    for k, v in b.items():
        if k.endswith("Label") and re.fullmatch(r"Q\d+", v.get("value", "")) and v["value"] in LABELS:
            v["value"] = LABELS[v["value"]]
    return b

def bindings(f):
    return [fixb(b) for b in json.loads(f.read_text())["results"]["bindings"]]

def top(name, n):
    return [qid(b["item"]["value"]) for b in L(name)][:n]

def top_in_range(name, n, var, scale, hi):
    """r6: the first n selection rows whose selection value (SI units, scaled) is inside the r2 range table."""
    out = []
    for b in L(name):
        v = float(b[var]["value"]) * scale
        if 0 < v <= hi:
            out.append(qid(b["item"]["value"]))
    return out[:n]

kind = {}
def put(ids, k):
    for i in ids:
        kind.setdefault(i, k)
put(top("sel_countries", 1000), "country")
caps = [qid(b["item"]["value"]) for b in L("sel_capitals")]
put(top("sel_cities", 300) + caps + top("sel_cities_r6", 100000), "city")
put(top("sel_lakes", 100) + top_in_range("sel_lakes_r6", 200, "v", 1e-6, 400_000), "lake")
put(top("sel_rivers", 100) + top_in_range("sel_rivers_r6", 300, "v", 1e-3, 7_000), "river")
put(top("sel_mountains", 100) + top_in_range("sel_mountains_elev_r6", 500, "v", 1, 9_000) + top("sel_mountains_prom_r6", 100000), "mountain")
put(top("sel_buildings", 100) + top_in_range("sel_buildings_r6", 300, "v", 1, 900) + top_in_range("sel_towers_r6", 300, "v", 1, 900), "building")
put(top_in_range("sel_dams_r6", 100, "v", 1, 350), "dam")
put(["Q155", "Q159", "Q189"], "country"); put(["Q12495"], "building"); put(["Q5513"], "lake"); put(["Q7296"], "mountain")
put(["Q5086"], "other"); put(["Q8613"], "event"); put(["Q37922"], "award")

lab, qty, itm, tim = {}, {}, {}, {}
for f in sorted(raw.glob("lab_*.json")):
    for b in bindings(f):
        lab[qid(b["item"]["value"])] = b
for f in sorted(raw.glob("qty_*.json")):
    for b in bindings(f):
        qty.setdefault((qid(b["item"]["value"]), qid(b["prop"]["value"])), []).append(b)
for f in sorted(raw.glob("pop_*.json")):
    for b in bindings(f):
        qty.setdefault((qid(b["item"]["value"]), "P1082"), []).append(b)
for f in sorted(raw.glob("itm_*.json")):
    for b in bindings(f):
        itm.setdefault((qid(b["item"]["value"]), qid(b["prop"]["value"])), []).append(b)
for f in sorted(raw.glob("tim_*.json")):
    for b in bindings(f):
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
        # r2 gate 2: drop undated, zero and year < 1000 rows; the latest must be dated >= 2020, else no population
        rows = [r for r in qty.get((i, p), []) if val(r, "time") and int(val(r, "time")[:4]) >= 1000 and float(r["amount"]["value"]) > 0]
        if not rows:
            GATES["pop: no valid dated row"] += 1 if (i, p) in qty else 0
            return None
        # r8 (FACTSAUDIT): a round figure (multiple of 100,000) dated in the snapshot year is a projection or a bulk edit
        # (Tunisia 37,100,000, Togo 12,400,000, Bahrain 2,700,000 for 2026); dropped when the item has other rows
        snap = int(SNAPSHOT[:4])
        bulk = [r for r in rows if int(val(r, "time")[:4]) >= snap and float(r["amount"]["value"]) % 100000 == 0]
        if bulk and len(bulk) < len(rows):
            GATES["pop: round snapshot-year figure dropped (r8)"] += 1
            rows = [r for r in rows if r not in bulk]
        rows = sorted(rows, key=lambda r: (val(r, "time") or "", r["rank"]["value"].endswith("PreferredRank"), float(r["amount"]["value"])))
        r = rows[-1]
        y = int(val(r, "time")[:4])
        if y < 2020:
            GATES["pop: latest dated < 2020"] += 1
            return None
        return [round(float(r["amount"]["value"])), y]
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

# r8 (FACTSAUDIT): areas whose Wikidata value misleads the plain question ("how big is Yemen / Denmark")
AREA_FIX = {"Q805": 527968, "Q756617": 42933}  # Yemen: the standard total area; Kingdom of Denmark: Denmark proper (the item adds Greenland and the Faroes)

# r8: emergency phone numbers (P2852) with their service (P366 "has use"), ended statements dropped; data/raw/emerg_r8_qual.json (WDQS 2026-10-19)
EMERG = {}
_ef = raw / "emerg_r8_qual.json"
if _ef.exists():
    _ended = set()
    for b in json.loads(_ef.read_text())["results"]["bindings"]:
        if b.get("pq", {}).get("value", "").endswith("/P582"): _ended.add((qid(b["c"]["value"]), b["numLabel"]["value"]))
    for b in json.loads(_ef.read_text())["results"]["bindings"]:
        c, n = qid(b["c"]["value"]), b["numLabel"]["value"]
        if (c, n) in _ended or not re.fullmatch(r"[0-9]{2,5}", n): continue
        use = b["qvLabel"]["value"] if b.get("pq", {}).get("value", "").endswith("/P366") else ""
        cur = EMERG.setdefault(c, {}); cur.setdefault(n, set())
        if use and not re.fullmatch(r"Q\d+", use): cur[n].add(use)

# r7: (country QID, currency label) pairs a traveller's "what currency does X use" answer must not carry
CUR_ENDED = {
    ("Q792", "Bitcoin"),  # El Salvador: Bitcoin no longer legal tender (Legislative Assembly reform, 2025-01-29)
    ("Q709", "SOV"),  # Marshall Islands: a planned digital token, never issued as legal tender
    ("Q29999", "Aruban florin"), ("Q29999", "United States dollar"), ("Q29999", "Caribbean guilder"),  # Kingdom of the Netherlands: the Caribbean parts' currencies; the Netherlands uses the euro
}

# ---- r2 gates (DATA-REVIEW.md §4) ----
from collections import Counter
GATES = Counter()
DROPPED, NICK, VALDROP = [], [], []
# gate 3: things that do not exist (now): description of a lake/building/river/mountain (settlements keep "former capital")
NONEXIST = re.compile(r"former|paleo|prehistoric|proposed|planned|envisioned|unbuilt|under construction", re.I)
NONEXIST_KINDS = ("lake", "building", "river", "mountain", "dam")
# gate 3: value ranges (DATA-REVIEW §2 range table); a value outside it is dropped (the entity stays)
RANGE = {"area": (0, 20_000_000), "elev": (-500, 9_000), "len": (0, 7_000)}
RANGE_KIND = {("lake", "area"): 400_000, ("building", "height"): 900, ("dam", "height"): 350}
MANUAL_DROP = {("Q855309", "len")}  # Bian River 5,806 km (DATA-REVIEW §2 "length outlier (manual)"; real river is ~ 300 km)
# gate 4: alias removals
ALIAS_DROP = {("lake", "Michigan"), ("lake", "Superior"), ("lake", "Huron"), ("city", "Cape")}
DICT = {w.strip() for w in open("/usr/share/dict/words") if w.strip() and w.strip()[0].islower()}
ALIAS_STOP = {"the", "of", "and", "de", "del", "da", "do", "dos", "das", "du", "des", "la", "le", "les", "el", "in", "on", "at",
              "y", "e", "a", "an", "to", "for", "by", "von", "van", "der", "den", "di", "al"}
fold = lambda s: "".join(c for c in unicodedata.normalize("NFKD", s.lower()) if c.isalpha())
core = lambda s: re.sub(r"\s*\(.*?\)\s*", " ", s).strip().lower()
contig = lambda a, b: re.search(r"(?:^|\W)" + re.escape(a) + r"(?:$|\W)", b) is not None
def edit(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]
def nickname(alias, label):
    """A multi-word alias that is a generic English phrase unrelated to the label ("White House", "Garden City",
    "Green River", "Trump Tower"): not containing / contained in the label, not a spelling variant of it (edit distance
    <= 2 on folded letters), and every non-stopword token a lowercase dictionary word."""
    if " " not in alias.strip():
        return False
    a, l = alias.lower(), core(label)
    if contig(l, a) or contig(a, l) or edit(fold(alias), fold(label)) <= 2:
        return False
    toks = [t for t in re.findall(r"[^\W\d_]+", a) if t not in ALIAS_STOP]
    return bool(toks) and all(t in DICT for t in toks)

# r6 gate (b): new entities whose exact English label belongs to a more prominent other item (more sitelinks)
HOMONYM = {}
for f in sorted(raw.glob("homonym_r6_*.json")):
    for b in bindings(f):
        HOMONYM.setdefault(qid(b["item"]["value"]), qid(b["x"]["value"]))
COUNTRY_LABELS = {lab[i]["label"]["value"] for i, k in kind.items() if k == "country" and i in lab and "label" in lab[i]}

ents = []
for i, k in sorted(kind.items(), key=lambda x: (x[1], x[0])):
    b = lab.get(i)
    if not b or "label" not in b:
        continue
    name = b["label"]["value"]
    if i in HOMONYM:
        GATES[f"entity dropped: label of a more prominent item (r6) {k}"] += 1
        DROPPED.append(f"{name} ({k}): homonym of {HOMONYM[i]}")
        continue
    if k in NONEXIST_KINDS and NONEXIST.search(val(b, "desc") or ""):
        GATES[f"entity dropped: former/proposed/unbuilt {k}"] += 1
        DROPPED.append(f"{name} ({k}): {val(b, 'desc')}")
        continue
    aliases = [a for a in (val(b, "aliases") or "").split("|") if a and a != name and (len(a) >= 3 or a.isupper())]
    n0 = len(aliases)
    aliases = [a for a in aliases if (k, a) not in ALIAS_DROP]
    GATES["alias dropped: explicit (Michigan/Superior/Huron/Cape)"] += n0 - len(aliases)
    nick = [a for a in aliases if nickname(a, name)]
    GATES["alias dropped: nickname (generic multi-word phrase)"] += len(nick)
    NICK.extend(f"{name}: {a}" for a in nick)
    aliases = [a for a in aliases if a not in nick]
    e = {"q": i, "n": name}
    if aliases: e["a"] = sorted(set(aliases))
    e["k"] = k
    if val(b, "desc"): e["d"] = val(b, "desc")
    pop = number(i, "P1082", latest=True)
    if pop and k in ("country", "city"): e["pop"] = pop
    area = AREA_FIX.get(i) or number(i, "P2046", 1e-6)
    if area and k in ("country", "city", "lake"): e["area"] = area
    if k in ("mountain", "city", "lake"):
        el = number(i, "P2044")
        if el: e["elev"] = el
    if k in ("building", "dam", "other"):
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
            if key == "cur":
                v = [x for x in v if (i, x) not in CUR_ENDED]
                current = [r for r in itm.get((i, p), []) if "end" not in r]
                if len(v) > 3 and not any(r["rank"]["value"].endswith("PreferredRank") for r in current):
                    GATES["cur: > 3 currencies, none preferred, dropped (r7)"] += 1
                    v = []
            if v: e[key] = v
        for key, p in (("lang", "P37"), ("cont", "P30"), ("bord", "P47"), ("plug", "P2853")):
            v = labels(i, p)
            if v: e[key] = v
        if i in EMERG: e["emerg"] = [[n, ", ".join(sorted(u))] for n, u in sorted(EMERG[i].items(), key=lambda x: (len(x[0]), x[0]))]
        if "plug" in e: e["plug"] = sorted({PLUG.get(x, x) for x in e["plug"]})
        volts = sorted({round(float(r["amount"]["value"])) for r in qty.get((i, "P2884"), [])})
        if volts: e["volt"] = volts
        hz = sorted({round(float(r["amount"]["value"])) for r in qty.get((i, "P2885"), [])})
        if hz: e["hz"] = hz
    if k in ("building", "dam", "other", "event"):  # r2 gate 1: no founding year for countries or cities
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
    if k in ("mountain", "lake", "river", "building", "dam", "city", "other"):
        c = labels(i, "P17")
        cur = [x for x in c if x in COUNTRY_LABELS]  # r6 gate (a): current table countries only, when any
        if cur and cur != c:
            GATES["ctry: non-current states dropped (r6)"] += 1
            c = cur
        if c: e["ctry"] = c
    for f in ("area", "height", "elev", "len"):
        if f not in e:
            continue
        lo, hi = RANGE.get(f, (0, float("inf")))
        hi = min(hi, RANGE_KIND.get((k, f), hi))
        # r6 gate (c) (DATA-REVIEW-r6.md seed 47): a water tower above 200 m is a mis-entered height (elevation)
        if f == "height" and re.search(r"water tower$", name, re.I):
            hi = min(hi, 200)
        if not (lo < e[f] <= hi) or (i, f) in MANUAL_DROP:
            GATES[f"value dropped: {f} out of range / manual"] += 1
            VALDROP.append(f"{name} ({k}) {f}={e[f]}")
            del e[f]
    ents.append(e)

for k_, n_ in sorted(GATES.items()):
    print(f"gate\t{k_}\t{n_}", file=sys.stderr)
for x in DROPPED: print("dropped-entity\t" + x, file=sys.stderr)
for x in VALDROP: print("dropped-value\t" + x, file=sys.stderr)
for x in NICK: print("dropped-nickname\t" + x, file=sys.stderr)
doc = {"snapshot": SNAPSHOT, "build": "r8", "source": "Wikidata (CC0 1.0), WDQS snapshot " + SNAPSHOT + "; builder rnd/research/coordinator/arms/facts/tools/build_asset.py",
       "entities": ents}
out.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")))
print(len(ents), "entities", out.stat().st_size, "bytes", {k: sum(1 for e in ents if e["k"] == k) for k in sorted(set(kind.values()))})
