"""Sonar exp-10: per-item judge score (mean rubric, BOAR side, both orders) vs whether the answer key reached the
pre-answer sources (tools/key_in_context.py, article mode). Shows how much a retrieval gain (key into the prompt) is
worth per item on each tier. Read-only on boar-eval runs."""
import json, sys, statistics, collections
sys.argv = ["x"]
exec(open("<workspace>/rnd/research/sonar/tools/key_in_context.py").read().split('if __name__ == "__main__":')[0])
R = "<workspace>/boar-eval/runs/night-2026-10-01/"
qs = {json.loads(l)["id"]: json.loads(l) for l in open("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl")}
res = Resolver(True)
def judge(run):
    s = collections.defaultdict(list)
    for l in open(R + run + ".judgments.jsonl"):
        j = json.loads(l)
        if j.get("ok") and j.get("mapped"):
            b, r = j["mapped"]["boar"], j["mapped"]["ref"]
            s[j["queryId"]].append((sum(b.values()) / 3, sum(r.values()) / 3))
    return {k: (statistics.mean(x[0] for x in v), statistics.mean(x[1] for x in v)) for k, v in s.items()}
for run in ["ios-main-s42", "ios-main-v5-s42", "and-qwen-s42", "and-gemma-s42"]:
    per, _ = score(qs, R + run + ".traces.jsonl", res); J = judge(run)
    both = [i for i in per if i in J]
    a = [J[i][0] / J[i][1] for i in both if per[i]["pre"]]; b = [J[i][0] / J[i][1] for i in both if not per[i]["pre"]]
    print(f"{run}: keyed+judged {len(both)} | key in pre n={len(a)} mean ratio {statistics.mean(a):.3f} | key not in pre n={len(b)} mean ratio {statistics.mean(b):.3f} | gap {statistics.mean(a)-statistics.mean(b):+.3f}")

print("\npaired: same items, key-in-pre changes between two runs (same tier)")
for a_run, b_run in [("ios-main-s42", "ios-main-v5-s42")]:
    pa, _ = score(qs, R + a_run + ".traces.jsonl", res); pb, _ = score(qs, R + b_run + ".traces.jsonl", res)
    Ja, Jb = judge(a_run), judge(b_run)
    for lab, cond in [("gained key", lambda i: pb[i]["pre"] and not pa[i]["pre"]), ("lost key", lambda i: pa[i]["pre"] and not pb[i]["pre"]), ("unchanged", lambda i: pa[i]["pre"] == pb[i]["pre"])]:
        ids = [i for i in pa if i in pb and i in Ja and i in Jb and cond(i)]
        d = [Jb[i][0] / Jb[i][1] - Ja[i][0] / Ja[i][1] for i in ids]
        print(f"  {a_run} -> {b_run} {lab}: n={len(ids)} mean Δratio {statistics.mean(d) if d else float('nan'):+.3f} {ids if len(ids) < 8 else ''}")
