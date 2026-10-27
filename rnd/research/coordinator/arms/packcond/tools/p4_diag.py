#!/usr/bin/env python3
"""PACKCOND P4 step 0: where is the fact-holding pack article lost on the v0.2 in-pack items (F0 true, P1 aggregates)?
Classes per item (F0 article = any of the P1 hit_articles of an F0 pack, matched on trace titles as packcond_p1.trace_pack_titles):
  d kept            : the article is in retrieval.kept
  a not-in-raw      : not in retrieval.raw (retrieval miss); records the raw titles' packs and the article's rank in a
                      k=20 pool (replay --pool 20; H only) = the k it would need
  b grounding-drop  : in raw, survives compressContext, dropped by onSubject/onTopic (or the health topic filter: b-health)
  c compress-drop   : in raw, cut by compressContext (relative floor / budget) or the substantive filter (c-substantive)
  b|c               : K only when the codes cannot separate them (no replay of the cut3 tree)
H: b vs c from the replay-side reconstruction (replay-pg.ts --diag on the dt512 tree, raw identical 32/32), else codes.
K: codes only: no off-topic code -> c; raw-kept == off-topic-dropped-N (+ no-content-dropped) -> b; else b|c.
Writes ONLY ids, titles, pack names, codes, counts. usage: p4_diag.py [--replay-h blind/.../pg-off-H32.jsonl]
"""
import sys, json, re, collections, argparse
sys.path.insert(0, "<workspace>/rnd/research/coordinator/arms/packcond/tools")
ROOT = "<workspace>"; COORD = f"{ROOT}/rnd/research/coordinator"; AGG = f"{COORD}/arms/packcond/aggregates"
LIBS_CRYPTO = ("Ethereum EIPs/ERCs", "ethereum.org", "Bitcoin BIPs", "Ethereum specs")
LIBS_OTHER = ("Wikibooks", "Appropedia", "US government", "Wikipedia")

def pack_of(title):
    """-> (pack, bare lower title) of a trace title; plain titles = 'plain' (essential corpus or crypto Wikipedia articles)."""
    t = title or ""
    if t.startswith("Wikivoyage: "): return "wikivoyage", t[12:].lower()
    for p in LIBS_CRYPTO:
        if t.startswith(p + ": "): return "crypto", t[len(p) + 2:].lower()
    for p in LIBS_OTHER:
        if t.startswith(p + ": "): return p.lower(), t[len(p) + 2:].lower()
    return "plain", t.lower()

def is_f0(ref, f0):
    """ref = {title,...}; f0 = {pack: set(lower article titles)}. Plain titles count for crypto (P1 rule)."""
    pk, bare = pack_of(ref.get("title"))
    if pk == "plain": pk = "crypto"
    return bare in f0.get(pk, set())

def norm_code(c): return re.sub(r"\d+(\.\d+)?", "N", c)

def first_pos(lst, f0):
    for i, r in enumerate(lst or []):
        if is_f0(r, f0): return i
    return None

def classify(arm, it, tr, rp):
    f0 = {p: {a.lower() for a in v["hit_articles"]} for p, v in it["packs"].items() if v["f0"]}
    raw, kept = tr["retrieval"]["raw"] or [], tr["retrieval"]["kept"] or []
    codes = tr["route"]["reasonCodes"]
    rec = {"id": it["id"], "p1_bucket": it["bucket"], "f0_packs": sorted(f0), "f0_articles": sorted(set().union(*f0.values())),
           "raw_n": len(raw), "kept_n": len(kept), "raw_packs": [pack_of(r["title"])[0] for r in raw],
           "raw_pos": first_pos(raw, f0), "kept_pos": first_pos(kept, f0), "codes": codes, "tier": tr["route"]["tier"]}
    if rp is not None:
        rec["pool_pos"] = first_pos(rp.get("pool"), f0)
        rec["replay_raw_same"] = rp.get("ref", {}).get("same")
    if rec["kept_pos"] is not None: cls = "d"
    elif rec["raw_pos"] is None: cls = "a"
    else:
        health = "grounding:health-strict" in codes
        d = (rp or {}).get("diag")
        if d and d.get("agree") and not d.get("special"):
            if first_pos(d["sub"], f0) is None: cls = "c-substantive"
            elif first_pos(d["comp"], f0) is None: cls = "c"
            elif first_pos(d["ground"], f0) is None: cls = "b"
            else: cls = "?"
            rec["diag_agree"] = True
        else:
            if d is not None: rec["diag_agree"] = bool(d.get("agree")); rec["diag_special"] = bool(d.get("special"))
            off = sum(int(c.rsplit("-", 1)[1]) for c in codes if re.match(r"grounding:(health-)?off-topic-dropped-\d+$", c))
            noc = sum(int(c.rsplit("-", 1)[1]) for c in codes if re.match(r"context:no-content-dropped-\d+$", c))
            restored = 1 if "grounding:health-best-restored" in codes else 0
            if off == 0: cls = "c"
            elif len(raw) - noc - len(kept) + restored == off: cls = "b"
            else: cls = "b|c"
            if health and cls.startswith("b"): cls = "b-health"
        if health and cls == "b": cls = "b-health"
    rec["class"] = cls
    return rec

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--replay-h", default=f"{ROOT}/blind/bench-v02/runs-packcond/pg-off-H32.jsonl")
    ap.add_argument("--out", default=f"{AGG}/p4-diag.json"); a = ap.parse_args()
    out = {}
    for arm in "HK":
        agg = json.load(open(f"{AGG}/packcond-{arm}-v02.json"))
        trs = {}
        for l in open(f"{agg['traces_dir']}/{agg['traces']}"):
            t = json.loads(l); trs[t["itemId"]] = t
        rps = {}
        if arm == "H":
            for l in open(a.replay_h):
                r = json.loads(l); rps[r["id"]] = r
        recs = [classify(arm, it, trs[it["id"]], rps.get(it["id"]) if arm == "H" else None) for it in agg["items"] if it["F0"]]
        by = collections.defaultdict(list)
        for r in recs: by[r["class"]].append(r["id"])
        hist = {c: dict(collections.Counter(norm_code(x) for r in recs if r["class"] == c for x in r["codes"]
                                           if x.startswith(("grounding:", "context:", "retrieve:", "match:")) ).most_common())
                for c in by}
        out[arm] = {"n": len(recs), "counts": {c: len(v) for c, v in sorted(by.items())}, "ids": dict(sorted(by.items())),
                    "codes_by_class": hist, "items": recs}
        print(arm, out[arm]["counts"])
    json.dump(out, open(a.out, "w"), indent=1)
    print("wrote", a.out)

if __name__ == "__main__": main()
