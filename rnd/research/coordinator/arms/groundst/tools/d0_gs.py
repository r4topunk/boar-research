"""GROUND-ST step 0, D0 per item on the 180 public self-test items (0 LLM / 0 judge). Run: python3 -I d0_gs.py
Reads runs/gs-<pack>.jsonl (passes off, ground, top1, off2; tree wt/groundst) and, for the identity check,
arms/densechunk-st/runs/st-<pack>.jsonl (ST2's reference OFF = its first "off" pass). Fact chunks / fact article as d0_st2.py
(in_pack_facts chunk_index over the article's chunks by start; article = source.article_id). Per mode: fact chunk / article in
raw[:6], in kept; empty kept; kept tokens. D0 loss classes on OFF (items with the fact chunk / article in raw6 but not kept),
from the replay's `diag` (OFF keep-stage reconstruction): not-substantive / compression (not in comp) / health-filter (in comp,
health question) / grounding (in comp, not on topic) / other (reconstruction keeps it, engine does not). Recovery per class by
ground and top1. Writes aggregates/d0-gs.json (ids/counts only).
Addendum 1: `python3 -I d0_gs.py perpack` reads runs/gs-<pack>.perpack.jsonl (passes off, perpack, off2) and writes
aggregates/d0-gs.perpack.json; adds keep-step ms (keepMs) p50 per mode, OFF-kept chunks cut by the variant, the
packground:cut-N count, OFF identity vs the step-0 OFF (runs/gs-<pack>.jsonl) and the recovery of the 9 step-0 items."""
import json, os, re, sqlite3, statistics as st, sys
X = sys.argv[1] if len(sys.argv) > 1 else None
SFX = f".{X}" if X else ""
VARS = (X,) if X else ("ground", "top1")
ROOT = "<workspace>"; ARM = f"{ROOT}/rnd/research/coordinator/arms/groundst"
REF = f"{ROOT}/rnd/research/coordinator/arms/densechunk-st/runs"
ST = f"{ROOT}/rnd/research/packs/selftest"
SHA = open(f"{ARM}/GROUND-ST-criterion.sha256").read().split()[0]
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se",
         "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
SE = {p for p in PACKS if p.startswith("qa-")}
MODES = ("off",) + VARS + ("off2",)
load = lambda f: [json.loads(l) for l in open(f) if l.strip()]
def pub(p): return f"{ROOT}/shared-data/packs/{'wave2' if p in ('boar-factbook', 'boar-simplewiki-en') else 'wave1'}/{p}.sqlite"
CID = re.compile(r"^pack:(?:local-)?([^:]+):(\d+)$")
def cid(c, pack):
    m = CID.match(c or ""); return int(m.group(2)) if m and m.group(1) == pack else None
def passes(lines):
    out, seen = {}, {}
    for l in lines:
        n = seen.get((l["mode"], l["id"]), 0); seen[(l["mode"], l["id"])] = n + 1
        out.setdefault(l["mode"] + ("2" if n else ""), {})[l["id"]] = l
    return out
def key(l):  # everything the engine returned except timings (gate_st2.py)
    return json.dumps([[x.get(k) for k in ("chunkId", "title", "section", "source", "similarity", "via")] for x in l["raw"]]
                      + [[x.get(k) for k in ("chunkId", "title", "section", "source")] for x in l["kept"]] + [l.get("task"), l.get("query"), l.get("k"), l.get("codes")])
def keyrk(l):  # raw + kept only
    return json.dumps([[x.get(k) for k in ("chunkId", "title", "section", "source", "similarity", "via")] for x in l["raw"]]
                      + [[x.get(k) for k in ("chunkId", "title", "section", "source")] for x in l["kept"]])
ids = lambda xs: [x.get("chunkId") for x in xs]

def stage(targets, d):
    """targets: full chunkIds (in raw6) of the fact chunk / article; d: OFF diag."""
    if not d: return "no-diag"
    if not any(t in d["sub"] for t in targets): return "not-substantive"
    if not any(t in d["comp"] for t in targets): return "compression"
    if d["health"]: return "health-filter"
    if not any(t in d["ground"] for t in targets): return "grounding"
    return "other"

