"""G2-FULLKIT scoring (0 LLM). python3 -I score_g2.py -> reads.json, reads.md. Reuses tools/sweep.py's QFORM loader (exec of its helper block) and step0/score.py's rule."""
import json, os, statistics, subprocess, sys
R = "<workspace>/rnd/research/coordinator/arms/retrieve-sweep"; H = R + "/g2-fullkit"
src = open(R + "/tools/sweep.py").read().split("\n")
i0 = next(i for i, l in enumerate(src) if l.startswith("import glob")); i1 = next(i for i, l in enumerate(src) if l.startswith("# ----") and "arm files" in l)
j0 = next(i for i, l in enumerate(src) if l.startswith("# ----") and "QFORM" in l); j1 = next(i for i, l in enumerate(src) if l.startswith("Q = {a: load_q"))
exec("\n".join(src[i0:i1]) + "\n" + "\n".join(src[j0:j1]))
PK = ["boar-factbook", "boar-firstaid-en", "boar-medlineplus-en", "boar-crypto", "boar-wikivoyage-en", "boar-visa-en"]
FN = {0: "F0 base", 1: "F1 entity-free", 2: "F2 keywords", 3: "F3 situational", 4: "F4 typos", 5: "F5 yes/no true", 6: "F6 false premise", 7: "F7 comparison", 8: "F8 follow-up"}
files = {"v2off": H + "/runs/qform.v2-off.jsonl", "v2k1": H + "/runs/qform.v2-k1.jsonl", "v3extra": H + "/runs/qform.v3-extra.jsonl"}
Qs = {a: load_q(f) for a, f in files.items() if os.path.exists(f)}
ctl = Qs["v2off"]; junk = [i for i in IDS if not ctl[i]["wide"]]
res = {"n": len(IDS), "junk_set_n": len(junk), "arms": {}}
pack_of = {i: items[i]["pack"] for i in IDS}
def d_ci(a, b, ids):
    va = {i: int(Qs[a][i]["kept"]) for i in ids}; vb = {i: int(Qs[b][i]["kept"]) for i in ids}
    d, lo, hi = boot(va, vb, [[i] for i in ids])
    fu = {}
    for i in ids: fu.setdefault(items[i]["fact_id"], []).append(i)
    dc, loc, hic = boot(va, vb, list(fu.values()))
    return dict(d=d * 100, ci=[lo * 100, hi * 100], ci_fact=[loc * 100, hic * 100], gained=sum(va[i] > vb[i] for i in ids), lost=sum(va[i] < vb[i] for i in ids))
for a, q in Qs.items():
    walls = [q[i]["wall"] for i in IDS if q[i]["wall"] is not None]; ctxs = [q[i]["ctx"] for i in IDS if q[i]["ctx"] is not None]
    e = dict(hit_kept_n=sum(q[i]["kept"] for i in IDS), hit_raw_n=sum(q[i]["raw"] for i in IDS), hit_wide_n=sum(q[i]["wide"] for i in IDS),
             by_form={f: sum(q[i]["kept"] for i in IDS if items[i]["form"] == f) for f in FORMS},
             by_pack={p: sum(q[i]["kept"] for i in IDS if pack_of[i] == p) for p in PK},
             junk_kept=statistics.mean(q[i]["nk"] for i in junk), mean_kept=statistics.mean(q[i]["nk"] for i in IDS),
             ctx_tokens=statistics.mean(ctxs), kept_tokens=statistics.mean(q[i]["ktok"] for i in IDS),
             wall_ms_mean=statistics.mean(walls), wall_ms_p50=statistics.median(walls), retrieve_ms_mean=statistics.mean(q[i]["ms"] for i in IDS if q[i]["ms"] is not None),
             kept_ids_changed_vs_v2off=sum(q[i]["ids"] != ctl[i]["ids"] for i in IDS))
    res["arms"][a] = e
