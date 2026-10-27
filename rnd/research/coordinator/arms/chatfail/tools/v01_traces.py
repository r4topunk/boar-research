"""CHATFAIL S1 v0.1 non-regression: out/gen-m4-{C0,A1}-v01.jsonl -> out/traces-v01-{C0,A1}.jsonl (EvalTrace layout of honestprompt/tools/convert_traces.py) + out/ids-v01.ids (the 57 ids of device-x6/v01.jids).
python3 -I tools/v01_traces.py"""
import json, hashlib, os
H = os.path.dirname(os.path.abspath(__file__)); O = H + "/out/"
ctx = {json.loads(l)["chat"]: json.loads(l) for l in open(O + "ctx-v01.jsonl") if l.strip()}
ids = [l.strip() for l in open("<workspace>/rnd/research/coordinator/arms/device-x6/v01.jids") if l.strip()]
open(O + "ids-v01.ids", "w").write("".join(i + "\n" for i in ids))
for arm in ("C0", "A1"):
    rows = {json.loads(l)["chat"]: json.loads(l) for l in open(O + f"gen-m4-{arm}-v01.jsonl") if l.strip()}
    assert set(rows) == set(ids), (arm, set(ids) - set(rows))
    p = O + f"traces-v01-{arm}.jsonl"
    with open(p, "w", encoding="utf-8") as f:
        for i in ids:
            a = rows[i]; titles = [s["title"] for s in ctx[i]["sources"]]
            f.write(json.dumps({"itemId": i, "answer": {"text": a["answer"], "cited": titles}, "engine": {"arm": f"chatfail-s1-{arm}", "commit": "b11010"},
                                "error": None if a["answer"].strip() else "empty", "timing": {"totalMs": a["ms"]}, "runId": f"chatfail-s1-v01-{arm}", "protocol": "1.0.0",
                                "runtime": {"model": "Qwen3-4B-Instruct-2507-Q4_K_M", "engine": "llama-server b11010 chat/completions, assembleChatMessages (reference engine path), Succinct"}}, ensure_ascii=False) + "\n")
    print(p, len(ids), hashlib.sha256(open(p, "rb").read()).hexdigest()[:16])
