#!/usr/bin/env python3
"""QREWRITE scorer (criterion 60fdc688). python3 -I score.py <label> [<label> ...] -> ../aggregates/score.<label>.json; prints a table row per label.
MAIN: chunklevel.py score() on replays/main.<label>.jsonl (92 keyed). ST: own-article raw/kept on replays/st.<label>.jsonl (PACKPROOF match)."""
import json, sys, re, os
A = "<workspace>/rnd/research/coordinator/arms"; Q = A + "/qrewrite"; CM = A + "/coverage-map"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
src = open(CM + "/tools/chunklevel.py").read(); src = src[:src.index("ARMS = {")]
G = {"__name__": "cl"}; exec(compile(src, "chunklevel.py", "exec"), G)
OWN = json.load(open(A + "/packproof/in/own.json")); ITEMS = {x["id"]: x["pack"] for x in json.load(open(A + "/packproof/in/items.json"))["items"]}
HP = {"qa-health-se", "boar-firstaid-en", "boar-medlineplus-en"}; hmain = lambda i: i.startswith(("lan-hlt-", "vit-hlt-", "dng-"))
CURP = {}
def match(arts, c, pack=None):
    # keptFull/rawFull carry docId (no source): own article = docId pack:local-<item pack>:a<article id> (the PACKPROOF url+title match, own pack copy)
    d = c.get("docId") or ""
    return any(d == f"pack:local-{pack}:a{a['article']}" for a in arts)
def st(label):
    rows = {r["id"]: r for r in rd(f"{Q}/replays/st.{label}.jsonl")}; out = {}
    for i, r in rows.items():
        kept = r.get("keptFull") or []; raw = r.get("rawFull") or []; p = ITEMS[i]
        own_k = [match(OWN[i], c, p) for c in kept]
        out[i] = dict(raw=any(match(OWN[i], c, p) for c in raw), kept=any(own_k), nkept=len(kept), nown=sum(own_k), keptids=[c.get("chunkId") for c in kept], pack=ITEMS[i], q=r.get("query"))
    return out
def main(label):
    s = G["score"](f"{Q}/replays/main.{label}.jsonl"); rows = {r["id"]: r for r in rd(f"{Q}/replays/main.{label}.jsonl")}
    for i in s:
        if s[i] is not None: s[i]["keptids"] = [c.get("chunkId") for c in rows[i].get("keptFull") or []]; s[i]["q"] = rows[i].get("query")
    return s
def summarize(label, base="base"):
    r = {}
    if os.path.exists(f"{Q}/replays/main.{label}.jsonl"):
        m, b = main(label), main(base)
        ch = sum(bool(v and v["chunk"]) for v in m.values()); bch = sum(bool(v and v["chunk"]) for v in b.values())
        gained = [i for i in m if m[i] and m[i]["chunk"] and not (b[i] and b[i]["chunk"])]; lost = [i for i in m if b[i] and b[i]["chunk"] and not (m[i] and m[i]["chunk"])]
        rows_m = {x["id"]: x for x in rd(f"{Q}/replays/main.{label}.jsonl")}; rows_b = {x["id"]: x for x in rd(f"{Q}/replays/main.{base}.jsonl")}
        chg = [i for i in rows_m if [c.get("chunkId") for c in rows_m[i].get("keptFull") or []] != [c.get("chunkId") for c in rows_b[i].get("keptFull") or []]]
        r["main"] = dict(chunk=ch, base=bch, delta=ch - bch, cm=sum(bool(v and v["chunk"] and v["set"] == "cm") for v in m.values()), v01=sum(bool(v and v["chunk"] and v["set"] == "v0.1") for v in m.values()),
                         art=sum(bool(v and v["art"]) for v in m.values()), gained=gained, lost=lost, health_lost=[i for i in lost if hmain(i)], changed=chg, n_changed=len(chg))
    if os.path.exists(f"{Q}/replays/st.{label}.jsonl"):
        s, b = st(label), st(base); n = len(s)
        kept = sum(v["kept"] for v in s.values()); bk = sum(v["kept"] for v in b.values())
        lost = [i for i in s if b[i]["kept"] and not s[i]["kept"]]; gained = [i for i in s if s[i]["kept"] and not b[i]["kept"]]
        nk = sum(v["nkept"] for v in s.values()); no = sum(v["nown"] for v in s.values())
        r["st"] = dict(n=n, raw=sum(v["raw"] for v in s.values()), kept=kept, base_kept=bk, base_raw=sum(v["raw"] for v in b.values()), delta=kept - bk, gained=gained, lost=lost,
                       health_lost=[i for i in lost if s[i]["pack"] in HP], crowd=round(1 - no / nk, 3) if nk else None, mean_kept=round(nk / n, 2),
                       changed=sum(s[i]["keptids"] != b[i]["keptids"] for i in s),
                       qform24=dict(kept=sum(s[i]["kept"] for i in s if i in Q24), base=sum(b[i]["kept"] for i in s if i in Q24)),
                       by_pack={p: [sum(s[i]["kept"] for i in s if s[i]["pack"] == p), sum(b[i]["kept"] for i in s if b[i]["pack"] == p)] for p in sorted(set(ITEMS.values()))})
    json.dump(r, open(f"{Q}/aggregates/score.{label}.json", "w"), indent=1); return r
Q24 = {i for i, v in json.load(open(Q + "/items/oracle.meta.json")).items() if v == "qform-F5"}
if __name__ == "__main__":
    for lab in sys.argv[1:]:
        r = summarize(lab); m = r.get("main"); s = r.get("st")
        print(lab, "| MAIN", f"{m['chunk']} (d{m['delta']:+d}, cm {m['cm']}, v01 {m['v01']}, gained {len(m['gained'])}, lost {len(m['lost'])} {m['lost']}, health lost {m['health_lost']}, changed {m['n_changed']})" if m else "-",
              "| ST", f"raw {s['raw']} (base {s['base_raw']}) kept {s['kept']} (d{s['delta']:+d}) lost {len(s['lost'])} health lost {s['health_lost']} crowd {s['crowd']} meank {s['mean_kept']} chg {s['changed']} q24 {s['qform24']}" if s else "-")
