"""HEADPASS-ST step 0 compare (0 LLM; criterion sha 8b910cad...). Cells: REF = tk2off tree (off); HP tree: off (pass 1), x1
(pass 2, settings.packHeadPass "a2"), off2 (pass 3). Fact chunks = oracle-st/tools/oracle-facts.json fact_chunks (as
h8st/tools/diag/arthead_cut7.py); only the item's pack chunks count (chunkId pack:(local-)?<pack>:<n>).
reach = fact chunk in raw ∪ appended; present = fact chunk in the final context (sources event = kept ∪ appended).
Identity = raw (chunkId, title, section, source, similarity, via), kept (chunkId, title, section), promptSha, task, query, k.
Cost = retrieval ms + keepMs (engine: first retrieve return -> sources event); prompt tokens = approxTokens(prompt).
Writes aggregates/compare.json + runs/split.jsonl. Public sets only. Run: python3 -I compare_hp.py"""
import json, re, statistics as stt, os, collections
ROOT = "<workspace>"; A = f"{ROOT}/rnd/research/coordinator/arms/headpass-st"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se",
         "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
SE = [p for p in PACKS if p.startswith("qa-")]; TOPIC = [p for p in PACKS if p not in SE]
FACTS = json.load(open(f"{ROOT}/rnd/research/coordinator/arms/oracle-st/tools/oracle-facts.json"))
load = lambda f: [json.loads(l) for l in open(f) if l.strip()]
CID = re.compile(r"^pack:(?:local-)?([^:]+):(\d+)$")
def own(ids, p): return {int(m.group(2)) for x in ids for m in [CID.match(x or "")] if m and m.group(1) == p}
num = lambda c: int(c.rsplit(":", 1)[1])
def cells(ref_f, hp_f):
    out = {"ref": {l["id"]: l for l in load(ref_f)}}; seen = {}
    for l in load(hp_f):
        n = seen.get(l["id"], 0); seen[l["id"]] = n + 1; out.setdefault(["off", "x1", "off2"][n], {})[l["id"]] = l
    assert all(l["mode"] == "x1" for l in out["x1"].values()) and all(l["mode"] == "off" for l in out["off"].values())
    return out
full = lambda l: json.dumps([[[x.get(k) for k in ("chunkId", "title", "section", "source", "similarity", "via")] for x in l["raw"]],
                             [[x.get("chunkId"), x.get("title"), x.get("section")] for x in l["kept"]], l.get("promptSha"), l["task"], l["query"], l["k"]])
