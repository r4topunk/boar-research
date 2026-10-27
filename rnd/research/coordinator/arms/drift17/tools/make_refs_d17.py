"""DRIFT17 references = the 1.7B STANDALONE run's answers (0 LLM calls), bench refs format. Usage: python3 -I make_refs_d17.py <bench dir> <questions.jsonl> <standalone traces>"""
import json, sys, os, hashlib, datetime, shutil
d, qsrc, tp = sys.argv[1:4]; h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
os.makedirs(os.path.join(d, "refs"), exist_ok=True); qp = os.path.join(d, "questions.jsonl"); shutil.copyfile(qsrc, qp)
Q = [json.loads(l) for l in open(qp) if l.strip()]; T = {t["itemId"]: t for t in map(json.loads, open(tp))}
rows = []
for q in Q:
    t = T.get(q["id"]); txt = ((t or {}).get("answer") or {}).get("text", "") if t and not t.get("error") else ""
    rows.append({"id": q["id"], "category": q["category"], "lang": "en", "question": q["question"], "ok": bool(txt.strip()), "answer": txt})
rp = os.path.join(d, "refs", "refs.jsonl"); open(rp, "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
man = {"bench": "DRIFT17 copy of boar-eval slice longsession-v1 (agent-written dev); references = the 1.7B lite K0 engine's own STANDALONE answers, not frontier answers",
       "questions_sha256": h(qp), "jsonl_sha256": h(rp), "frozen": True, "n_items": len(rows), "n_ok": sum(r["ok"] for r in rows),
       "missing_ids": [r["id"] for r in rows if not r["ok"]], "source_traces": os.path.basename(tp), "source_traces_sha256": h(tp),
       "source_run": "d17-standalone-s42 (mini, be-0cfd4a77-cut7-litepacks, LITEDECLINE_OFF=5, Qwen3-1.7B, seed 42, kit K0)",
       "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat()}
open(os.path.join(d, "refs", "MANIFEST.json"), "w").write(json.dumps(man, indent=1) + "\n")
print(json.dumps({k: man[k] for k in ("n_items", "n_ok", "missing_ids", "jsonl_sha256")}))
