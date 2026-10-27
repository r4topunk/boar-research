#!/usr/bin/env python3
"""Run o2_reference.decide over Kiln's rnd/kiln/exp-03-o2/inputs.jsonl (or any file with query, answer, label,
citedTitles, promptTitles, declined) and print the confusion vs the hand label. Passage text comes from the local
pack copies (article level; the app has the passage itself)."""
import sys, json, collections, argparse
sys.path.insert(0, __import__("os").path.dirname(__file__))
import o2_reference as o, refusal_audit as ra
ap = argparse.ArgumentParser(); ap.add_argument("inputs"); ap.add_argument("--variant", choices=["A", "B"], default="A",
    help="A: uncited answers use all prompt passages; B: only prompt passage [1]"); ap.add_argument("--json"); ap.add_argument("--quiet", action="store_true")
a = ap.parse_args()
ra.configure(["boar-crypto", "boar-wikivoyage-en", "wiki-vital5"]); P = ra.Packs()
def text(t):
    """Source-aware lookup: 'Wikivoyage: X' -> wikivoyage pack; 'Ethereum…: X' -> crypto; bare titles are Wikipedia
    (crypto enwiki subset, then wiki-vital5), never Wikivoyage."""
    bare = ra.strip_prefix(t)
    order = ["boar-wikivoyage-en"] if t.startswith("Wikivoyage: ") else ["boar-crypto"] if bare != t else ["boar-crypto", "wiki-vital5"]
    for pk in order:
        x = P._v1_text(pk, bare) if pk in ra.V1_PACKS else P._v2_text(pk, bare)
        if x: return x
    return None
def L(x):
    if isinstance(x, list): return x
    try: return json.loads(x)
    except Exception: return []
out = []
for r in map(json.loads, open(a.inputs)):
    if str(r.get("declined")) == "True":
        continue
    cited, prompt = L(r.get("citedTitles")), L(r.get("promptTitles"))
    used = cited or (prompt if a.variant == "A" else prompt[:1])
    d = o.decide(r["query"], [{"title": t, "text": text(t)} for t in dict.fromkeys(used)])
    out.append({**{k: r.get(k) for k in ("src", "model", "queryId", "label")}, "in_scope": d["in_scope"], "action": d["action"],
                "reason": d["reason"], "used": used, "cited": bool(cited)})
sc = [x for x in out if x["in_scope"]]
C = collections.Counter((x["label"], x["action"]) for x in sc)
print(f"variant {a.variant}: answered rows {len(out)}, in scope {len(sc)}  |  " + "  ".join(f"{k[0]}->{k[1]}:{v}" for k, v in sorted(C.items())))
if not a.quiet:
    for x in sorted(sc, key=lambda x: (x["label"], x["action"], x["queryId"])):
        print(f"  {x['src']:3} {x['model'][:14]:14} {x['queryId']:11} {x['label']:7} {x['action']:6} {x['reason'][:75]}")
if a.json: json.dump(out, open(a.json, "w"), indent=1)