p50 = lambda xs: (round(stt.median([x for x in xs if x is not None]), 1) if any(x is not None for x in xs) else None)
cost = lambda l: (l["ms"] or 0) + (l["keepMs"] or 0) if l["ms"] is not None or l["keepMs"] is not None else None
CN = ("ref", "off", "x1", "off2")
per = {}; split_rows = []
for p in PACKS:
    C = cells(f"{A}/runs/st-{p}.ref.jsonl", f"{A}/runs/st-{p}.hp.jsonl"); ids = list(C["ref"])
    o = {"n": len(ids)}
    for c in CN:
        s = collections.Counter(); costs, ptok, ktok = [], [], []
        for i in ids:
            l = C[c][i]; fcs = {num(x) for x in FACTS[i]["fact_chunks"]}
            raw = own([x.get("chunkId") for x in l["raw"]], p); kept = own([x.get("chunkId") for x in l["kept"]], p); app = own(l.get("appended") or [], p)
            s["raw_fact"] += bool(fcs & raw); s["reach"] += bool(fcs & (raw | app)); s["present"] += bool(fcs & kept)
            s["fire"] += bool(l.get("appended")); s["appended"] += len(l.get("appended") or []); s["app_fact"] += bool(fcs & app)
            s["empty_kept_retrieving"] += bool(l["raw"]) and not l["kept"]
            s["health_strict"] += "grounding:health-strict" in l["codes"]
            s["hp_health_dropped"] += sum(int(x.rsplit("-", 1)[1]) for x in l["codes"] if x.startswith("headpass:health-dropped-"))
            s["hp_health_fail"] += sum(1 for x in l.get("hpHealth") or [] if not x["ok"]); s["hp_health_checked"] += len(l.get("hpHealth") or [])
            s["no_user_pack"] += "headpass:no-user-pack" in l["codes"]
            costs.append(cost(l)); ptok.append(l.get("promptTokens")); ktok.append(l.get("keptTokens"))
        s = dict(s); s["cost_p50"] = p50(costs); s["ret_p50"] = p50([C[c][i]["ms"] for i in ids]); s["keep_p50"] = p50([C[c][i]["keepMs"] for i in ids])
        s["ptok_p50"] = p50(ptok); s["ktok_p50"] = p50(ktok); s["_costs"] = costs; s["_ptok"] = ptok; s["_ktok"] = ktok; o[c] = s
    o["ref_vs_off_identical"] = sum(full(C["ref"][i]) == full(C["off"][i]) for i in ids)
    o["off_vs_off2_identical"] = sum(full(C["off"][i]) == full(C["off2"][i]) for i in ids)
    o["x1_prompt_changed"] = sum(C["off"][i]["promptSha"] != C["x1"][i]["promptSha"] for i in ids)
    o["x1_lost_kept"] = sum(bool({x["chunkId"] for x in C["off"][i]["kept"]} - {x["chunkId"] for x in C["x1"][i]["kept"]}) for i in ids)
    sp = collections.Counter()
    for i in ids:
        fcs = {num(x) for x in FACTS[i]["fact_chunks"]}; a, b = C["off"][i], C["x1"][i]
        pa = bool(fcs & own([x["chunkId"] for x in a["kept"]], p)); pb = bool(fcs & own([x["chunkId"] for x in b["kept"]], p))
        app = own(b.get("appended") or [], p)
        if a["promptSha"] == b["promptSha"] and full(a) == full(b): k = "unchanged"
        elif pb and not pa: k = "newly_present"
        elif app and not (fcs & app): k = "nonfact_only"
        else: k = "other_changed"
        sp[k] += 1; sp[f"{k}|fact_already_present"] += pa
        split_rows.append({"pack": p, "id": i, "split": k, "off_present": pa, "x1_present": pb, "appended": b.get("appended") or [], "n_kept_off": len(a["kept"])})
    o["split"] = dict(sp); per[p] = o
def tot(ps):
    t = {"n": sum(per[p]["n"] for p in ps)}
    for c in CN:
        keys = {k for p in ps for k in per[p][c] if not k.startswith("_") and not k.endswith("_p50")}
        t[c] = {k: sum(per[p][c].get(k, 0) for p in ps) for k in sorted(keys)}
        for nm, src in (("cost_p50", "_costs"), ("ptok_p50", "_ptok"), ("ktok_p50", "_ktok")): t[c][nm] = p50(sum((per[p][c][src] for p in ps), []))
        t[c]["ret_p50"] = None
    for k in ("ref_vs_off_identical", "off_vs_off2_identical", "x1_prompt_changed", "x1_lost_kept"): t[k] = sum(per[p][k] for p in ps)
    sp = collections.Counter()
    for p in ps: sp.update(per[p]["split"])
    t["split"] = dict(sp); return t
res = {"st180": {"total": tot(PACKS), "SE": tot(SE), "topic": tot(TOPIC), "per_pack": per}}
for p in PACKS:
    for c in CN:
        for k in ("_costs", "_ptok", "_ktok"): per[p][c].pop(k)
# v0.1 sets
_LIB = re.compile(r"^[^:]{2,40}:\s+"); norm = lambda s: " ".join(str(s or "").split()).lower(); bare = lambda t: _LIB.sub("", str(t or ""))
def gmatch(gold, ref):
    title, _, section = gold.partition("#")
    if norm(title) != norm(ref.get("title")) and (_LIB.match(title) or norm(title) != norm(bare(ref.get("title")))): return False
    return not section or norm(section) == norm(ref.get("section"))
