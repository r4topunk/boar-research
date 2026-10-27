"""exp-34: where does the oracle's judged gain live? Per item: Q450 - engine (s44) mean rubric, grouped by the
retrieval loss category of a replay trace file (gold sentence / wrong passage / gate-dropped / in pack not retrieved /
outside top100k / no Wikipedia gold).  python3 where.py <kic traces> [pack-ceiling N]"""
import json, sys, statistics as st, collections
A = "<workspace>/rnd/research/anvil/exp/"
def per(f):
    d = collections.defaultdict(list)
    for l in open(f):
        r = json.loads(l)
        if r.get("ok"): d[r["queryId"]].append(st.mean(r["mapped"]["boar"].values()))
    return {k: st.mean(v) for k, v in d.items()}
eng = per("<workspace>/boar-eval/runs/and-qwen-s44/and-qwen-s44.judgments.jsonl")
q = per(A + "oracle/runs/qwen3-4b-Q450.judgments.jsonl"); r = per(A + "oracle/runs/qwen3-4b-R450.judgments.jsonl")
cb = per(A + "outofkit/runs/srv-qwen3-4b.judgments.jsonl")
ceil = {x["id"]: x for x in json.load(open("ceiling.json"))}
N = int(sys.argv[2]) if len(sys.argv) > 2 else 100000
gold = collections.defaultdict(set)
for l in open(A + "oracle/articles.jsonl"):
    a = json.loads(l)
    if a["kind"] == "wiki": gold[a["id"]].add(a["title"].lower())
lab = sys.argv[1].split("/")[-1].split(".")[0]
gh = {x["id"]: x for x in json.load(open(f"goldhit-{lab}.json"))}
cat = {}
for l in open(sys.argv[1]):
    t = json.loads(l); i = t["itemId"]
    if i not in ceil: continue
    isw = lambda x: (x.get("source") or "Wikipedia").startswith("Wikipedia")
    raw = {x["title"].lower() for e in t["events"] if e.get("type") == "retrieve" for x in e.get("sources", []) if isw(x)}
    g = gold.get(i, set())
    if gh[i]["sent"]: c = "1 gold sentence in context"
    elif not g: c = "6 no Wikipedia gold"
    elif gh[i]["art"]: c = "2 right article, wrong passage"
    elif raw & g: c = "3 retrieved, dropped by gates/compression"
    elif ceil[i]["best"] and ceil[i]["best"] <= N: c = "4 in pack, not retrieved"
    else: c = "5 outside pack"
    cat[i] = c
print(f"{lab}: per category, n / sum of (Q450 - engine) / sum of (R450 - engine) / mean closed-book rubric")
for c in sorted(set(cat.values())):
    ids = [i for i in cat if cat[i] == c and i in eng and i in q]
    print(f"  {c:42} n={len(ids):2}  dQ {sum(q[i]-eng[i] for i in ids):+6.2f}  dR {sum(r[i]-eng[i] for i in ids):+6.2f}  closed {st.mean(cb[i] for i in ids if i in cb):.2f}")
ids = [i for i in cat if i in eng and i in q]
print(f"  {'TOTAL':42} n={len(ids):2}  dQ {sum(q[i]-eng[i] for i in ids):+6.2f}  dR {sum(r[i]-eng[i] for i in ids):+6.2f}")