def do_pack(p):
    items = load(f"{ST}/{p}.jsonl")
    db = sqlite3.connect(f"file:{pub(p)}?mode=ro", uri=True)
    ch_art = dict(db.execute("SELECT id, article_id FROM chunks").fetchall())
    art_chunks = lambda a: [r[0] for r in db.execute("SELECT id FROM chunks WHERE article_id=? ORDER BY start", (a,))]
    R = passes(load(f"{ARM}/runs/gs-{p}{SFX}.jsonl")); S = passes(load(f"{REF}/st-{p}.jsonl"))
    S0 = passes(load(f"{ARM}/runs/gs-{p}.jsonl")) if X else None
    rows = []
    for it in items:
        i = it["id"]; fa = it["source"]["article_id"]; fcs = set()
        for f in it["in_pack_facts"]:
            if f.get("chunk_index") is None: continue
            cs = art_chunks(f.get("article", fa))
            if f["chunk_index"] < len(cs): fcs.add(cs[f["chunk_index"]])
        isc = lambda c: cid(c, p) in fcs
        isa = lambda c: cid(c, p) is not None and ch_art.get(cid(c, p)) == fa
        row = {"id": i, "pack": p, "family": "SE" if p in SE else "topic"}
        for m in MODES:
            l = R.get(m, {}).get(i)
            if not l: continue
            row[m] = {"chunk_raw6": any(isc(c) for c in ids(l["raw"][:6])), "art_raw6": any(isa(c) for c in ids(l["raw"][:6])),
                      "chunk_kept": any(isc(c) for c in ids(l["kept"])), "art_kept": any(isa(c) for c in ids(l["kept"])),
                      "kept_n": len(l["kept"]), "raw_n": len(l["raw"]), "ms": l["ms"], "kept_tokens": l.get("keptTokens"),
                      "budget": l.get("budget"), "keep_codes": l.get("keepCodes", []), "keep_ms": l.get("keepMs"),
                      "kept_ids": ids(l["kept"])}
        o = R.get("off", {}).get(i)
        if o:
            d = o.get("diag")
            row["diag_agree"] = d["agree"] if d else None; row["diag_special"] = d["special"] if d else None
            if row["off"]["chunk_raw6"] and not row["off"]["chunk_kept"]:
                row["chunk_loss"] = stage([c for c in ids(o["raw"][:6]) if isc(c)], d)
            if row["off"]["art_raw6"] and not row["off"]["art_kept"]:
                row["art_loss"] = stage([c for c in ids(o["raw"][:6]) if isa(c)], d)
            for m in VARS:
                v = R.get(m, {}).get(i)
                if v:
                    row[f"{m}_off_kept_cut"] = [c for c in ids(o["kept"]) if c not in set(ids(v["kept"]))]
                    row[f"{m}_kept_changed"] = ids(o["kept"]) != ids(v["kept"])
                    row[f"{m}_raw_same"] = keyrk({"raw": o["raw"], "kept": []}) == keyrk({"raw": v["raw"], "kept": []})
            if i in S.get("off", {}): row["off_same_as_st2ref"] = key(o) == key(S["off"][i])
            if S0 and i in S0.get("off", {}): row["off_same_as_step0"] = key(o) == key(S0["off"][i])
            if i in R.get("off2", {}): row["off_repeat_same"] = key(o) == key(R["off2"][i])
        rows.append(row)
    return rows

