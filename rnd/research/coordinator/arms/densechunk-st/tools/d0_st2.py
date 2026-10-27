"""DENSECHUNK-ST2 step 0, D0 per item on the 180 public self-test items (0 LLM / 0 judge). Run: python3 -I d0_st2.py
Reads runs/st2-<pack>.jsonl (passes off, extra, off2; tree wt/packs with packDense2 "extra") and, for the differential,
runs/st-<pack>.jsonl (DENSECHUNK-ST: off, on, off2). Fact chunks / fact article as d0_st.py (in_pack_facts, chunk_index
over the article's chunks by start; article = source.article_id). Per mode: fact chunk / article in raw[:6], in raw[:8]
(the appended list), in kept; empty kept; appended = extra.raw[len(off.raw):] when off.raw is its prefix; appended chunks
in kept (slot share). Writes aggregates/d0-st2.json (counts/ids only)."""
import json, os, re, sqlite3, statistics as st
ROOT = "<workspace>"; ARM = f"{ROOT}/rnd/research/coordinator/arms/densechunk-st"
ST = f"{ROOT}/rnd/research/packs/selftest"
SHA = open(f"{ARM}/DENSECHUNK-ST2-criterion.sha256").read().split()[0]
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se",
         "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
SE = {p for p in PACKS if p.startswith("qa-")}
load = lambda f: [json.loads(l) for l in open(f) if l.strip()]
def pub(p): return f"{ROOT}/shared-data/packs/{'wave2' if p in ('boar-factbook', 'boar-simplewiki-en') else 'wave1'}/{p}.sqlite"
CID = re.compile(r"^pack:(?:local-)?([^:]+):(\d+)$")
def cid(ref, pack):
    m = CID.match(ref.get("chunkId") or ""); return int(m.group(2)) if m and m.group(1) == pack else None
def pct(a, q):
    a = sorted(a); return None if not a else a[min(len(a) - 1, int(round(q * (len(a) - 1))))]
def passes(lines):
    out, seen = {}, {}
    for l in lines:
        n = seen.get((l["mode"], l["id"]), 0); seen[(l["mode"], l["id"])] = n + 1
        out.setdefault(l["mode"] + ("2" if n else ""), {})[l["id"]] = l
    return out
def key(l):  # everything the engine returned except timings
    return json.dumps([[x.get(k) for k in ("chunkId", "title", "section", "source", "similarity", "via")] for x in l["raw"]]
                      + [[x.get(k) for k in ("chunkId", "title", "section", "source")] for x in l["kept"]] + [l.get("task"), l.get("query"), l.get("k"), l.get("codes")])
def appended(off, ex):
    o = [x.get("chunkId") for x in off["raw"]]; e = [x.get("chunkId") for x in ex["raw"]]
    return (e[:len(o)] == o), e[len(o):]

def do_pack(p):
    items = load(f"{ST}/{p}.jsonl")
    db = sqlite3.connect(f"file:{pub(p)}?mode=ro", uri=True)
    ch_art = dict(db.execute("SELECT id, article_id FROM chunks").fetchall())
    art_chunks = lambda a: [r[0] for r in db.execute("SELECT id FROM chunks WHERE article_id=? ORDER BY start", (a,))]
    nlead = db.execute("SELECT count(*) FROM lead_vecs").fetchone()[0]
    R = passes(load(f"{ARM}/runs/st2-{p}.jsonl")); S = passes(load(f"{ARM}/runs/st-{p}.jsonl"))
    rows = []
    for it in items:
        i = it["id"]; fa = it["source"]["article_id"]; fcs = set()
        for f in it["in_pack_facts"]:
            if f.get("chunk_index") is None: continue
            cs = art_chunks(f.get("article", fa))
            if f["chunk_index"] < len(cs): fcs.add(cs[f["chunk_index"]])
        row = {"id": i, "pack": p, "family": "SE" if p in SE else "topic"}
        for mode in ("off", "extra", "off2"):
            l = R.get(mode, {}).get(i)
            if not l: continue
            cr = lambda xs: any(c in fcs for c in (cid(x, p) for x in xs) if c)
            ar = lambda xs: any(ch_art.get(c) == fa for c in (cid(x, p) for x in xs) if c)
            row[mode] = {"chunk_raw6": cr(l["raw"][:6]), "chunk_raw8": cr(l["raw"][:8]), "art_raw6": ar(l["raw"][:6]), "art_raw8": ar(l["raw"][:8]),
                         "chunk_kept": cr(l["kept"]), "art_kept": ar(l["kept"]), "kept_n": len(l["kept"]), "raw_n": len(l["raw"]), "ms": l["ms"],
                         "scan": [d for d in l.get("dense", []) if d["leads"] == nlead]}
        o, e = R.get("off", {}).get(i), R.get("extra", {}).get(i)
        if o and e:
            pre, app = appended(o, e); kept = {x.get("chunkId") for x in e["kept"]}
            row["prefix_ok"] = pre; row["appended"] = app; row["appended_kept"] = [c for c in app if c in kept]
            row["churn_kept"] = [x.get("chunkId") for x in o["kept"]] != [x.get("chunkId") for x in e["kept"]]
            row["off_kept_lost"] = [x.get("chunkId") for x in o["kept"] if x.get("chunkId") not in kept]
        if o and i in S.get("off", {}): row["off_same_as_st"] = key(o) == key(S["off"][i])
        if o and i in R.get("off2", {}): row["off_repeat_same"] = key(o) == key(R["off2"][i])
        rows.append(row)
    return rows

