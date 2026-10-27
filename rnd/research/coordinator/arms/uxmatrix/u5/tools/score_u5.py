"""U5 FOLLOWUP-PACKS scorer (0 LLM; criterion U5-criterion.md a87f8877). python3 -I tools/score_u5.py -> ../u5.json (+ prints markdown table)."""
import json, re, os, glob, statistics, collections
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = "<workspace>/rnd/research/coordinator/arms"; B = "<workspace>"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s.lower())).strip()
items = {d["id"]: d for d in rd(A + "/qform/items/qform.jsonl")}
qs = {d["id"]: d for d in rd(B + "/boar-eval/bench/slices/longsession-v1/questions.jsonl")}
pk = lambda c: c["chunkId"].split(":")[1].removeprefix("local-") if c["chunkId"].startswith("pack:") else "kb"
def load(*names):
    out = {}
    for n in names:
        for f in sorted(glob.glob(f"{D}/replays/{n}.jsonl")):
            for r in rd(f): out.setdefault(r["id"] + "|" + os.path.basename(f), r)
    return out
def by_id(name):
    f = f"{D}/replays/{name}.jsonl"; return {r["id"]: r for r in rd(f)} if os.path.exists(f) else None
# ---- F8
def fhit(lst, i): q = norm(items[i]["gold"]["quote"]); return any(q in norm(c["title"] + " " + c["body"]) for c in lst)
def fon(c, i): g = items[i]; return c.get("docId") == f"pack:local-{g['pack']}:a{g['gold']['article_id']}"
def f8_rows(R, RC):
    F8 = sorted(i for i in R if i.endswith("-F8"))
    rows = {}
    for i in F8:
        k1 = fhit(R[i[:-1] + "0"]["keptFull"], i); k2 = fhit(R[i]["keptFull"], i); kc = fhit(RC[i]["keptFull"], i) if RC and i in RC else None
        kept = R[i]["keptFull"]; ckept = RC[i]["keptFull"] if RC and i in RC else []
        rows[i] = dict(k1=k1, k2=k2, kc=kc, n=len(kept), off=sum(not fon(c, i) for c in kept), nc=len(ckept), offc=sum(not fon(c, i) for c in ckept),
                       t1_packs=[pk(c) for c in R[i[:-1] + "0"]["keptFull"]], t2_packs=[pk(c) for c in kept])
    return rows
# ---- LS
def refs(i): return [x.lower() for x in qs[i].get("referent", [])]
def lhit(lst, i): r = refs(i); t = " ".join((c["title"] + " " + c["body"]).lower() for c in lst); return bool(r) and any(x in t for x in r)
def lon(c, i): t = (c["title"] + " " + c["body"]).lower(); return any(x in t for x in refs(i))
FU = sorted(i for i in qs if qs[i]["followup"] and 2 <= int(i.split("-t")[1]) <= 5)
SC = sorted(i for i in qs if not qs[i]["followup"] and 2 <= int(i.split("-t")[1]) <= 5)
def ls_rows(R, RC):
    rows = {}
    for i in FU:
        if i not in R: continue
        p = R[i]["prevId"]; k1 = lhit(R[p]["keptFull"], i); k2 = lhit(R[i]["keptFull"], i); kc = lhit(RC[i]["keptFull"], i) if RC and i in RC else None
        kept = R[i]["keptFull"]; ckept = RC[i]["keptFull"] if RC and i in RC else []
        rows[i] = dict(k1=k1, k2=k2, kc=kc, n=len(kept), off=sum(not lon(c, i) for c in kept), nc=len(ckept), offc=sum(not lon(c, i) for c in ckept),
                       t1_ref_packs=[pk(c) for c in R[p]["keptFull"] if lon(c, i)], t2_packs=[pk(c) for c in kept])
    return rows
def agg(rows, sub=None, R=None, RC=None):
    ids = [i for i in rows if sub is None or i in sub]; g = lambda k: [i for i in ids if rows[i][k]]
    K1 = g("k1"); S = [i for i in K1 if rows[i]["k2"]]; LOST = [i for i in K1 if not rows[i]["k2"]]
    Rr = [i for i in LOST if rows[i]["kc"]]; G = [i for i in ids if rows[i]["k2"] and not rows[i]["k1"]]
    n = sum(rows[i]["n"] for i in ids); off = sum(rows[i]["off"] for i in ids); nc = sum(rows[i]["nc"] for i in ids); offc = sum(rows[i]["offc"] for i in ids)
    o = dict(n=len(ids), K1=len(K1), K2=len(g("k2")), S=len(S), survival=(len(S) / len(K1) if K1 else None), LOST=len(LOST), R=len(Rr), G=len(G),
             carry_K2=sum(1 for i in ids if rows[i]["kc"]), junk=(off / n if n else None), junk_carry=(offc / nc if nc else None),
             carry_mult=(offc / off if off else None), mean_kept=n / len(ids) if ids else None, mean_kept_carry=nc / len(ids) if ids else None,
             lost_ids=LOST, recovered_ids=Rr, gained_ids=G)
    return o
