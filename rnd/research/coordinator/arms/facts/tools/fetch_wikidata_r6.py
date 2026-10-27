#!/usr/bin/env python3
"""r6 (FACTS-r6-criterion.md A): coverage expansion. Reuses fetch_wikidata.q() (same generic User-Agent, same 1 req/min
pacing, cache: an existing <name>.json is never refetched). New selections are saved as sel_*_r6.{rq,json}; property rows
for entities not already in the r1 cache are saved as {lab,qty,pop,itm,tim}_r6_<n>.{rq,json} with the exact r1 queries.
Usage: python3 -I fetch_wikidata_r6.py <out_dir>   (out_dir = arms/facts/data/raw)"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch_wikidata as fw  # noqa: E402  (reads OUT from sys.argv[1])

NOEND = "FILTER NOT EXISTS { ?item wdt:P576 ?end }"
SEL = {
 # cities: the r1 class list, population >= 300k (all; no LIMIT cut beyond a safety cap)
 "sel_cities_r6": """SELECT ?item (MAX(?pop) AS ?p) WHERE {
  ?item wdt:P1082 ?pop . FILTER(?pop >= 300000)
  ?item wdt:P31/wdt:P279? ?t . VALUES ?t { wd:Q515 wd:Q1549591 wd:Q1637706 wd:Q5119 wd:Q200250 wd:Q22865 wd:Q1093829 wd:Q748149 wd:Q15284 wd:Q1066984 }
  %s
} GROUP BY ?item ORDER BY DESC(?p) LIMIT 20000""" % NOEND,
 # mountains: elevation (the 500 highest are kept at build time; > 6,000 m pre-filter keeps the GROUP BY small)
 "sel_mountains_elev_r6": """SELECT ?item (MAX(?a) AS ?v) WHERE { ?item p:P2044/psn:P2044/wikibase:quantityAmount ?a . FILTER(?a > 6000)
  ?item wdt:P31/wdt:P279? wd:Q8502 . }
 GROUP BY ?item ORDER BY DESC(?v) LIMIT 1500""",
 # mountains: all with prominence >= 1,500 m
 "sel_mountains_prom_r6": """SELECT ?item (MAX(?a) AS ?v) WHERE { ?item p:P2660/psn:P2660/wikibase:quantityAmount ?a . FILTER(?a >= 1500)
  ?item wdt:P31/wdt:P279? wd:Q8502 . }
 GROUP BY ?item ORDER BY DESC(?v) LIMIT 5000""",
 "sel_rivers_r6": """SELECT ?item (MAX(?a) AS ?v) WHERE { ?item wdt:P31 wd:Q4022 ; p:P2043/psn:P2043/wikibase:quantityAmount ?a . }
 GROUP BY ?item ORDER BY DESC(?v) LIMIT 400""",
 "sel_lakes_r6": """SELECT ?item (MAX(?a) AS ?v) WHERE { ?item wdt:P31/wdt:P279* wd:Q23397 ; p:P2046/psn:P2046/wikibase:quantityAmount ?a . }
 GROUP BY ?item ORDER BY DESC(?v) LIMIT 300""",
 "sel_buildings_r6": """SELECT ?item (MAX(?a) AS ?v) WHERE { ?item wdt:P31 wd:Q11303 ; p:P2048/psn:P2048/wikibase:quantityAmount ?a .
  %s }
 GROUP BY ?item ORDER BY DESC(?v) LIMIT 450""" % NOEND,
 "sel_towers_r6": """SELECT ?item (MAX(?a) AS ?v) WHERE { ?item p:P2048/psn:P2048/wikibase:quantityAmount ?a . FILTER(?a > 150)
  ?item wdt:P31/wdt:P279* wd:Q12518 . %s }
 GROUP BY ?item ORDER BY DESC(?v) LIMIT 450""" % NOEND,
 "sel_dams_r6": """SELECT ?item (MAX(?a) AS ?v) WHERE { ?item p:P2048/psn:P2048/wikibase:quantityAmount ?a . FILTER(?a > 100)
  ?item wdt:P31/wdt:P279* wd:Q12323 . %s }
 GROUP BY ?item ORDER BY DESC(?v) LIMIT 200""" % NOEND,
}
B = 800

def main():
    have = set()
    for f in fw.OUT.glob("lab_*.json"):
        if "_r6_" not in f.name:
            have.update(fw.ids(json.loads(f.read_text())["results"]["bindings"]))
    sel = {k: fw.q(k, v) for k, v in SEL.items()}
    for k, v in sel.items():
        print(k, len(v), flush=True)
    new = sorted({i for v in sel.values() for i in fw.ids(v)} - have)
    print("new entities", len(new), flush=True)
    for bi in range(0, len(new), B):
        n = bi // B
        vals = " ".join("wd:" + i for i in new[bi:bi + B])
        r1 = {p: (fw.OUT / f"{p}_0.rq").read_text() for p in ("lab", "qty", "pop", "itm", "tim")}
        for p, text in r1.items():
            # the exact r1 query text with this batch's VALUES list
            head, rest = text.split("VALUES ?item {", 1)
            tail = rest.split("}", 1)[1]
            fw.q(f"{p}_r6_{n}", head + "VALUES ?item { " + vals + " }" + tail)
            print(p, n, flush=True)

if __name__ == "__main__":
    main()
