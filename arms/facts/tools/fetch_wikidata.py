#!/usr/bin/env python3
"""Fetch the FACTS entity set from the Wikidata Query Service (CC0) once and cache raw JSON + the query text.
Usage: python3 -I fetch_wikidata.py <out_dir>   (out_dir = arms/facts/data/raw). Generic User-Agent, no personal data."""
import json, sys, time, urllib.parse, urllib.request
from pathlib import Path

UA = "facts-pack-builder/0.1 (offline research; generic)"
EP = "https://query.wikidata.org/sparql"
OUT = Path(sys.argv[1])

def q(name, sparql):
    f = OUT / f"{name}.json"
    if f.exists():
        return json.loads(f.read_text())["results"]["bindings"]
    (OUT / f"{name}.rq").write_text(sparql)
    req = urllib.request.Request(EP, data=urllib.parse.urlencode({"query": sparql, "format": "json"}).encode(),
                                 headers={"User-Agent": UA, "Accept": "application/sparql-results+json",
                                          "Content-Type": "application/x-www-form-urlencoded"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            f.write_bytes(data)
            time.sleep(62)  # WDQS rate limit during the outage rule: 1 req/min
            return json.loads(data)["results"]["bindings"]
        except Exception as e:
            print(name, "attempt", attempt, e, file=sys.stderr)
            time.sleep(65)
    raise SystemExit(f"failed {name}")

def ids(rows, var="item"):
    return [r[var]["value"].rsplit("/", 1)[1] for r in rows]

# ---- phase A: entity selection ----
SEL = {
 "sel_countries": """SELECT ?item WHERE { ?item wdt:P31 wd:Q3624078 . FILTER NOT EXISTS { ?item wdt:P576 ?end } }""",
 "sel_cities": """SELECT ?item (MAX(?pop) AS ?p) WHERE {
  ?item wdt:P1082 ?pop . FILTER(?pop > 1000000)
  ?item wdt:P31/wdt:P279? ?t . VALUES ?t { wd:Q515 wd:Q1549591 wd:Q1637706 wd:Q5119 wd:Q200250 wd:Q22865 wd:Q1093829 wd:Q748149 wd:Q15284 wd:Q1066984 }
  FILTER NOT EXISTS { ?item wdt:P576 ?end }
} GROUP BY ?item ORDER BY DESC(?p) LIMIT 400""",
 "sel_lakes": """SELECT ?item (MAX(?a) AS ?v) WHERE { ?item wdt:P31/wdt:P279* wd:Q23397 ; p:P2046/psn:P2046/wikibase:quantityAmount ?a . }
 GROUP BY ?item ORDER BY DESC(?v) LIMIT 140""",
 "sel_rivers": """SELECT ?item (MAX(?a) AS ?v) WHERE { ?item wdt:P31 wd:Q4022 ; p:P2043/psn:P2043/wikibase:quantityAmount ?a . }
 GROUP BY ?item ORDER BY DESC(?v) LIMIT 140""",
 "sel_mountains": """SELECT ?item (MAX(?a) AS ?v) WHERE { ?item wdt:P31/wdt:P279? wd:Q8502 ; p:P2660/psn:P2660/wikibase:quantityAmount ?a . }
 GROUP BY ?item ORDER BY DESC(?v) LIMIT 140""",
 "sel_buildings": """SELECT ?item (MAX(?a) AS ?v) WHERE { ?item wdt:P31 wd:Q11303 ; p:P2048/psn:P2048/wikibase:quantityAmount ?a .
  FILTER NOT EXISTS { ?item wdt:P576 ?end } }
 GROUP BY ?item ORDER BY DESC(?v) LIMIT 140""",
}
NAMED = ["Q155", "Q159", "Q189", "Q12495", "Q5513", "Q7296", "Q5086", "Q8613", "Q37922"]  # step-1 entities

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sel = {k: q(k, v) for k, v in SEL.items()}
    for k, v in sel.items():
        print(k, len(v))
    allq = set(NAMED)
    for k, v in sel.items():
        allq.update(ids(v))
    # capitals of the countries
    cap = q("sel_capitals", "SELECT ?item WHERE { VALUES ?c { %s } ?c wdt:P36 ?item . }" % " ".join("wd:" + i for i in ids(sel["sel_countries"])))
    allq.update(ids(cap))
    allq = sorted(allq)
    print("entities", len(allq))
    batches = [allq[i:i + 600] for i in range(0, len(allq), 600)]
    for bi, b in enumerate(batches):
        vals = " ".join("wd:" + i for i in b)
        q(f"lab_{bi}", """SELECT ?item ?label ?desc (GROUP_CONCAT(DISTINCT ?alias; separator="|") AS ?aliases) WHERE { VALUES ?item { %s }
  OPTIONAL { ?item rdfs:label ?label FILTER(LANG(?label)="en") } OPTIONAL { ?item schema:description ?desc FILTER(LANG(?desc)="en") }
  OPTIONAL { ?item skos:altLabel ?alias FILTER(LANG(?alias)="en") } } GROUP BY ?item ?label ?desc""" % vals)
        q(f"qty_{bi}", """SELECT ?item ?prop ?amount ?unit ?rank ?time WHERE { VALUES ?item { %s }
  VALUES ?prop { wd:P1082 wd:P2046 wd:P2044 wd:P2048 wd:P2043 wd:P4511 wd:P2660 wd:P2884 wd:P2885 wd:P1101 }
  ?prop wikibase:claim ?c ; wikibase:statementValueNormalized ?psn .
  ?item ?c ?st . ?st ?psn ?n . ?n wikibase:quantityAmount ?amount ; wikibase:quantityUnit ?unit . ?st wikibase:rank ?rank .
  FILTER(?rank != wikibase:DeprecatedRank)
  OPTIONAL { ?st pq:P585 ?time } }""" % vals)
        # population is unitless: no normalized value node, so read the plain statement value (+ P585 point in time)
        q(f"pop_{bi}", """SELECT ?item ?amount ?rank ?time WHERE { VALUES ?item { %s }
  ?item p:P1082 ?st . ?st ps:P1082 ?amount ; wikibase:rank ?rank . FILTER(?rank != wikibase:DeprecatedRank)
  OPTIONAL { ?st pq:P585 ?time } }""" % vals)
        q(f"itm_{bi}", """SELECT ?item ?prop ?val ?valLabel ?rank ?end WHERE { VALUES ?item { %s }
  VALUES ?prop { wd:P36 wd:P38 wd:P37 wd:P30 wd:P47 wd:P2853 wd:P17 wd:P31 wd:P276 wd:P403 wd:P131 }
  ?prop wikibase:claim ?c ; wikibase:statementProperty ?ps .
  ?item ?c ?st . ?st ?ps ?val ; wikibase:rank ?rank . FILTER(?rank != wikibase:DeprecatedRank) FILTER(isIRI(?val))
  OPTIONAL { ?st pq:P582 ?end }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }""" % vals)
        q(f"tim_{bi}", """SELECT ?item ?prop ?t ?prec ?rank WHERE { VALUES ?item { %s }
  VALUES ?prop { wd:P571 wd:P576 wd:P580 wd:P582 wd:P1619 wd:P729 wd:P3999 }
  ?prop wikibase:claim ?c ; wikibase:statementValue ?psv .
  ?item ?c ?st . ?st ?psv ?tv . ?tv wikibase:timeValue ?t ; wikibase:timePrecision ?prec . ?st wikibase:rank ?rank .
  FILTER(?rank != wikibase:DeprecatedRank) }""" % vals)
    # winners of the named award, by year (P1346 on the award with P585, and P166 on people with P585)
    q("award_winners", """SELECT ?award ?w ?wLabel ?time ?src WHERE { VALUES ?award { wd:Q37922 }
  { ?award p:P1346 ?st . ?st ps:P1346 ?w ; pq:P585 ?time . BIND("P1346" AS ?src) }
  UNION { ?w p:P166 ?st . ?st ps:P166 ?award ; pq:P585 ?time . BIND("P166" AS ?src) }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }""")

if __name__ == "__main__":
    main()
