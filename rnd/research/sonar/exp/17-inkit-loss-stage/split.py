import json, sys, re
sys.argv = ["x"]
exec(open("<workspace>/rnd/research/sonar/tools/key_in_context.py").read().split('if __name__ == "__main__":')[0])
R = "<workspace>/boar-eval/runs/night-2026-10-01/"
qs = {json.loads(l)["id"]: json.loads(l) for l in open("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl")}
res = Resolver(True)
T = {json.loads(l)["itemId"]: json.loads(l) for l in open(R + "g1plus/and-main-v5-s42-kic.traces.jsonl")}
A = ['vit-hum-002', 'vit-trv-003', 'vit-hlt-002', 'lan-ref-002', 'lan-ref-003', 'lan-rsn-003', 'lan-cmp-003', 'lan-ref-004', 'lan-exp-003', 'lan-cmp-005', 'lan-rsn-005']
for i in A:
    t = T[i]; g = qs[i]["grading"]
    keyarts = sorted({s["title"] for s in t["retrieval"]["raw"] if (res.text(s) or "") and key_hit(res.text(s), g)})
    ev = [e for e in t["events"] if e["type"] == "sources"]; pre = ev[-1]["sources"] if ev else []
    pre_titles = {s["title"] for s in pre}
    codes = [c for c in t["route"]["reasonCodes"] if re.match(r"(context:\d|grounding:(off-topic|no-good|health))", c)]
    kind = "article kept, key cut (passage/compression)" if any(k in pre_titles for k in keyarts) else "article dropped (onSubject/gates/cut)"
    print(f"{i:12} {kind:45} key-articles={keyarts} pre={sorted(pre_titles)[:3]} {codes}")
