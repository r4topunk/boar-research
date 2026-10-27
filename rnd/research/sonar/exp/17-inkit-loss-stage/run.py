"""Sonar exp-17 (new direction, same-model pipeline): where do the 4B's in-kit items lose points along the pipeline?
Android Qwen3-4B, kit A + vital5. Items = v0.1 public keyed items whose answer key is in the installed text of a
referenced article (tools/coverage_classes.py --vital5: in-kit-key). Stage of each item (exact passage text from
g1plus/and-main-v5-s42-kic, tools/key_in_context.py logic):
  R  = key NOT in the retriever's output (raw, article mode)      -> retrieval gap
  A  = key in raw, NOT in the pre-answer passages (exact)         -> assembly gap (gates, onSubject, compression)
  G  = key in the pre-answer passages                              -> generation / use of context
Points: judge mean rubric (BOAR side, both orders) from and-main-v5-s42/s43, vs reference; lost = ref - boar."""
import json, sys, collections, statistics
sys.argv = ["x"]
exec(open("<workspace>/rnd/research/sonar/tools/key_in_context.py").read().split('if __name__ == "__main__":')[0])
R = "<workspace>/boar-eval/runs/night-2026-10-01/"
qs = {json.loads(l)["id"]: json.loads(l) for l in open("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl")}
cls = json.load(open("<scratch>"))  # --vital5 classes
res = Resolver(True)
per, _ = score(qs, R + "g1plus/and-main-v5-s42-kic.traces.jsonl", res)
def judge(f):
    s = collections.defaultdict(list)
    for l in open(R + f):
        j = json.loads(l)
        if j.get("ok") and j.get("mapped"):
            b, r = j["mapped"]["boar"], j["mapped"]["ref"]; s[j["queryId"]].append((sum(b.values()) / 3, sum(r.values()) / 3))
    return s
J = collections.defaultdict(list)
for f in ["and-main-v5-s42.judgments.jsonl", "and-main-v5-s43.judgments.jsonl"]:
    for k, v in judge(f).items(): J[k] += v
rows = []
for i, c in cls.items():
    if c != "in-kit-key" or i not in per or i not in J: continue
    p = per[i]; stage = "G" if p["pre"] else ("A" if p["raw"] else "R")
    b = statistics.mean(x[0] for x in J[i]); r = statistics.mean(x[1] for x in J[i])
    rows.append((stage, i, b, r))
tot_lost = sum(r - b for _, _, b, r in rows)
print(f"in-kit-key items judged: {len(rows)}; points lost (ref - boar, mean over seeds/orders) total {tot_lost:.2f}")
for st, name in [("R", "retrieval gap"), ("A", "assembly gap"), ("G", "key in context (generation)")]:
    sel = [x for x in rows if x[0] == st]
    if not sel: print(f"  {st} {name}: 0"); continue
    lost = sum(r - b for _, _, b, r in sel)
    print(f"  {st} {name}: n={len(sel)} ratio {sum(b for *_, b, _ in sel)/sum(r for *_, r in sel):.3f} lost {lost:.2f} ({100*lost/tot_lost:.0f}% of in-kit loss) items {[x[1] for x in sel]}")
