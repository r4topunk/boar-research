#!/usr/bin/env python3
"""exp-31 (A): per-item pack coverage + retrieval outcome for the post author's example question classes (bench v0.1 PUBLIC only).

Read-only. Coverage: the item's answer key (precheck must_any/must_k, same matcher as sonar/tools/key_in_context.py) is
checked in the installed text of its reference articles (+ a few named extra titles) per pack:
  kitA   = bundled corpus*.json @0cfd4a77 (300 + 1k + 4k docs) + boar-crypto + boar-wikivoyage-en
  vital5 = wiki-vital5 (lead sections of ~50k Vital Articles)
  top100k= boar-wiki-en-top100k (Mac mini, fixed sha 9123b372; built, not in any shipped kit)
  live   = live Wikipedia plaintext cached by exp-03 (proxy for the full 15-shard enwiki pack when the article is in its
           top-1M full-text set; see exp-04 ranks)
Retrieval: traces under boar-eval/runs/night-2026-10-01 (non-blind); raw = retrieval.raw, pre = last `sources` event
(exact passage text in *-kic runs, else article mode), shown = answer.shown. Judged ratio = sum boar / sum ref over
both orders and seeds s42+s43 (judge.v1).
Usage: python3 items.py > items.out.txt   (writes items.json next to it)
"""
import json, os, re, sqlite3, subprocess, sys, urllib.parse
B = "<workspace>"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = ["x"]
exec(open(f"{B}/rnd/research/sonar/tools/key_in_context.py").read().split('if __name__ == "__main__":')[0])

IDS = {
    "1 humanities": ["vit-hum-001", "vit-hum-002", "vit-hum-003", "vit-hum-005", "vit-hum-006"],
    "2 crypto/cryptography": ["vit-cry-001", "vit-cry-002", "vit-cry-004", "vit-cry-005", "vit-cry-006", "vit-cry-007", "vit-cry-010"],
    "3 country overview": ["lan-exp-001", "lan-exp-003", "lan-exp-004", "lan-exp-007", "vit-sci-002"],
    "4 places": ["food-006", "food-001"],
    "5 travel": ["vit-trv-003", "vit-trv-004", "vit-hlt-002", "trv-002", "trv-004"],
}
EXTRA = {  # extra installed titles worth checking (named in the question or the obvious guide)
    "vit-trv-003": ["Wikivoyage: Pai", "Wikivoyage: Chiang Mai", "Wikivoyage: Mae Hong Son Loop"],
    "vit-trv-004": ["Wikivoyage: Via Francigena", "Via Francigena"],
    "vit-hlt-002": ["Wikivoyage: Altitude sickness"],
    "food-006": ["Wikivoyage: Tokyo"], "food-001": ["Wikivoyage: Berlin"],
    "trv-002": ["Wikivoyage: Brazil"], "trv-004": ["Wikivoyage: Lisbon"],
    "lan-exp-004": ["Wikivoyage: Kyoto"], "lan-exp-003": ["Wikivoyage: Kenya"], "lan-exp-001": ["Wikivoyage: Singapore"],
    "lan-exp-007": ["Wikivoyage: Greenland"], "vit-sci-002": ["Wikivoyage: Japan", "Wikivoyage: Germany"],
    "vit-cry-002": ["eip:7805"], "vit-cry-004": ["eip:7594", "PeerDAS"], "vit-cry-001": ["Post-quantum cryptography", "Elliptic Curve Digital Signature Algorithm"],
    "vit-cry-005": ["Privacy Pools"], "vit-cry-007": ["d/acc"],
}
RUNS = {  # label -> (trace file, judgment files)
    "A-1.5B": ("ios-main-s42", ["ios-main-s42", "ios-main-s43"]),
    "A-4B": ("and-qwen-s42", ["and-qwen-s42", "and-qwen-s43"]),
    "A+v5-1.5B": ("ios-main-v5-s42-kic", ["ios-main-v5-s42", "ios-main-v5-s43"]),
    "A+v5-4B": ("and-main-v5-s42", ["and-main-v5-s42", "and-main-v5-s43"]),
    "A+v5+top100k-1.5B": ("ios-enwiki-s42-kic", []),
}
R = f"{B}/boar-eval/runs/night-2026-10-01"
qs = {json.loads(l)["id"]: json.loads(l) for l in open(f"{B}/boar-eval/bench/v0.1/questions.public.jsonl")}

