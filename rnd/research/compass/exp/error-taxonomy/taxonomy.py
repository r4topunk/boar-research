# Where do the Android 4B's in-kit items lose points? (v0.1 public, and-qwen s42/s43; read-only; Sonar tools reused)
import json, collections, sys
T = "<workspace>/rnd/research/sonar/tools/"
src = open(T + "key_in_context.py").read().split('if __name__ == "__main__":')[0]; exec(src)       # Resolver, key_hit, score
cc = open(T + "coverage_classes.py").read(); exec(cc.split("def main():")[0].split("exec(open(")[0])  # header only
exec("def titles_of" + cc.split("def titles_of")[1].split("def main():")[0])
QP = "<workspace>/boar-eval/bench/v0.1/questions.public.jsonl"
qs = {json.loads(l)["id"]: json.loads(l) for l in open(QP)}
res = Resolver(False)  # kit A (no vital5), as and-qwen ran
# coverage class per item against kit A (same logic as coverage_classes.main)
cls = {}
for q in qs.values():
    g = q.get("grading") or {}
    if not (g.get("must_any") or g.get("must_k")): cls[q["id"]] = "unkeyed"; continue
    texts = []
    for title, voyage in titles_of(q):
        tx = res.text({"title": f"Wikivoyage: {title}" if voyage else title, "source": "https://en.wikivoyage.org/" if voyage else None})
        if tx is not None: texts.append(tx)
    cls[q["id"]] = "not-in-kit" if not texts else ("in-kit-key" if key_hit("\n".join(texts), g) else "in-kit-no-key")
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
B = "<workspace>/boar-eval/runs/night-2026-10-01/"
rows = []
for run in ("and-qwen-s42", "and-qwen-s43"):
    kic, _ = score(qs, B + run + ".traces.jsonl", res)
    T_ = {json.loads(l)["itemId"]: json.loads(l) for l in open(B + run + ".traces.jsonl")}
    J = collections.defaultdict(list)
    for l in open(B + run + ".judgments.jsonl"):
        r = json.loads(l)
        if r.get("ok"): J[r["queryId"]].append(r)
    for q, v in J.items():
        if len(v) != 2 or q not in qs: continue
        b = {k: sum(x["mapped"]["boar"][k] for x in v) / 2 for k in K}; rf = {k: sum(x["mapped"]["ref"][k] for x in v) / 2 for k in K}
        t = T_[q]; a = t["answer"]; g = qs[q].get("grading") or {}
        k = kic.get(q, {})
        ans_key = bool(g.get("must_any") or g.get("must_k")) and key_hit(a.get("text") or "", g)
        if a.get("declined"): cat = "1 declined"
        elif cls[q] in ("unkeyed",): cat = "x unkeyed"
        elif not k.get("raw"): cat = "2 key not retrieved"
        elif not k.get("pre"): cat = "3 retrieved, dropped before prompt"
        elif not ans_key: cat = "4 in context, not used"
        elif b["correctness"] < 3: cat = "5 used, but wrong (synthesis/reasoning)"
        elif b["completeness"] < 4: cat = "6 correct but incomplete"
        else: cat = "7 near reference"
        rows.append({"run": run, "id": q, "class": cls[q], "cat": cat, "lost": mr(rf) - mr(b), "b": b, "ref": rf,
                     "rationale": (v[0]["verdict"].get("rationale") or "")[:300], "answer": (a.get("text") or "")[:300]})
json.dump(rows, open("rows.json", "w"), ensure_ascii=False, indent=0)
for scope, f in (("in-kit-key", lambda r: r["class"] == "in-kit-key"), ("in-kit-no-key", lambda r: r["class"] == "in-kit-no-key"),
                 ("not-in-kit", lambda r: r["class"] == "not-in-kit"), ("all keyed", lambda r: r["class"] != "unkeyed")):
    S = [r for r in rows if f(r)]; tot = sum(r["lost"] for r in S)
    print(f"\n== {scope}: {len(S)} item-runs ({len({r['id'] for r in S})} items), lost rubric points {tot:.1f}")
    c = collections.defaultdict(lambda: [0, 0.0])
    for r in S: c[r["cat"]][0] += 1; c[r["cat"]][1] += r["lost"]
    for cat, (n, l) in sorted(c.items()): print(f"   {cat:42} n={n:2}  lost {l:5.1f} ({l / tot:4.0%})  mean lost/item {l / n:.2f}")
