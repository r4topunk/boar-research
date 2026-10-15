"""LONGSESSION references = the STANDALONE run's answers (0 LLM calls), in the bench refs format (bench/v0.1/refs/refs.jsonl + MANIFEST.json).
Usage: python3 -I make_refs.py <slice dir> <standalone traces.jsonl>"""
import json, sys, os, hashlib, datetime
d, tp = sys.argv[1:3]; qp = os.path.join(d, "questions.jsonl"); h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
Q = [json.loads(l) for l in open(qp) if l.strip()]; T = {}
for l in open(tp):
    if l.strip(): t = json.loads(l); T[t["itemId"]] = t
rows = []
for q in Q:
    t = T.get(q["id"]); txt = ((t or {}).get("answer") or {}).get("text", "") if t and not t.get("error") else ""
    rows.append({"id": q["id"], "category": q["category"], "lang": "en", "question": q["question"], "ok": bool(txt.strip()), "answer": txt})
os.makedirs(os.path.join(d, "refs"), exist_ok=True); rp = os.path.join(d, "refs", "refs.jsonl")
open(rp, "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
man = {"bench": "boar-eval slice longsession-v1 (agent-written dev); references = the engine's own STANDALONE answers (no history), not frontier answers",
       "questions_sha256": h(qp), "jsonl_sha256": h(rp), "frozen": True, "n_items": len(rows), "n_ok": sum(r["ok"] for r in rows),
       "missing_ids": [r["id"] for r in rows if not r["ok"]], "source_traces": os.path.basename(tp), "source_traces_sha256": h(tp),
       "source_run": "ls-standalone-s42 (cut 7, runner-local/be-0cfd4a77-cut7, seed 42, kit boar-crypto + boar-wikivoyage-en)",
       "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat()}
open(os.path.join(d, "refs", "MANIFEST.json"), "w").write(json.dumps(man, indent=1) + "\n")
print(json.dumps({k: man[k] for k in ("n_items", "n_ok", "missing_ids", "jsonl_sha256")}))
