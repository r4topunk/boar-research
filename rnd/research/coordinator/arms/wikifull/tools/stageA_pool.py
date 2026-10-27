#!/usr/bin/env python3
"""Pool WIKIFULL A0 (shard 07) + stage A shards. Reads only aggregates (ids/titles/probabilities/counts).
Per set: items with any verified hit (p>=0.7 AND quote_supports) over covered shards; hits >=0.6/>=0.7 unverified;
by LOSSMAP group; by shard; outside-top-100k share; jev spend and time. Verdict (V-para, frozen criterion
ee81ad30): REOPEN >=14/34, MARGINAL 7-13, CLOSE <=6 -- only when all 15 shards are covered.
Stage B (2026-10-13): with --with-b, also pools aggregates/stageA-<set>-B.json (the delta pack of enwiki 20261001
pages outside FineWiki) and applies the bands to A+B only when all 15 shards + B are present.
usage: python3 -I tools/stageA_pool.py [--with-b]  -> markdown to stdout, aggregates/stageA-pooled.json (or stageAB-pooled.json)"""
import json, glob, os, re, sys
WITHB = "--with-b" in sys.argv
AG = "<workspace>/rnd/research/coordinator/arms/wikifull/aggregates"
TH = 0.7; GROUPS = ("on_topic", "off_topic_kept", "no_kept"); ALL = [f"{i:02d}" for i in range(15)]

def load(s):
    sh = {}
    p = f"{AG}/A0-shard07-{s}.json"
    if os.path.exists(p): sh["07"] = json.load(open(p))
    for p in sorted(glob.glob(f"{AG}/stageA-{s}-[0-9][0-9].json")):
        sh[re.search(r"-(\d\d)\.json$", p).group(1)] = json.load(open(p))
    if WITHB and os.path.exists(f"{AG}/stageA-{s}-B.json"): sh["B"] = json.load(open(f"{AG}/stageA-{s}-B.json"))
    return sh

def pool(s):
    sh = load(s); items = {}; per = {}
    for t, d in sorted(sh.items()):
        nv = 0
        for it in d["items"]:
            r = items.setdefault(it["id"], dict(id=it["id"], group=it["group"], max_p=0.0, ge06=False, ge07=False, verified=False,
                                                verified_outside_top100k=False, verified_shards=[], ge07_shards=[], verified_titles=[]))
            if it["max_p"] is not None: r["max_p"] = max(r["max_p"], it["max_p"])
            hs = it["hits"]
            if any(h["p"] >= 0.6 for h in hs): r["ge06"] = True
            if any(h["p"] >= TH for h in hs): r["ge07"] = True; r["ge07_shards"].append(t)
            v = [h for h in hs if h["p"] >= TH and h.get("verified")]
            if v:
                nv += 1; r["verified"] = True; r["verified_shards"].append(t)
                r["verified_titles"] += sorted({h["title"] for h in v} - set(r["verified_titles"]))
                if any(h["outside_top100k"] for h in v): r["verified_outside_top100k"] = True
        per[t] = dict(verified=nv, ge07=d["summary"]["ALL"]["ge07"], ge06=d["summary"]["ALL"]["ge06"],
                      cost=d.get("gateway_cost_usd", 0), runtime_s=d.get("runtime_s", 0), requests=d.get("requests_uncached", 0))
    L = list(items.values())
    def c(G):
        G = list(G); return dict(n=len(G), verified=sum(i["verified"] for i in G), ge07=sum(i["ge07"] for i in G), ge06=sum(i["ge06"] for i in G),
                                 verified_outside_top100k=sum(i["verified_outside_top100k"] for i in G))
    by = {"ALL": c(L)}; by.update({g: c(i for i in L if i["group"] == g) for g in GROUPS})
    return dict(shards=sorted(sh), missing=[t for t in ALL + (["B"] if WITHB else []) if t not in sh], per_shard=per, by_group=by,
                cost=round(sum(p["cost"] for p in per.values()), 4), runtime_s=sum(p["runtime_s"] for p in per.values()),
                items=sorted(L, key=lambda i: i["id"]))

def verdict(r):
    if r["missing"]: return f"partial: {len(r['shards'])}/{15 + WITHB} shards (missing {' '.join(r['missing'])}); no verdict"
    v = r["by_group"]["ALL"]["verified"]
    return f"{'REOPEN' if v >= 14 else 'MARGINAL' if v >= 7 else 'CLOSE'} ({v}/{r['by_group']['ALL']['n']} verified)"

out = {}
for s in ("vpara", "v02"):
    r = pool(s); r["verdict"] = verdict(r) if s == "vpara" else "dev context only (never decided on): " + verdict(r).split(";")[0]; out[s] = r
json.dump(out, open(f"{AG}/{'stageAB' if WITHB else 'stageA'}-pooled.json", "w"), indent=1)
for s, r in out.items():
    print(f"\n### {s}: shards {len(r['shards'])}/{15 + WITHB}{' (15 + B)' if WITHB else ''}, jev ${r['cost']:.3f}, gate time {r['runtime_s']} s -- {r['verdict']}\n")
    print("| group | n | verified p>=0.7 | hit >=0.7 (unverified) | hit >=0.6 | verified outside top-100k |\n|---|---|---|---|---|---|")
    for g in ("ALL",) + GROUPS:
        b = r["by_group"][g]; print(f"| {g} | {b['n']} | {b['verified']} | {b['ge07']} | {b['ge06']} | {b['verified_outside_top100k']} |")
    print("\n| shard | verified items | items >=0.7 | items >=0.6 | jev $ | s |\n|---|---|---|---|---|---|")
    for t, p in sorted(r["per_shard"].items()):
        print(f"| {t} | {p['verified']} | {p['ge07']} | {p['ge06']} | {p['cost']:.3f} | {p['runtime_s']} |")