def wiki_titles(q):
    out = []
    for u in q.get("reference_sources", []):
        for host, pre in (("en.wikipedia.org/wiki/", ""), ("en.wikivoyage.org/wiki/", "Wikivoyage: ")):
            if host in u: out.append(pre + urllib.parse.unquote(u.split(host)[1]).replace("_", " "))
        if u.startswith("enwikivoyage:"): out.append("Wikivoyage: " + u.split(":", 1)[1])
    return out

# --- installed text per pack -------------------------------------------------------------------------------------
cry = sqlite3.connect(f"file:{B}/shared-data/crypto/boar-crypto.sqlite?mode=ro", uri=True)
voy = sqlite3.connect(f"file:{B}/shared-data/packs/boar-wikivoyage-en.sqlite?mode=ro", uri=True)
v5 = sqlite3.connect(f"file:{B}/shared-data/packs/wiki-vital5.sqlite?mode=ro", uri=True)
corp = {}
for f in ("corpus.json", "corpus-standard.json", "corpus-full.json"):
    for d in json.loads(subprocess.check_output(["git", "-C", f"{B}/boar-app", "show", f"0cfd4a77:assets/corpus/{f}"])):
        corp.setdefault(d["title"].lower(), d["body"])
def f2(db, title):
    row = db.execute("SELECT block_id, off, len FROM articles WHERE title = ? COLLATE NOCASE ORDER BY views DESC LIMIT 1", (title,)).fetchone()
    if not row:
        r = db.execute("SELECT article_id FROM redirects WHERE title = ? COLLATE NOCASE LIMIT 1", (title,)).fetchone()
        if r: row = db.execute("SELECT block_id, off, len FROM articles WHERE id = ?", (r[0],)).fetchone()
    if not row: return None
    return zstd.decompress(db.execute("SELECT zdata FROM blocks WHERE id = ?", (row[0],)).fetchone()[0])[row[1]:row[1] + row[2]].decode("utf-8", "replace")
def eip(n):
    row = cry.execute("SELECT title FROM articles WHERE title LIKE ? LIMIT 1", (f"EIP-{n}:%",)).fetchone()
    return (row[0], f2(cry, row[0])) if row else (None, None)
def kitA(t):
    if t.startswith("eip:"):
        return eip(t[4:])[1]
    if t.startswith("Wikivoyage: "): return f2(voy, t[12:])
    return f2(cry, t) or corp.get(t.lower())
def vital5(t):
    if t.startswith("Wikivoyage: ") or t.startswith("eip:"): return None
    rows = v5.execute("SELECT body FROM chunks WHERE title = ? COLLATE NOCASE", (t,)).fetchall()
    return "\n".join(r[0] for r in rows) if rows else None
def live(t):
    p = f"{B}/rnd/research/sonar/exp/03-intro-vs-body-coverage/fulltext/{re.sub(r'[^A-Za-z0-9]+', '_', t)}.txt"
    return open(p).read() if os.path.exists(p) else None

all_ids = [i for v in IDS.values() for i in v]
wtitles = sorted({t for i in all_ids for t in wiki_titles(qs[i]) + EXTRA.get(i, []) if not t.startswith(("Wikivoyage: ", "eip:"))})
remote = json.loads(subprocess.run(["ssh", "-o", "BatchMode=yes", "MINI_HOST",
                                    "/opt/homebrew/bin/python3 /tmp/sonar31-f2text.py <runner>/shared-data/packs/boar-wiki-en-top100k.sqlite"],
                                   input=json.dumps(wtitles), capture_output=True, text=True, check=True).stdout)
