"""Sonar exp-18 (card P-1 'keep the key'): items (v0.1 public, keyed) whose answer-bearing article is in the retriever's
output (raw) but not in the pre-answer sources, on and-qwen s42/s43 (Android Qwen3-4B, kit A: corpus + Wikivoyage + crypto).
Title-level (these runs carry no passage text): an article is 'key-bearing' if its installed text holds the key."""
import json, sys, re
sys.argv = ["x"]
exec(open("<workspace>/rnd/research/sonar/tools/key_in_context.py").read().split('if __name__ == "__main__":')[0])
R = "<workspace>/boar-eval/runs/night-2026-10-01/"
qs = {json.loads(l)["id"]: json.loads(l) for l in open("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl")}
res = Resolver(False)  # kit A: no vital5
out = {}
for run in ["and-qwen-s42", "and-qwen-s43"]:
    for l in open(R + run + ".traces.jsonl"):
        t = json.loads(l); q = qs.get(t["itemId"]); g = (q or {}).get("grading", {})
        if not (g.get("must_any") or g.get("must_k")): continue
        keyarts = sorted({s["title"] for s in t["retrieval"]["raw"] if key_hit(res.text(s) or "", g)})
        ev = [e for e in t["events"] if e["type"] == "sources"]; pre = {s["title"] for s in (ev[-1]["sources"] if ev else [])}
        if keyarts and not (set(keyarts) & pre):
            codes = [c for c in t["route"]["reasonCodes"] if re.match(r"(task:|context:|grounding:|instant:)", c)]
            out.setdefault(t["itemId"], {})[run] = {"key_articles": keyarts, "raw": [s["title"] for s in t["retrieval"]["raw"]], "pre": sorted(pre), "codes": codes, "tier": t["route"]["tier"]}
json.dump(out, open("dropped.json", "w"), indent=1)
print(f"items with key-bearing article retrieved but absent from pre: {len(out)} (s42 {sum('and-qwen-s42' in v for v in out.values())}, s43 {sum('and-qwen-s43' in v for v in out.values())})")
for i, v in out.items():
    r = v.get("and-qwen-s42") or v.get("and-qwen-s43")
    print(f"{i:12} key={r['key_articles']} pre={r['pre'][:3]} tier={r['tier']} {r['codes']}")