res["delta"] = {}
for a, b in (("v3extra", "v2off"), ("v3extra", "v2k1"), ("v2k1", "v2off")):
    if a in Qs and b in Qs:
        r = {"pooled": d_ci(a, b, IDS), "by_form": {f: d_ci(a, b, [i for i in IDS if items[i]["form"] == f]) for f in FORMS},
             "by_pack": {p: d_ci(a, b, [i for i in IDS if pack_of[i] == p]) for p in PK}}
        res["delta"][f"{a}-{b}"] = r
# MAIN 97
def main_score(fn, label):
    o = subprocess.run(["python3", "-I", R + "/g-chunkvecs/step0/score.py", fn, label], capture_output=True, text=True); return json.loads(o.stdout)
res["main"] = {}
for k in ("v2", "v3"):
    fn = H + f"/runs/main.{k}.jsonl"
    if os.path.exists(fn):
        s = main_score(fn, k); rr = rd(fn); w = [r["wallMs"] for r in rr if r.get("wallMs") is not None]
        s["wall_ms_mean"] = statistics.mean(w); s["wall_ms_p50"] = statistics.median(w); s["retrieve_ms_mean"] = statistics.mean(r["ms"] for r in rr if r.get("ms") is not None)
        ctxs = [ctx_after(r["reasonCodes"]) for r in rr]; ctxs = [c for c in ctxs if c is not None]; s["ctx_tokens"] = statistics.mean(ctxs) if ctxs else None
        s["kept_tokens"] = statistics.mean(sum(tok(c) for c in r["keptFull"]) for r in rr)
        res["main"][k] = s
# bytes
V3 = "<workspace>/shared-data/packs/v3proto"; S = "<workspace>/shared-data"
v2p = {"boar-factbook": S + "/packs/wave2", "boar-firstaid-en": S + "/packs/wave1", "boar-medlineplus-en": S + "/packs/wave1", "boar-crypto": S + "/crypto", "boar-wikivoyage-en": S + "/packs", "boar-visa-en": S + "/packs/wave4", "boar-simplewiki-en": S + "/packs/wave2"}
res["bytes"] = {p: dict(v2=os.path.getsize(f"{d}/{p}.sqlite"), v3=os.path.getsize(f"{V3}/{p}.sqlite")) for p, d in v2p.items()}
json.dump(res, open(H + "/reads.json", "w"), indent=1)
# ---------------- markdown
L = ["# G2-FULLKIT reads (0 LLM; criterion sha dcac6f4b)\n"]
m = res["main"]
L += ["## Read 1: MAIN 97, K1 tree, settings {packHeadPass a2, packDense2 extra}\n", "| kit | recovery /25 | losses /22 | kept lists changed | mean kept | ctx tok | wall ms/q (mean) |", "|---|---|---|---|---|---|---|"]
for k, lab in (("v2", "v2 kit (crypto, wikivoyage, simplewiki wave2; no chunk_vecs)"), ("v3", "v3 kit (crypto, wikivoyage, simplewiki v3proto)")):
    if k in m: s = m[k]; L.append(f"| {lab} | {s['recovery']} {s['recovery_ids']} | {s['losses']} {s['loss_ids']} | {s['kept_changed']} | {s['mean_kept_arm']:.2f} | {s['ctx_tokens']:.0f} | {s['wall_ms_mean']:.0f} |")
if "v3" in m:
    s = m["v3"]; ok = s["recovery"] >= 5 and s["losses"] <= 2
    L.append(f"\nFrozen rule (recovery >= 5/25 and losses <= 2/22): **{'PASS' if ok else 'FAIL'}** (recovery {s['recovery']}, losses {s['losses']}). Reference: simplewiki v3 alone 4/0.\n")
