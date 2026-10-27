# Declined compact drafts from night-2026-10-01 iPhone-profile traces (read-only) + precheck label + source text from packs.
import json, re, sqlite3, sys, collections
import compression.zstd as zstd
sys.path.insert(0, "<workspace>/boar-eval/scorers/vendor/lantern"); import precheck
R = "<workspace>/boar-eval/runs/night-2026-10-01/"
Q = {}
for f in ["<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "<workspace>/boar-eval/bench/v0.1/slices/citation-pt.jsonl"]:
    for l in open(f): r = json.loads(l); Q[r["id"]] = r
PACKS = {"Wikivoyage": "<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", "Wikipedia": "<workspace>/shared-data/packs/wiki-vital5.sqlite"}
crypto = sqlite3.connect("<workspace>/shared-data/crypto/boar-crypto.sqlite")
dbs = {k: sqlite3.connect(v) for k, v in PACKS.items()}
def article(title):
    pre, _, t = title.partition(": ")
    for db in ([dbs[pre]] if pre in dbs else [crypto, *dbs.values()]):
        try:
            a = db.execute("select block_id, off, len from articles where title = ? collate nocase", (t,)).fetchone()
        except sqlite3.OperationalError:
            a = None
        if a:
            z = db.execute("select zdata from blocks where id=?", (a[0],)).fetchone()[0]
            return zstd.decompress(z)[a[1]:a[1] + a[2]].decode("utf8", "replace")
    return None
CODES = ("all-citations-removed-declined-compact", "uncited-with-sources-declined-compact")
out, seen = [], set()
for f in ["ios-main-s42", "ios-main-s43", "ios-main-v58x-s42", "ios-main-v5-t0"]:
    for l in open(R + f + ".traces.jsonl"):
        r = json.loads(l)
        code = next((c for c in CODES if any(c in x for x in r["route"]["reasonCodes"])), None)
        if not code: continue
        draft = "".join(e.get("text", "") for e in r["events"] if e["type"] == "token").strip()
        key = (r["itemId"], draft)
        if key in seen or not draft: continue
        seen.add(key)
        titles = list(dict.fromkeys((r["answer"].get("shown") or []) + [s["title"] for s in r["retrieval"].get("raw", [])]))
        q = Q.get(r["itemId"])
        label = precheck.grade(q, {"answer": re.sub(r"\[\d+\]", "", draft), "declined": False})[0] if q and q.get("grading") else "unlabeled"
        srcs = [(t, article(t)) for t in titles[:4]]
        out.append({"run": f, "id": r["itemId"], "question": r["question"], "code": code, "draft": draft, "label": label,
                    "category": q.get("category") if q else None, "danger": q.get("danger") if q else None,
                    "titles": titles, "sources": [{"title": t, "text": (x or "")[:6000]} for t, x in srcs]})
json.dump(out, open("drafts.json", "w"), ensure_ascii=False)
print(len(out), collections.Counter(o["label"] for o in out), collections.Counter(o["code"] for o in out))
print("with source text:", sum(1 for o in out if any(s["text"] for s in o["sources"])))
print("unique items:", len({o["id"] for o in out}))
