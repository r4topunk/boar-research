"""L0 gold-hit (Sonar exp-34): does the engine's Context (the 4B's fast-tier prompt, from a --dump-prompts run) contain
Anvil's oracle gold? Metrics per v0.1 EN item (57):
  art  = a gold Wikipedia article title (anvil/exp/oracle/articles.jsonl, kind=wiki) is a Context source labelled Wikipedia*;
  pas  = best coverage of an oracle R450 passage (top-3 by sim to the Opus answer) by the Context: share of the passage's
         word 4-grams found in the Context; hit at >= 0.5.
Usage: python3 goldhit.py <prompts.jsonl> [label]   (dev only; no blind data)"""
import json, re, sys, collections
O = "<workspace>/rnd/research/anvil/exp/oracle/"
ids = open("<workspace>/rnd/research/anvil/exp/outofkit/v01-en-ids.txt").read().strip().split(",")
gold = collections.defaultdict(set)
for l in open(O + "articles.jsonl"):
    a = json.loads(l)
    if a["kind"] == "wiki": gold[a["id"]].add(a["title"].lower())
R = {json.loads(l)["id"]: json.loads(l)["passages"] for l in open(O + "ctx-R450.jsonl")}
W = lambda s: re.findall(r"\w+", s.lower())
def grams(ws, n=4): return {tuple(ws[i:i + n]) for i in range(len(ws) - n + 1)}
def norm_t(t): return re.sub(r"\s*\(.*?\)\s*$", "", t).strip().lower()
dump = {}
for l in open(sys.argv[1]):
    r = json.loads(l)
    if "messages" in r:  # --dump-prompts file: the Context block of the system prompt
        s = r["messages"][0]["content"]
        dump[r["itemId"]] = s.split("\n\nContext:\n", 1)[1] if "\n\nContext:\n" in s else ""
    else:  # --event-source-text traces: the last "sources" event with passage text = what was placed in the prompt
        ev = [e for e in (r.get("events") or []) if e.get("type") == "sources" and any(x.get("text") for x in e.get("sources", []))]
        src = ev[-1]["sources"] if ev else []
        dump[r["itemId"]] = "\n\n".join(f"[{k + 1}] {(x.get('source') or 'Wikipedia-vital5').split(' ')[0]}: {x.get('title')}\n{x.get('text') or ''}" for k, x in enumerate(src))
rows = []
for i in ids:
    ctx = dump.get(i)
    if ctx is None: rows.append((i, None, None, None, "", None)); continue
    titles = [norm_t(t) for t in re.findall(r"^\[\d+\] Wikipedia[^:\n]*: (.+)$", ctx, re.M)]  # Wikipedia sources only (Wikivoyage "Singapore" is not the gold article)
    g = gold.get(i, set())
    art = any(t in g or any(t == x or t.startswith(x + " ") for x in g) for t in titles) if g else None
    cg = grams(W(ctx))
    cov = max((len(grams(W(p["text"])) & cg) / max(1, len(grams(W(p["text"])))) for p in R.get(i, [])[:3]), default=None) if R.get(i) else None
    sents = [x for p in R.get(i, [])[:3] for x in re.split(r"(?<=[.!?])\s+", p["text"]) if len(W(x)) >= 8]
    sh = max((len(grams(W(x)) & cg) / max(1, len(grams(W(x)))) for x in sents), default=0.0) >= 0.6
    rows.append((i, art, cov, bool(ctx), ";".join(sorted(set(titles)))[:120], sh))
lab = sys.argv[2] if len(sys.argv) > 2 else sys.argv[1]
have = [r for r in rows if r[1] is not None or r[2] is not None]
n_g = [r for r in rows if r[1] is not None]
n_p = [r for r in rows if r[2] is not None]
print(f"== {lab}: items {len(ids)}, in dump {sum(1 for r in rows if r[3] is not None)}, with context {sum(1 for r in rows if r[3])}")
print(f"gold-article hit {sum(1 for r in n_g if r[1])}/{len(n_g)} (items with a gold wiki title)")
print(f"gold-passage hit (cov>=0.5) {sum(1 for r in n_p if r[2] >= 0.5)}/{len(n_p)}; any overlap (>=0.2) {sum(1 for r in n_p if r[2] >= 0.2)}/{len(n_p)}; mean cov {sum(r[2] for r in n_p)/max(1,len(n_p)):.3f}")
print(f"gold-sentence hit (a >=8-word sentence of the top-3 oracle passages, >=60% of its 4-grams in Context) {sum(1 for r in n_p if r[5])}/{len(n_p)}")
if "-v" in sys.argv:
    for r in rows: print(r[0], r[1], None if r[2] is None else round(r[2], 2), r[4])
json.dump([{"id": r[0], "art": r[1], "cov": r[2], "sent": r[5], "titles": r[4]} for r in rows], open(f"goldhit-{lab}.json", "w"))
