#!/usr/bin/env python3
"""facts-r11 (2026-10-23, ENGFIX-FACTS-DATA / NOBEL1988): currency and Nobel data with the qualifiers the r6 fetch dropped.
Usage: python3 -I fetch_currency_r11.py <facts.v1.r10.json> <raw_dir>. Generic User-Agent, no personal data, sequential, cached.
  cur_r11      every non-deprecated P38 statement of the 197 countries with qualifiers P580 start, P582 end, P518 applies to part,
               P3005 valid in place, P1480 sourcing circumstances (the r6 itm_* query kept only P582)
  curitem_r11  per currency item: P31 types, P576 abolished date, P1366 replaced by, P571 inception, P2... (label)
  nobel_r11    P1346 (award side) and P166 (person side) for the Nobel Prize in Literature with point in time P585, statement ids kept"""
import json, sys, time, urllib.parse, urllib.request
from pathlib import Path

UA = "facts-pack-builder/0.1 (offline research; generic)"
EP = "https://query.wikidata.org/sparql"
table, OUT = Path(sys.argv[1]), Path(sys.argv[2])
C = sorted(e["q"] for e in json.loads(table.read_text())["entities"] if e["k"] == "country")
VALUES = "VALUES ?c { " + " ".join(f"wd:{c}" for c in C) + " }"

def q(name, sparql):
    f = OUT / f"{name}.json"
    if f.exists():
        return
    (OUT / f"{name}.rq").write_text(sparql)
    req = urllib.request.Request(EP, data=urllib.parse.urlencode({"query": sparql, "format": "json"}).encode(),
                                 headers={"User-Agent": UA, "Accept": "application/sparql-results+json",
                                          "Content-Type": "application/x-www-form-urlencoded"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            f.write_bytes(data)
            print(name, len(json.loads(data)["results"]["bindings"]), "rows", file=sys.stderr)
            time.sleep(20)
            return
        except Exception as e:
            print(name, "attempt", attempt, e, file=sys.stderr)
            time.sleep(65)
    raise SystemExit(f"failed {name}")

CUR = """SELECT ?c ?st ?rank ?v ?vLabel ?pq ?qv ?qvLabel WHERE { %s
  ?c p:P38 ?st . ?st ps:P38 ?v ; wikibase:rank ?rank . FILTER(?rank != wikibase:DeprecatedRank)
  OPTIONAL { ?st ?pq ?qv . FILTER(?pq IN (pq:P580, pq:P582, pq:P518, pq:P3005, pq:P1480)) }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }""" % VALUES
CURITEM = """SELECT DISTINCT ?v ?vLabel ?typeLabel ?abol ?repl ?replLabel ?inc WHERE { %s
  ?c p:P38 ?st . ?st ps:P38 ?v . FILTER NOT EXISTS { ?st wikibase:rank wikibase:DeprecatedRank }
  OPTIONAL { ?v wdt:P31 ?type }
  OPTIONAL { ?v wdt:P576 ?abol }
  OPTIONAL { ?v wdt:P1366 ?repl }
  OPTIONAL { ?v wdt:P571 ?inc }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }""" % VALUES
NOBEL = """SELECT ?w ?wLabel ?time ?src ?st WHERE {
  { wd:Q37922 p:P1346 ?st . ?st ps:P1346 ?w ; pq:P585 ?time . BIND("P1346" AS ?src) }
  UNION { ?w p:P166 ?st . ?st ps:P166 wd:Q37922 ; pq:P585 ?time . BIND("P166" AS ?src) }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }"""

OUT.mkdir(parents=True, exist_ok=True)
q("cur_r11", CUR); q("curitem_r11", CURITEM); q("nobel_r11", NOBEL)

# ---- bare-QID labels (root cause of the missing euro, r6): Wikidata moved the labels of many items (the euro Q4916, Kipling
# Q34743 ...) from "en" to the language-neutral "mul" code; WDQS's label service (language "en") then returns the bare QID,
# and the builder's "unlabelled item" guard dropped the statement (the euro vanished on 30 countries). wbgetentities with
# languagefallback=1 resolves en -> mul. Every bare QID found in the r11 results goes into data/labels-r11.json; the builder
# fails if one stays unresolved on a kept statement.
import re
def bare():
    out = set()
    for n in ("cur_r11", "curitem_r11", "nobel_r11"):
        for b in json.loads((OUT / f"{n}.json").read_text())["results"]["bindings"]:
            for k, v in b.items():
                if k.endswith("Label") and re.fullmatch(r"Q\d+", v.get("value", "")):
                    out.add(v["value"])
    return sorted(out)

lf = OUT.parent / "labels-r11.json"
ids = bare()
labels = {}
for i in range(0, len(ids), 50):
    url = "https://www.wikidata.org/w/api.php?action=wbgetentities&props=labels&languages=en&languagefallback=1&format=json&ids=" + "|".join(ids[i:i + 50])
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
        for k, e in json.loads(r.read())["entities"].items():
            if "labels" in e and "en" in e["labels"]:
                labels[k] = e["labels"]["en"]["value"]
lf.write_text(json.dumps({"fetched": time.strftime("%Y-%m-%d"), "source": "wikidata wbgetentities labels en (r11: bare QIDs in cur_r11/curitem_r11/nobel_r11)",
                          "labels": dict(sorted(labels.items()))}, ensure_ascii=False, indent=0))
print("labels-r11:", len(labels), "of", len(ids), "bare QIDs", file=sys.stderr)