def agg(rows):
    a = {"n": len(rows)}
    for mode in ("off", "extra"):
        r = [x[mode] for x in rows if mode in x]
        a[mode] = {k: sum(y[k] for y in r) for k in ("chunk_raw6", "chunk_raw8", "art_raw6", "art_raw8", "chunk_kept", "art_kept")} | {"empty_kept": sum(y["kept_n"] == 0 for y in r), "kept_slots": sum(y["kept_n"] for y in r), "n": len(r)}
    a["appended_slots_raw"] = sum(len(x.get("appended", [])) for x in rows); a["appended_items"] = sum(bool(x.get("appended")) for x in rows)
    a["appended_kept_slots"] = sum(len(x.get("appended_kept", [])) for x in rows)
    a["appended_kept_share"] = round(a["appended_kept_slots"] / a["extra"]["kept_slots"], 3) if a["extra"]["kept_slots"] else None
    a["prefix_ok"] = f"{sum(bool(x.get('prefix_ok')) for x in rows)}/{sum('prefix_ok' in x for x in rows)}"
    a["off_kept_lost_items"] = sum(bool(x.get("off_kept_lost")) for x in rows); a["churn_kept"] = sum(bool(x.get("churn_kept")) for x in rows)
    a["off_same_as_st"] = f"{sum(bool(x.get('off_same_as_st')) for x in rows)}/{sum('off_same_as_st' in x for x in rows)}"
    a["off_repeat_same"] = f"{sum(bool(x.get('off_repeat_same')) for x in rows)}/{sum('off_repeat_same' in x for x in rows)}"
    for mode in ("off", "extra", "off2"):
        ms = [x[mode]["ms"] for x in rows if mode in x and x[mode]["ms"] is not None]
        a[f"ms_p50_{mode}"] = round(st.median(ms), 1) if ms else None
    sc = [s["leadMs"] + s["chunkMs"] for x in rows for s in x.get("extra", {}).get("scan", [])]
    a["scan_ms"] = {"p50": pct(sc, .5), "p95": pct(sc, .95), "max": max(sc) if sc else None,
                    "first_load_ms": max([s["loadMs"] for x in rows for s in x.get("extra", {}).get("scan", [])], default=None)}
    el = lambda k: {"enter": sum(1 for x in rows if "extra" in x and x["extra"][k] and not x["off"][k]), "leave": sum(1 for x in rows if "extra" in x and x["off"][k] and not x["extra"][k])}
    a["chunk_kept_enter_leave"] = el("chunk_kept"); a["art_kept_enter_leave"] = el("art_kept")
    return a

def main():
    items = []
    for p in PACKS:
        if not os.path.exists(f"{ARM}/runs/st2-{p}.jsonl"): print(f"skip {p} (not ready)"); continue
        items += do_pack(p)
    out = {"criterion_sha256": SHA, "mode": "extra", "D": 2, "packs_done": sorted({x["pack"] for x in items}, key=PACKS.index),
           "per_pack": {p: agg([x for x in items if x["pack"] == p]) for p in PACKS if any(x["pack"] == p for x in items)},
           "family": {f: agg([x for x in items if x["family"] == f]) for f in ("SE", "topic")}, "all": agg(items), "items": items}
    json.dump(out, open(f"{ARM}/aggregates/d0-st2.json", "w"), indent=1)
    a = out["all"]; print(json.dumps({k: a[k] for k in ("n", "off", "extra", "appended_kept_share", "prefix_ok", "off_same_as_st", "off_repeat_same", "ms_p50_off2", "ms_p50_extra", "scan_ms")}))
main()