def top100k(t):
    v = remote.get(t); return v["text"] if v else None

# --- traces + judgments ------------------------------------------------------------------------------------------
res = Resolver(True)
def load(run): return {json.loads(l)["itemId"]: json.loads(l) for l in open(f"{R}/{run}.traces.jsonl") if l.strip()}
traces = {lab: load(f) for lab, (f, _) in RUNS.items()}
def ratio(files, iid):
    b = r = 0
    for f in files:
        for l in open(f"{R}/{f}.judgments.jsonl"):
            j = json.loads(l)
            if j["queryId"] == iid and j.get("ok") and j.get("mapped"):
                b += sum(j["mapped"]["boar"].values()); r += sum(j["mapped"]["ref"].values())
    return round(b / r, 2) if r else None
def outcome(t, g):
    raw = t["retrieval"]["raw"]; ev = [e for e in t.get("events", []) if e.get("type") == "sources"]
    pre = ev[-1]["sources"] if ev else []
    def hit(refs, exact):
        if not g or not refs: return None if not g else False
        txt = [s.get("text") if exact else res.text(s) for s in refs]
        return key_hit("\n".join(x for x in txt if x), g)
    rc = [c for c in t["route"].get("reasonCodes", []) if c.startswith(("context:", "grounding:", "retrieve:"))]
    return {"raw": [s["title"] for s in raw], "raw_key": hit(raw, False), "raw_unresolved": sum(res.text(s) is None for s in raw),
            "pre": [s["title"] for s in pre], "pre_key": hit(pre, bool(pre) and all("text" in s for s in pre)),
            "shown": [s["title"] if isinstance(s, dict) else s for s in t["answer"].get("shown", [])], "declined": t["answer"]["declined"],
            "task": t["route"].get("task"), "codes": rc}

out = {}
for cls, ids in IDS.items():
    print(f"\n######## class {cls}")
    for i in ids:
        q = qs[i]; g = q["grading"] if (q["grading"].get("must_any") or q["grading"].get("must_k")) else None
        titles = wiki_titles(q) + [t for t in EXTRA.get(i, []) if t not in wiki_titles(q)]
        cov = {}
        for t in titles:
            row = {}
            for name, fn in (("kitA", kitA), ("vital5", vital5), ("top100k", top100k), ("live", live)):
                if name in ("top100k", "live") and t.startswith(("Wikivoyage: ", "eip:")): continue
                tx = fn(t)
                row[name] = None if tx is None else (len(tx), key_hit(tx, g) if g else "n/a")
            cov[t] = row
        rec = {"q": q["question"], "category": q["category"], "origin": q["origin"], "keyed": bool(g), "coverage": cov, "runs": {}}
        print(f"\n{i} [{q['category']}, {q['origin']}] {q['question']}")
        for t, row in cov.items():
            print(f"   cov {t!r}: " + "; ".join(f"{k}={'-' if v is None else f'{v[0]}ch key={v[1]}'}" for k, v in row.items()))
        for lab, (f, jf) in RUNS.items():
            t = traces[lab].get(i)
            if not t: continue
            o = outcome(t, g); o["ratio"] = ratio(jf, i) if jf else None; rec["runs"][lab] = o
            print(f"   {lab:18s} raw[{o['raw_key']}{'/unres'+str(o['raw_unresolved']) if o['raw_unresolved'] else ''}]={o['raw'][:5]} | pre[{o['pre_key']}]={o['pre']} | shown={o['shown']} declined={o['declined']} task={o['task']} ratio={o['ratio']} {o['codes']}")
        out[i] = rec
json.dump(out, open(f"{HERE}/items.json", "w"), indent=1, ensure_ascii=False)
