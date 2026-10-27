"""H3 MAIN 97 autopsy (0 LLM): per S2/S3 id and per S4/S5 id, the FACTPRESENT check (sweep.py rule) at four points:
rawFull (retrieved), compress output switch off / on (tools/h3-stage.mts at budget 700, validated 85/86 vs the replay's context codes), kept list B0 / H3.
usage: python3 -I tools/h3_main_autopsy.py <stage700 of B0.main> <H3.main.jsonl>"""
import json, sys, re
R = "<workspace>/rnd/research/coordinator/arms/retrieve-sweep"; CO = R + "/../.."; QF = R + "/../qform"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
src = open(R + "/tools/sweep.py").read().split("\n")
a = next(i for i, l in enumerate(src) if l.startswith("spec = importlib.util.spec_from_file_location")); b = next(i for i, l in enumerate(src) if l.startswith("FUN = json.load"))
BE = "<workspace>/boar-eval/bench/"; import importlib.util, glob, unicodedata
exec("\n".join(src[a:b]))
FUN = json.load(open(CO + "/ruler/RAG-FUNNEL-2026-10-21.json"))["items"]
S23 = [l.strip() for l in open(QF + "/funnel-S2S3.ids") if l.strip()]
S45 = sorted(i for i, v in FUN.items() if v["K1"]["vstage"] in ("S4", "S5"))
st = {r["id"]: r for r in rd(sys.argv[1])}; b0 = {r["id"]: r for r in rd(R + "/replay/B0.main.jsonl")}; h3 = {r["id"]: r for r in rd(sys.argv[2])}
blk = lambda cs: [f"{c['title']}\n{c['body']}" for c in cs]
def row(i):
    s = st[i]; r = b0[i]
    ids_changed = [c["chunkId"] for c in b0[i]["keptFull"]] != [c["chunkId"] for c in h3[i]["keptFull"]]
    body_changed = [c["body"] for c in b0[i]["keptFull"]] != [c["body"] for c in h3[i]["keptFull"]]
    pr = lambda x: {None: "-", True: "Y", False: "n"}[x]
    return dict(id=i, vstage=FUN[i]["K1"]["vstage"], raw=pr(present(i, r["rawFull"])), cmp_off=pr(present(i, [{"title": t, "body": b} for t, b in zip(s["off"]["titles"], s["off"]["bodies"])])),
                cmp_on=pr(present(i, [{"title": t, "body": b} for t, b in zip(s["on"]["titles"], s["on"]["bodies"])])), kept_B0=pr(present(i, b0[i]["keptFull"])), kept_H3=pr(present(i, h3[i]["keptFull"])),
                fired="rs:compress-head" in h3[i]["reasonCodes"], ids_changed=ids_changed, body_changed=body_changed,
                ctx_B0=next((c for c in b0[i]["reasonCodes"] if c.startswith("context:")), ""), ctx_H3=next((c for c in h3[i]["reasonCodes"] if c.startswith("context:")), ""),
                nk0=len(b0[i]["keptFull"]), nk3=len(h3[i]["keptFull"]))
out = {"S23": [row(i) for i in S23], "S45": [row(i) for i in S45]}
json.dump(out, open(R + "/aggregates/h3-main-autopsy.json", "w"), indent=1)
for k in ("S23", "S45"):
    print(k); print("id | raw | cmp_off | cmp_on | kept_B0 | kept_H3 | fired | ids_chg | ctx_B0 -> ctx_H3 | kept n")
    for r in out[k]: print(" | ".join(str(r[x]) for x in ("id", "raw", "cmp_off", "cmp_on", "kept_B0", "kept_H3", "fired", "ids_changed")), "|", r["ctx_B0"], "->", r["ctx_H3"], "|", r["nk0"], "->", r["nk3"])
