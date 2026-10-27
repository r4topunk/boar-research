#!/usr/bin/env python3
"""facts-r9 (2026-10-19): travel-practical country fields from the Wikidata Query Service (CC0), for the 197 countries of
the r8 table. Usage: python3 -I fetch_wikidata_r9.py <facts.v1.r8.json> <raw_dir>. Generic User-Agent, no personal data.
Writes raw/<name>_r9.rq (query text) + raw/<name>_r9.json (response, unmodified); cached files are not refetched.
Verified property ids (wbgetentities 2026-10-19): P1622 driving side, P474 telephone country code, P2884 mains voltage
(mains frequency is its qualifier P2144 'frequency'; P2885 does not exist), P2853 electrical plug type, P421 time zone,
P37 official language. Qualifiers kept: P582 end time, P580 start time, P518 applies to part."""
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

# one row per (statement, qualifier); statement value + rank always present
ITEM = """SELECT ?c ?st ?rank ?v ?vLabel ?pq ?qv ?qvLabel WHERE { %s
  ?c p:%s ?st . ?st ps:%s ?v ; wikibase:rank ?rank . FILTER(?rank != wikibase:DeprecatedRank)
  OPTIONAL { ?st ?pq ?qv . FILTER(?pq IN (pq:P582, pq:P580, pq:P518)) }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }"""
VOLT = """SELECT ?c ?st ?rank ?v ?unit ?pq ?qv ?qvLabel WHERE { %s
  ?c p:P2884 ?st . ?st psv:P2884 ?vn ; wikibase:rank ?rank . ?vn wikibase:quantityAmount ?v ; wikibase:quantityUnit ?unit .
  FILTER(?rank != wikibase:DeprecatedRank)
  OPTIONAL { ?st ?pq ?qv . FILTER(?pq IN (pq:P582, pq:P580, pq:P518, pq:P2144)) }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }"""

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    print(len(C), "countries", file=sys.stderr)
    q("drive_r9", ITEM % (VALUES, "P1622", "P1622"))
    q("call_r9", ITEM % (VALUES, "P474", "P474"))
    q("volt_r9", VOLT % VALUES)
    q("plug_r9", ITEM % (VALUES, "P2853", "P2853"))
    q("tz_r9", ITEM % (VALUES, "P421", "P421"))

main()
