#!/usr/bin/env python3
"""O3 (early decline): Lantern's reference decide() on ALL prompt passages (before prefill), for P3 and H1 qwen3-4b.
Same text lookup as tools/o2_eval.py. Reports which late (cited) O2 hits the early check already catches, and the
prefill+generation time the early decline would save (harness rows only; iPhone rows use their own totalLatencyMs)."""
import json, sys
sys.path.insert(0, "<workspace>/rnd/lantern/tools")
import o2_reference as o, refusal_audit as ra
ra.configure(["boar-crypto", "boar-wikivoyage-en", "wiki-vital5"]); P = ra.Packs()
def text(t):
    bare = ra.strip_prefix(t)
    order = ["boar-wikivoyage-en"] if t.startswith("Wikivoyage: ") else ["boar-crypto"] if bare != t else ["boar-crypto", "wiki-vital5"]
    for pk in order:
        x = P._v1_text(pk, bare) if pk in ra.V1_PACKS else P._v2_text(pk, bare)
        if x: return x
late = {(d["src"], d["model"], d["queryId"]): d["o2Decline"] for d in map(json.loads, open("results/decisions-refA.jsonl"))}
t_h = {json.loads(l)["queryId"]: json.loads(l) for l in open("../exp-01-inram-moe-reader/runs/qwen3-4b.jsonl")}
t_p = {json.loads(l)["queryId"]: json.loads(l) for l in open("<workspace>/rnd/plumb/data/qwen2.5-1.5b-instruct-q4km__iphone-14de107-device-vital5.jsonl")}
for src, model in (("H1", "qwen3-4b"), ("P3", "qwen2.5-1.5b@iphone")):
    rows = [json.loads(l) for l in open("inputs.jsonl")]
    rows = [r for r in rows if r["src"] == src and r["model"] == model and not r["declined"] and r["label"] not in ("refused", "declined")]
    early, both, saved = [], 0, 0.0
    for r in rows:
        d = o.decide(r["query"], [{"title": t, "text": text(t)} for t in dict.fromkeys(r["promptTitles"])])
        if d["action"] == "refuse":
            early.append((r["queryId"], r["label"]))
            both += late.get((src, model, r["queryId"]), False)
            ms = (t_h[r["queryId"]]["totalMs"] if src == "H1" else (t_p[r["queryId"]].get("totalLatencyMs") or 0))
            saved += ms / 1000
    nlate = sum(1 for r in rows if late.get((src, model, r["queryId"])))
    print(f"{src} {model}: late (cited) hits {nlate}; early (prompt) hits {len(early)} {early}; early ∩ late {both}; answer time saved by early decline {saved:.1f} s total")
