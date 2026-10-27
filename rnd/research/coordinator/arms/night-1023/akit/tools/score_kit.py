"""KIT-V01 scoring (0 LLM). python3 -I tools/score_kit.py -> ../a-kit.json
Reuses coverage-map/tools/chunklevel.py machinery (exec of its header up to ARMS): chunk-level delivery per replay; losses vs SEFIX-124 (sefix F1F2F4); junk; kept tokens. Rule per NIGHT-criterion (sha 36635ca23543a44e)."""
import json, sys, os, math, statistics
CL = "<workspace>/rnd/research/coordinator/arms/coverage-map/tools/chunklevel.py"
D = "<workspace>/rnd/research/coordinator/arms/night-1023/akit"
src = open(CL).read(); head = src.split("ARMS = {")[0]
sys.argv = [CL, "/dev/null"]
exec(head)   # ids92, V01, CMI, score(), rd
CM_ = "<workspace>/rnd/research/coordinator/arms/coverage-map/"
ARMS = {"SEFIX-124 (K13 control)": CM_ + "sefix/replays/main.F1F2F4.jsonl"}
for lab, f in (("K13+SE2", "KSE"), ("K13+SE2+NIST", "KSEN"), ("K13+SE2+NIST+EIPs", "KSENE")):
    p = f"{D}/replays/main.{f}.jsonl"
    if os.path.exists(p) and sum(1 for _ in open(p)) >= 97: ARMS[lab] = p
tok = lambda c: math.ceil(len(f"{c['title']}\n{c['body']}") / 4)
RES = {l: score(f) for l, f in ARMS.items()}; ROWS = {l: {r["id"]: r for r in rd(f)} for l, f in ARMS.items()}
ctl = "SEFIX-124 (K13 control)"
def junk(lab, level, itemset):
    ids = [i for i in ids92 if itemset(i, lab) and RES[lab][i] is not None]
    return (statistics.mean(len(ROWS[lab][i]["keptFull"]) for i in ids), len(ids)) if ids else (None, 0)
out = {"criterion_sha": "36635ca23543a44e", "arms": {}, "rule": "ADOPTED iff v0.1 chunk-level >= 31 AND losses <= 1 AND junk <= 1.15x SEFIX-124"}
dctl = {i for i in ids92 if RES[ctl][i]["chunk"]}
for lab in ARMS:
    s = RES[lab]; rows = ROWS[lab]; d = {i for i in ids92 if s[i]["chunk"]}
    own_nofact = lambda i, l=lab: not RES[l][i]["chunk"]
    both_nofact = lambda i, l=lab: not RES[l][i]["chunk"] and not RES[ctl][i]["chunk"]
    ctl_nofact = lambda i, l=lab: not RES[ctl][i]["chunk"]
    jo = junk(lab, "chunk", own_nofact); jb = junk(lab, "chunk", both_nofact); jc = junk(lab, "chunk", ctl_nofact)
    e = dict(n_packs_extra=lab, chunk92=len(d), v01=sum(1 for i in V01 if s[i]["chunk"]), cm40=sum(1 for i in CMI if s[i]["chunk"]),
             art92=sum(1 for i in ids92 if s[i]["art"]), art_v01=sum(1 for i in V01 if s[i]["art"]),
             gained=sorted(d - dctl), lost=sorted(dctl - d), losses=len(dctl - d), losses_v01=len([i for i in dctl - d if i in V01]),
             gained_v01=[i for i in sorted(d - dctl) if i in V01], gained_cm=[i for i in sorted(d - dctl) if i in CMI],
             junk_own=jo[0], junk_own_n=jo[1], junk_both=jb[0], junk_both_n=jb[1], junk_ctlset=jc[0], junk_ctlset_n=jc[1],
             mean_kept=statistics.mean(len(rows[i]["keptFull"]) for i in ids92),
             kept_tokens=statistics.mean(sum(tok(c) for c in rows[i]["keptFull"]) for i in rows),
             lists_changed=sum(1 for i in ids92 if [c["chunkId"] for c in rows[i]["keptFull"]] != [c["chunkId"] for c in ROWS[ctl][i]["keptFull"]]),
             wall_ms=statistics.mean(r["wallMs"] for r in rows.values() if r.get("wallMs") is not None))
    out["arms"][lab] = e
c = out["arms"][ctl]
for lab, e in out["arms"].items():
    if lab == ctl: continue
    e["junk_ratio_own"] = e["junk_own"] / c["junk_own"]; e["junk_ratio_both"] = e["junk_both"] / c["junk_both"]; e["junk_ratio_ctlset"] = e["junk_ctlset"] / c["junk_ctlset"]
    e["tok_ratio"] = e["kept_tokens"] / c["kept_tokens"]
    e["adopt_v01"] = e["v01"] >= 31; e["adopt_losses"] = e["losses"] <= 1; e["adopt_junk"] = e["junk_ratio_own"] <= 1.15
    e["ADOPTED"] = e["adopt_v01"] and e["adopt_losses"] and e["adopt_junk"]
out["adopted"] = next((l for l, e in out["arms"].items() if e.get("ADOPTED")), None)
json.dump(out, open(os.path.dirname(D) + "/a-kit.json", "w"), indent=1)
for lab, e in out["arms"].items(): print(lab, {k: v for k, v in e.items() if k not in ("n_packs_extra",)})
