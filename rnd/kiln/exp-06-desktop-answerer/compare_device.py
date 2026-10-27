#!/usr/bin/env python3
"""exp-06 DoD check: does the desktop answerer reproduce the iPhone's route and sources?

Compares the desktop rows (answerer.ts, same app commit 14de107, same packs, same settings, iPhone 13 simulated) with
Plumb's run 2 on the physical iPhone 13 (rnd/plumb/data/qwen2.5-1.5b-instruct-q4km__iphone-14de107-device.jsonl,
build rc6eval-r11-0459 = build/model-ab-rc6-eval @14de107, packs boar-crypto + boar-wikivoyage-en).
Sample: 10 ids drawn with seed 20261001 among the ids both runs answered, excluding "near me" items (GPS context).
Per id: tier, declined, route codes, shown sources (title Jaccard), cited titles.
Usage: python3 compare_device.py desktop.jsonl device.jsonl [--all] [out.md]
"""
import json, random, re, sys

desk_p, dev_p = sys.argv[1], sys.argv[2]
ALL = "--all" in sys.argv
out = next((a for a in sys.argv[3:] if a.endswith(".md")), None)
D = {r["id"]: r for r in map(json.loads, open(desk_p))}
P = {r["queryId"]: r for r in map(json.loads, open(dev_p))}
common = sorted(i for i in D if i in P and not (D[i].get("question", "").lower().find("near me") >= 0))
ids = common if ALL else sorted(random.Random(20261001).sample(common, 10))
KEY = re.compile(r"^(task:|instant:|places:|grounding:|generate:|retrieve:|offer-deep|health|calc|emergency)")


def codes(rc):
    return sorted({c.split("-")[0] if c.startswith("grounding:off-topic-dropped") else c for c in rc if KEY.match(c)} - {"generate:user-model-qwen2.5-1.5b-instruct-q4km"})


def norm(t):
    return re.sub(r"\s+", " ", (t or "").strip().lower())


def jacc(a, b):
    a, b = set(map(norm, a)), set(map(norm, b))
    return 1.0 if not a and not b else len(a & b) / len(a | b)


rows, agg = [], {"tier": 0, "declined": 0, "route": 0, "sources_jacc": [], "cited": 0}
for i in ids:
    d, p = D[i], P[i]
    d_src = [s["title"] for s in (d.get("shownSources") or d["sources"])]
    p_src = p.get("retrievedTitles") or []
    d_cit, p_cit = d.get("citedTitles") or [], p.get("citedTitles") or []
    d_codes, p_codes = codes(d["reasonCodes"]), codes(p.get("reasonCodes") or [])
    t = d["tier"] == p.get("tier")
    dec = bool(d["flags"]["declined"]) == bool(p.get("declined"))
    rt = d_codes == p_codes
    j = jacc(d_src, p_src)
    c = set(map(norm, d_cit)) == set(map(norm, p_cit))
    agg["tier"] += t; agg["declined"] += dec; agg["route"] += rt; agg["sources_jacc"].append(j); agg["cited"] += c
    rows.append({"id": i, "tier": (d["tier"], p.get("tier")), "declined": (d["flags"]["declined"], bool(p.get("declined"))),
                 "route_same": rt, "route_diff": (sorted(set(d_codes) - set(p_codes)), sorted(set(p_codes) - set(d_codes))),
                 "src_jaccard": round(j, 2), "src_desk": d_src, "src_dev": p_src, "cited_same": c, "cited_desk": d_cit, "cited_dev": p_cit,
                 "answer_desk": d["answer"][:160], "answer_dev": (p.get("answer") or "")[:160]})
n = len(ids)
L = [f"# exp-06 desktop vs iPhone 13 (run 2, build 14de107), {'all' if ALL else 'sample of'} {n} ids", "",
     f"- tier same: {agg['tier']}/{n}", f"- declined same: {agg['declined']}/{n}", f"- route codes same: {agg['route']}/{n}",
     f"- shown sources, mean title Jaccard: {sum(agg['sources_jacc']) / n:.2f}; identical sets: {sum(j == 1 for j in agg['sources_jacc'])}/{n}",
     f"- cited titles same: {agg['cited']}/{n}", "", "| id | tier desk/dev | declined desk/dev | route same | route only-desk / only-dev | src J | cited same |", "|---|---|---|---|---|---:|---|"]
for r in rows:
    L.append(f"| {r['id']} | {r['tier'][0]}/{r['tier'][1]} | {r['declined'][0]}/{r['declined'][1]} | {'✓' if r['route_same'] else '✗'} | "
             f"{', '.join(r['route_diff'][0]) or '—'} / {', '.join(r['route_diff'][1]) or '—'} | {r['src_jaccard']} | {'✓' if r['cited_same'] else '✗'} |")
L += ["", "## Per-id detail", ""]
for r in rows:
    L += [f"### {r['id']}", f"- sources desk: {r['src_desk']}", f"- sources dev:  {r['src_dev']}",
          f"- cited desk: {r['cited_desk']} / dev: {r['cited_dev']}", f"- answer desk: {r['answer_desk']!r}", f"- answer dev:  {r['answer_dev']!r}", ""]
text = "\n".join(L) + "\n"
print(text)
if out:
    open(out, "w").write(text)