G = {k: v for k, v in json.load(open(f"{ROOT}/boar-eval/bench/v0.1/gold/sources.json")).items() if isinstance(v, list) and v}
for st in ("v01-kit", "v01-sw"):
    C = cells(f"{A}/runs/{st}.ref.jsonl", f"{A}/runs/{st}.hp.jsonl"); ids = list(C["ref"]); o = {"n": len(ids)}
    for c in CN:
        L = C[c]
        o[c] = {"gold_raw6": sum(any(gmatch(g, x) for g in G[i] for x in L[i]["raw"][:6]) for i in G if i in L),
                "gold_kept": sum(any(gmatch(g, x) for g in G[i] for x in L[i]["kept"]) for i in G if i in L),
                "retrieving": sum(bool(l["raw"]) for l in L.values()), "fire": sum(bool(l.get("appended")) for l in L.values()),
                "appended": sum(len(l.get("appended") or []) for l in L.values()), "kept_slots": sum(len(l["kept"]) for l in L.values()),
                "health_fail": sum(1 for l in L.values() for x in l.get("hpHealth") or [] if not x["ok"]),
                "cost_p50": p50([cost(l) for l in L.values()]), "ptok_p50": p50([l.get("promptTokens") for l in L.values()]),
                "ktok_p50": p50([l.get("keptTokens") for l in L.values()])}
    o["ref_vs_off_identical"] = sum(full(C["ref"][i]) == full(C["off"][i]) for i in ids)
    o["off_vs_off2_identical"] = sum(full(C["off"][i]) == full(C["off2"][i]) for i in ids)
    o["x1_vs_off_identical"] = sum(full(C["x1"][i]) == full(C["off"][i]) for i in ids)
    o["lost_context"] = [i for i in ids if {x["chunkId"] for x in C["off"][i]["kept"]} - {x["chunkId"] for x in C["x1"][i]["kept"]}]
    fired = [i for i in ids if C["x1"][i].get("appended")]
    o["fired_ids"] = fired
    o["added_ktok_fired_p50"] = p50([(C["x1"][i]["keptTokens"] or 0) - (C["off"][i]["keptTokens"] or 0) for i in fired])
    o["added_ptok_fired_p50"] = p50([(C["x1"][i]["promptTokens"] or 0) - (C["off"][i]["promptTokens"] or 0) for i in fired if C["x1"][i]["promptTokens"] and C["off"][i]["promptTokens"]])
    o["gold_kept_changed"] = [i for i in G if i in C["off"] and any(gmatch(g, x) for g in G[i] for x in C["off"][i]["kept"]) != any(gmatch(g, x) for g in G[i] for x in C["x1"][i]["kept"])]
    o["empty_to_nonempty"] = [i for i in ids if C["off"][i]["raw"] and not C["off"][i]["kept"] and C["x1"][i]["kept"]]
    res[st] = o
json.dump(res, open(f"{A}/aggregates/compare.json", "w"), indent=1)
with open(f"{A}/runs/split.jsonl", "w") as f:
    for d in split_rows: f.write(json.dumps(d) + "\n")
K = ("raw_fact", "reach", "present", "fire", "appended", "app_fact", "empty_kept_retrieving", "health_strict", "hp_health_dropped", "hp_health_checked", "hp_health_fail", "cost_p50", "keep_p50", "ptok_p50", "ktok_p50")
for k in ("total", "SE", "topic"):
    t = res["st180"][k]; print(f"== {k} n={t['n']} ref=off {t['ref_vs_off_identical']} off=off2 {t['off_vs_off2_identical']} promptChanged {t['x1_prompt_changed']} lostKept {t['x1_lost_kept']} split {t['split']}")
    for c in CN: print("  ", c, {kk: t[c].get(kk) for kk in K})
for p in PACKS:
    r = per[p]; print(p, "ref=off", r["ref_vs_off_identical"], "off=off2", r["off_vs_off2_identical"], {c: {kk: r[c].get(kk) for kk in ("reach", "present", "fire", "appended", "app_fact", "cost_p50", "ptok_p50")} for c in ("off", "x1")}, r["split"])
for st in ("v01-kit", "v01-sw"):
    o = res[st]; print(st, json.dumps({k: v for k, v in o.items()}))
