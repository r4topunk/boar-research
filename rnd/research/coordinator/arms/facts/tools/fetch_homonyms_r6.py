#!/usr/bin/env python3
"""r6 data-review gate input (DATA-REVIEW-r6.md, class "label shared with a more prominent other sense"): for every entity
of a candidate asset that is not in the r5 asset, the other Wikidata items with the exact same English label that have MORE
sitelinks (not disambiguation pages), via fetch_wikidata.q() (generic UA, 1 req/min). Saved as homonym_r6_<n>.{rq,json}.
Usage: python3 -I fetch_homonyms_r6.py <raw_dir> <r5_asset.json> <candidate_asset.json>"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch_wikidata as fw  # noqa: E402  (reads OUT from sys.argv[1])

old = {e["q"] for e in json.load(open(sys.argv[2]))["entities"]}
new = sorted(e["q"] for e in json.load(open(sys.argv[3]))["entities"] if e["q"] not in old)
B = 700
for bi in range(0, len(new), B):
    vals = " ".join("wd:" + i for i in new[bi:bi + B])
    rows = fw.q(f"homonym_r6_{bi // B}", """SELECT ?item ?s1 ?x ?s2 WHERE { VALUES ?item { %s }
  ?item rdfs:label ?l ; wikibase:sitelinks ?s1 . FILTER(LANG(?l) = "en")
  ?x rdfs:label ?l ; wikibase:sitelinks ?s2 . FILTER(?x != ?item && ?s2 > ?s1)
  FILTER NOT EXISTS { ?x wdt:P31 wd:Q4167410 } FILTER NOT EXISTS { ?x wdt:P31 wd:Q13406463 } }""" % vals)
    print(bi // B, len(rows), flush=True)