res = {"criterion_sha256": open(D + "/../U5-criterion.sha256").read().split()[0], "f8": {}, "ls": {}, "ls16": {}}
# his 16 (UXT-24 vital6 primary): previous-turn referent kept in his engine
his = {r["id"]: r for r in rd(A + "/ux-tests-1023/work/out/t4-longsession-vital6.jsonl")} if os.path.exists(A + "/ux-tests-1023/work/out/t4-longsession-vital6.jsonl") else {}
H16 = {i for i in FU if i in his and lhit(his[his[i]["prevId"]]["keptFull"], i)}
res["his16_ids"] = sorted(H16)
for arm in ("base", "on", "off"):
    if arm == "off":
        R = {}; RC = {}
        for f in sorted(glob.glob(f"{D}/replays/qform.off.*.jsonl")):
            if ".c2." in f: continue
            p = os.path.basename(f)[len("qform.off."):-len(".jsonl")]
            for r in rd(f):
                if items[r["id"]]["pack"] == p: R[r["id"]] = r
            fc = f[:-len(".jsonl")] + ".c2.jsonl"
            if os.path.exists(fc):
                for r in rd(fc):
                    if items[r["id"]]["pack"] == p: RC[r["id"]] = r
        LR = {}; LRC = {}
        plan = json.load(open(D + "/ls_off_plan.json")) if os.path.exists(D + "/ls_off_plan.json") else {}
        for pid, pack in plan.get("pairs", {}).items():
            tag = pack or "fullkit"; a = by_id(f"longsession.off.{tag}"); c = by_id(f"longsession.off.{tag}.c2")
            if a: LR[pid] = a[pid]; LR[a[pid]["prevId"]] = a[a[pid]["prevId"]]
            if c: LRC[pid] = c[pid]
        ls_R, ls_RC = LR, LRC
    else:
        R = by_id(f"qform.{arm}"); RC = by_id(f"qform.{arm}.c2"); ls_R = by_id(f"longsession.{arm}"); ls_RC = by_id(f"longsession.{arm}.c2")
    if R and len([i for i in R if i.endswith("-F8")]) == 48:
        rows = f8_rows(R, RC); res["f8"][arm] = agg(rows); res["f8"][arm]["rows"] = rows
        res["f8"][arm]["per_pack"] = {p: agg(rows, {i for i in rows if items[i]["pack"] == p}) for p in sorted({items[i]["pack"] for i in rows})}
        for v in res["f8"][arm]["per_pack"].values(): [v.pop(k) for k in ("lost_ids", "recovered_ids", "gained_ids")]
    if ls_R and all(i in ls_R for i in FU):
        rows = ls_rows(ls_R, ls_RC); res["ls"][arm] = agg(rows); res["ls"][arm]["rows"] = rows; res["ls16"][arm] = agg(rows, H16)
        if arm != "off":
            sc = [len(ls_R[i]["keptFull"]) for i in SC]; scc = [len(ls_RC[i]["keptFull"]) for i in SC] if ls_RC else None
            res["ls"][arm]["selfcontained_mean_kept"] = statistics.mean(sc); res["ls"][arm]["selfcontained_mean_kept_carry"] = statistics.mean(scc) if scc else None
            res["ls"][arm]["selfcontained_mult"] = (statistics.mean(scc) / statistics.mean(sc)) if scc else None
# identity rs-U5 vs rs-SEFIX (LS ON, no carry)
a, b = by_id("longsession.on"), by_id("longsession.on.sefix")
if a and b:
    same = [i for i in a if i in b and [c["chunkId"] for c in a[i]["keptFull"]] == [c["chunkId"] for c in b[i]["keptFull"]] and a[i]["reasonCodes"] == b[i]["reasonCodes"]]
    res["identity"] = dict(n=len(a), same=len(same), diff=sorted(set(a) - set(same)))
json.dump(res, open(D + "/../u5.json", "w"), indent=1, default=list)
f = lambda x: "-" if x is None else (f"{x:.2f}" if isinstance(x, float) else str(x))
print("| set | arm | n | K1 turn 1 | K2 turn 2 | survived S/K1 | lost | R (carry recovers) | G (turn 2 only) | junk t2 | junk t2 carry | carry off-subject mult | carry K2 |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for s in ("f8", "ls", "ls16"):
    for arm, v in res[s].items():
        print(f"| {s} | {arm} | {v['n']} | {v['K1']} | {v['K2']} | {v['S']}/{v['K1']} = {f(v['survival'])} | {v['LOST']} | {v['R']} | {v['G']} | {f(v['junk'])} | {f(v['junk_carry'])} | {f(v['carry_mult'])} | {v['carry_K2']} |")
print("identity", res.get("identity")); print("ls selfcontained", {a: (f(v.get('selfcontained_mean_kept')), f(v.get('selfcontained_mean_kept_carry')), f(v.get('selfcontained_mult'))) for a, v in res["ls"].items()})
for s in ("f8", "ls"):
    for arm, v in res[s].items(): print(s, arm, "lost", v["lost_ids"], "rec", v["recovered_ids"], "gained", v["gained_ids"])
