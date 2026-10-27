"""G1-SWA5 request maker (0 LLM). Writes the three phone requests from the frozen ids file.
  python3 -I mkreq_swa5.py   (paths fixed below)
Each request = warmup-000 (standalone, needed by the route gate) + 2 longsession-v1 sessions x 5 turns in turn order,
with the bench-only "session" block (bench-app/src/benchSession.ts) and engineOverrides {reload, temperature 0, seed 42}
(+ swaFull true for swa5-g-full). Kit: the A-union kit already on the phone (as gemmaa73-a)."""
import json, hashlib, pathlib
B = pathlib.Path("<workspace>")
IDS = B / "rnd/research/coordinator/ruler/ids/swa5.ids"
Q = {(d := json.loads(l))["id"]: d for l in open(B / "boar-eval/bench/slices/longsession-v1/questions.jsonl") if l.strip()}
OUT = B / "handoff/pixel8-2026-10-20/bench/requests"
ids = [l.strip() for l in open(IDS) if l.strip() and not l.startswith("#")]
groups = {}
for i in ids: groups.setdefault(Q[i]["session"], []).append(i)
assert len(groups) == 2 and all(len(g) == 5 for g in groups.values()), groups
for g in groups.values(): assert [Q[i]["turn"] for i in g] == [1, 2, 3, 4, 5], g
ARMS = {"swa5-g-default": ("gemma-4-e2b-it-q4km", False), "swa5-g-full": ("gemma-4-e2b-it-q4km", True), "swa5-q17-default": ("qwen3-1.7b-q4km", False)}
for rid, (model, full) in ARMS.items():
    ov = {"reload": True, "temperature": 0, "seed": 42, "label": rid}
    if full: ov["swaFull"] = True
    req = {"requestId": rid, "pipeline": "answer", "models": [model], "answerSettings": {"quickFirst": True, "alwaysComplete": False},
           "evalSetVersion": "longsession-v1-swa5", "engineOverrides": ov, "session": {"groups": list(groups.values())},
           "questions": [{"id": "warmup-000", "query": "What is the capital of France?", "category": "warmup"}]
                        + [{"id": i, "query": Q[i]["question"], "category": Q[i]["category"]} for i in ids]}
    p = OUT / f"{rid}.request.json"; p.write_text(json.dumps(req, indent=1, ensure_ascii=False) + "\n")
    print(rid, hashlib.sha256(p.read_bytes()).hexdigest()[:8], len(req["questions"]), "questions")
