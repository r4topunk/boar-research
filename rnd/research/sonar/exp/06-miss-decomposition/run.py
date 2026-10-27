"""Sonar exp-06: for items whose answer key is NOT in the retrieved candidates (raw) on ios-main-v5-t0 (kit A + vital5),
is the key present anywhere in an installed source of the reference article (coverage OK -> retrieval miss) or not
(coverage gap)? Installed: bundled corpus, wiki-vital5 (intros), boar-wikivoyage-en, boar-crypto. Reference titles =
en.wikipedia.org URLs in the item's reference_sources (+ the same title in Wikivoyage/crypto). Read-only."""
import json, sys, urllib.parse, sqlite3
sys.argv = ["x"]
exec(open("<workspace>/rnd/research/sonar/tools/key_in_context.py").read().split('if __name__ == "__main__":')[0])
R = "<workspace>/boar-eval/runs/night-2026-10-01/"
qs = {json.loads(l)["id"]: json.loads(l) for l in open("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl")}
res = Resolver(True)
per, _ = score(qs, R + "ios-main-v5-t0.traces.jsonl", res)
miss = [i for i, v in per.items() if not v["raw"]]
rows = []
for i in miss:
    q = qs[i]
    titles = [urllib.parse.unquote(u.split("/wiki/")[1]).replace("_", " ") for u in q["reference_sources"] if "wikipedia.org/wiki/" in u or "wikivoyage.org/wiki/" in u]
    found = []
    for t in titles:
        tx = res.text({"title": t, "source": None})
        if tx is not None: found.append((t, key_hit(tx, q["grading"])))
    status = "retrieval-miss" if any(h for _, h in found) else ("in-pack-no-key" if found else "not-in-pack")
    rows.append({"id": i, "cat": q["category"], "q": q["question"][:80], "ref_titles": titles, "found": found, "status": status,
                 "raw": [s["title"] for s in json.loads(next(l for l in open(R + "ios-main-v5-t0.traces.jsonl") if json.loads(l)["itemId"] == i))["retrieval"]["raw"]]})
json.dump(rows, open("miss.json", "w"), indent=1)
import collections
print(f"keyed items {len(per)}; key in raw {sum(v['raw'] for v in per.values())}; misses {len(miss)}:", dict(collections.Counter(r["status"] for r in rows)))
for r in sorted(rows, key=lambda r: r["status"]):
    print(f"\n[{r['status']}] {r['id']} ({r['cat']}) {r['q']}\n   refs: {r['ref_titles']}\n   in-pack (title, key?): {r['found']}\n   raw: {r['raw']}")