L += ["## Read 2: QFORM 432, six separate A-union packs (hit@kept)\n", "| arm | hit@kept | hit@raw | hit@wide12 | junk-kept (x v2off) | mean kept | ctx tok | kept tok | kept lists changed vs v2off |", "|---|---|---|---|---|---|---|---|---|"]
a0 = res["arms"]["v2off"]
for a, lab in (("v2off", "v2 six, settings off"), ("v2k1", "v2 six, K1 settings (a2 + append-budget)"), ("v3extra", "v3 six, a2 + extra")):
    if a in res["arms"]:
        e = res["arms"][a]; L.append(f"| {lab} | {e['hit_kept_n']} ({100*e['hit_kept_n']/432:.1f} %) | {e['hit_raw_n']} | {e['hit_wide_n']} | {e['junk_kept']:.2f} ({e['junk_kept']/a0['junk_kept']:.2f}) | {e['mean_kept']:.2f} | {e['ctx_tokens']:.0f} | {e['kept_tokens']:.0f} | {e['kept_ids_changed_vs_v2off']} |")
L.append(f"\nJunk set = {res['junk_set_n']} items whose gold is not in the v2off wide-12.\n")
for k, r in res["delta"].items():
    p = r["pooled"]
    L.append(f"**{k} pooled: {p['d']:+.1f} pts [item CI {p['ci'][0]:+.1f}, {p['ci'][1]:+.1f}] [fact-cluster CI {p['ci_fact'][0]:+.1f}, {p['ci_fact'][1]:+.1f}], gained/lost {p['gained']}/{p['lost']}**\n")
    L.append("| form | " + " | ".join(FN[f] for f in FORMS) + " |"); L.append("|---|" + "---|" * len(FORMS))
    if "v2off" in k.split("-")[-1]:
        pass
    b = k.split("-")[-1]; a = k.split("-")[0]
    L.append(f"| {b} -> {a} (of 48) | " + " | ".join(f"{res['arms'][b]['by_form'][f]}->{res['arms'][a]['by_form'][f]} ({r['by_form'][f]['d']:+.0f})" for f in FORMS) + " |")
    L.append("\n| pack (of 72) | " + " | ".join(p.replace("boar-", "") for p in PK) + " |"); L.append("|---|" + "---|" * len(PK))
    L.append(f"| {b} -> {a} | " + " | ".join(f"{res['arms'][b]['by_pack'][p]}->{res['arms'][a]['by_pack'][p]} ({r['by_pack'][p]['d']:+.1f})" for p in PK) + " |\n")
L += ["## Read 3: costs\n", "| pack | v2 bytes | v3 bytes | delta |", "|---|---|---|---|"]
for p, b in res["bytes"].items(): L.append(f"| {p} | {b['v2']:,} | {b['v3']:,} | {100*(b['v3']/b['v2']-1):+.1f} % |")
tv2 = sum(b["v2"] for p, b in res["bytes"].items()); tv3 = sum(b["v3"] for p, b in res["bytes"].items()); L.append(f"| all 7 | {tv2:,} | {tv3:,} | {100*(tv3/tv2-1):+.1f} % |")
L.append("\nWall per query (replay answer() up to the stubbed generation, minus the wide-12 list; MacBook, desktop proxy, one run each, other load on the machine):\n")
L.append("| set | v2 mean / p50 ms | v3 mean / p50 ms |"); L.append("|---|---|---|")
if "v2" in m and "v3" in m: L.append(f"| MAIN 97 (K1 kit, a2+extra) | {m['v2']['wall_ms_mean']:.0f} / {m['v2']['wall_ms_p50']:.0f} | {m['v3']['wall_ms_mean']:.0f} / {m['v3']['wall_ms_p50']:.0f} |")
if "v3extra" in res["arms"]:
    for b, lab in (("v2off", "QFORM 432 v2 off"), ("v2k1", "QFORM 432 v2 K1")):
        L.append(f"| {lab} vs v3 extra | {res['arms'][b]['wall_ms_mean']:.0f} / {res['arms'][b]['wall_ms_p50']:.0f} | {res['arms']['v3extra']['wall_ms_mean']:.0f} / {res['arms']['v3extra']['wall_ms_p50']:.0f} |")
open(H + "/reads.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