def agg(rows):
    a = {"n": len(rows)}
    for m in MODES:
        r = [x[m] for x in rows if m in x]
        a[m] = {k: sum(y[k] for y in r) for k in ("chunk_raw6", "art_raw6", "chunk_kept", "art_kept")} | {
            "empty_kept": sum(y["kept_n"] == 0 for y in r), "empty_kept_retrieving": sum(y["kept_n"] == 0 and y["raw_n"] > 0 for y in r),
            "kept_slots": sum(y["kept_n"] for y in r), "n": len(r),
            "ms_p50": round(st.median([y["ms"] for y in r if y["ms"] is not None]), 1) if r else None,
            "keep_ms_p50": round(st.median([y["keep_ms"] for y in r if y.get("keep_ms") is not None]), 3) if any(y.get("keep_ms") is not None for y in r) else None,
            "total_ms_p50": round(st.median([y["ms"] + y["keep_ms"] for y in r if y["ms"] is not None and y.get("keep_ms") is not None]), 1) if any(y.get("keep_ms") is not None for y in r) else None}
    for lvl in ("chunk", "art"):
        L = [x for x in rows if f"{lvl}_loss" in x]
        cls = sorted({x[f"{lvl}_loss"] for x in L})
        a[f"{lvl}_loss"] = {"n": len(L), "by_stage": {c: sum(x[f"{lvl}_loss"] == c for x in L) for c in cls},
                            **{f"recovered_{m}": {c: sum(x[f"{lvl}_loss"] == c and x[m][f"{lvl}_kept"] for x in L) for c in cls} for m in VARS}}
    for m in VARS:
        a[f"{m}_off_kept_cut_items"] = sum(bool(x.get(f"{m}_off_kept_cut")) for x in rows)
        a[f"{m}_off_kept_cut_chunks"] = sum(len(x.get(f"{m}_off_kept_cut", [])) for x in rows)
        el = lambda k: {"enter": sum(1 for x in rows if m in x and x[m][k] and not x["off"][k]), "leave": sum(1 for x in rows if m in x and x["off"][k] and not x[m][k])}
        a[f"{m}_enter_leave"] = {"chunk_kept": el("chunk_kept"), "art_kept": el("art_kept")}
        a[f"{m}_kept_changed"] = sum(bool(x.get(f"{m}_kept_changed")) for x in rows)
        a[f"{m}_raw_same"] = f"{sum(bool(x.get(f'{m}_raw_same')) for x in rows)}/{sum(f'{m}_raw_same' in x for x in rows)}"
        a[f"{m}_tokens_over_budget"] = sum(1 for x in rows if m in x and x[m]["kept_tokens"] is not None and x[m]["budget"] is not None
                                           and x[m]["kept_tokens"] > max(x[m]["budget"], x["off"]["kept_tokens"] or 0))
        a[f"{m}_keep_codes"] = {c: sum(1 for x in rows if m in x and c in x[m]["keep_codes"]) for c in sorted({c for x in rows if m in x for c in x[m]["keep_codes"]})}
    a["off_same_as_st2ref"] = f"{sum(bool(x.get('off_same_as_st2ref')) for x in rows)}/{sum('off_same_as_st2ref' in x for x in rows)}"
    if X: a["off_same_as_step0"] = f"{sum(bool(x.get('off_same_as_step0')) for x in rows)}/{sum('off_same_as_step0' in x for x in rows)}"
    a["off_repeat_same"] = f"{sum(bool(x.get('off_repeat_same')) for x in rows)}/{sum('off_repeat_same' in x for x in rows)}"
    a["diag_agree_nonspecial"] = f"{sum(1 for x in rows if x.get('diag_agree') and not x.get('diag_special'))}/{sum(1 for x in rows if x.get('diag_agree') is not None and not x.get('diag_special'))}"
    return a

def main():
    items = []
    for p in PACKS:
        if not os.path.exists(f"{ARM}/runs/gs-{p}{SFX}.jsonl"): print(f"skip {p} (not ready)"); continue
        items += do_pack(p)
    out = {"criterion_sha256": SHA, "packs_done": sorted({x["pack"] for x in items}, key=PACKS.index),
           "per_pack": {p: agg([x for x in items if x["pack"] == p]) for p in PACKS if any(x["pack"] == p for x in items)},
           "family": {f: agg([x for x in items if x["family"] == f]) for f in ("SE", "topic")}, "all": agg(items),
           "loss_ids": {lvl: {x["id"]: x[f"{lvl}_loss"] for x in items if f"{lvl}_loss" in x} for lvl in ("chunk", "art")}, "items": items}
    if X:  # the 9 step-0 items: chunk lost to grounding, not recovered by top1
        s0 = json.load(open(f"{ARM}/aggregates/d0-gs.json"))["items"]
        nine = [x["id"] for x in s0 if x.get("chunk_loss") == "grounding" and not x["top1"]["chunk_kept"]]
        byid = {x["id"]: x for x in items}
        out["step0_nine"] = {i: bool(byid[i][X]["chunk_kept"]) for i in nine if i in byid}
    json.dump(out, open(f"{ARM}/aggregates/d0-gs{SFX}.json", "w"), indent=1)
    a = out["all"]; print(json.dumps({k: a[k] for k in a if not k.endswith("_keep_codes")}) + (" nine=" + json.dumps(out.get("step0_nine")) if X else ""))
main()
