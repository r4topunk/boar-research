#!/usr/bin/env python3
"""exp-04 LAYA arm: the SAME questions as the Jev arm (prompts/v2.json, frozen), one item per state, local CPU.

- Checkpoint: convaiinnovations/laya-multilingual @ e4e9ddf2 (mmBERT-base 322M; 1,024-token default context, raised
  with --max-len). The English `laya` checkpoint (ModernBERT-large, 512 tokens) is not used: our items are ~700 tokens,
  so it would truncate most of them.
- State per item: {"item": {question, reference, rubric, answer, retrieved_titles}}; the Jev instructions are used
  verbatim with the path `items.kNN` replaced by `item`. Jev `boolean` = Laya `noul` (same meaning, P(yes)).
- One predict() per item, like the phone would call it: per-item latency is measured around that call.
- --backend onnx uses laya.ONNXAgent over an export made by the repo's scripts/export_onnx.py (v0.3.21).
Output rows have the Jev arm's fields (jev = chosen label) so analyze.py / compare.py read them unchanged.
Usage: .venv/bin/python run_laya.py --prompts v2.json --rows rows-test.jsonl --out preds/laya-fp32-test.jsonl
       [--backend torch|onnx --onnx onnx/laya-int8.onnx] [--threads 4] [--max-len 2048] [--limit N]
"""
import argparse, hashlib, json, os, statistics, time

ap = argparse.ArgumentParser()
ap.add_argument("--prompts", required=True)
ap.add_argument("--rows", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--backend", choices=["torch", "onnx"], default="torch")
ap.add_argument("--onnx")
ap.add_argument("--threads", type=int, default=4)
ap.add_argument("--max-len", type=int, default=2048)
ap.add_argument("--limit", type=int, default=0)
ap.add_argument("--split", action="store_true", help="one question per predict() call (the ONNX export of v0.3.21 fails on 2 question rows in one call)")
ap.add_argument("--plain", action="store_true", help="diagnostic: plain-text state instead of the JSON item")
a = ap.parse_args()

os.environ.setdefault("OMP_NUM_THREADS", str(a.threads))
import torch  # noqa: E402
torch.set_num_threads(a.threads)
import laya  # noqa: E402

REPO, REV = "convaiinnovations/laya-multilingual", "e4e9ddf21a7b1903b7acffd8814ad4307bf63a67"
P = json.load(open(a.prompts))
prompt_sha = hashlib.sha256(open(a.prompts, "rb").read()).hexdigest()
fix = lambda s: s.replace("{item}", "item")
questions = {
    "label": {"type": "choice", "instructions": fix(P["label"]["instructions"]), "criteria": P["label"]["criteria"]},
    "unsafe": {"type": "noul", "instructions": fix(P["unsafe"]["instructions"]),
               **({"criteria": P["unsafe"]["criteria"]} if P["unsafe"].get("criteria") else {})},
}

t0 = time.perf_counter()
if a.backend == "torch":
    agent = laya.load(REPO, device="cpu", revision=REV)
else:
    from laya.onnx_agent import ONNXAgent
    agent = ONNXAgent(REPO, onnx_path=a.onnx, revision=REV)
load_s = time.perf_counter() - t0

rows = [json.loads(l) for l in open(a.rows) if l.strip()]
if a.limit:
    rows = rows[: a.limit]
out, lat = [], []
for i, r in enumerate(rows):
    state = {"item": {"question": r["query"], "reference": r["reference"], "rubric": r.get("rubric") or "",
                      "answer": r["answer"] if r["answer"].strip() else "(empty: the app showed no answer text)",
                      "retrieved_titles": r.get("titles") or []}}
    if a.plain:
        it = state["item"]
        state = (f"QUESTION: {it['question']}\nTRUSTED REFERENCE: {it['reference']}\nGRADING NOTES: {it['rubric']}\n"
                 f"APP ANSWER: {it['answer']}")
    t = time.perf_counter()
    if a.split:
        res = {"answers": {}, "usage": {"input_tokens": 0}}
        for qk, qv in questions.items():
            one = agent.predict(state, {qk: qv}, max_len=a.max_len)
            res["answers"][qk] = one["answers"][qk]
            res["usage"]["input_tokens"] = max(res["usage"]["input_tokens"], one["usage"]["input_tokens"])
    else:
        res = agent.predict(state, questions, max_len=a.max_len)
    dt = time.perf_counter() - t
    lat.append(dt)
    A = res["answers"]
    lab, un = A["label"], A["unsafe"]
    probs = lab.get("probabilities") or lab.get("probs")
    out.append({"src": r["src"], "model": r["model"], "queryId": r["queryId"], "hand": r["hand4"], "jev": lab.get("choice"),
                "probs": probs, "confidence": lab.get("confidence") or lab.get("answer_confidence"),
                "unsafe_p": un.get("noul", un.get("probability")), "batch_secs": round(dt, 4), "batch_usd": 0.0, "cached": False,
                "batch_n": 1, "prompt_sha": prompt_sha, "usage": res.get("usage"), "backend": a.backend})
    if i < 2 or (i + 1) % 25 == 0:
        print(f"{i + 1}/{len(rows)} {r['queryId']} -> {lab.get('choice')} ({dt * 1000:.0f} ms)", flush=True)
with open(a.out, "w") as f:
    for o in out:
        f.write(json.dumps(o) + "\n")
q = sorted(lat)
meta = {"split": a.split, "backend": a.backend, "onnx": a.onnx, "threads": a.threads, "max_len": a.max_len, "load_s": round(load_s, 2), "n": len(lat),
        "latency_ms_p50": round(statistics.median(q) * 1000, 1), "latency_ms_p95": round(q[int(0.95 * (len(q) - 1))] * 1000, 1),
        "latency_ms_mean": round(statistics.fmean(q) * 1000, 1), "repo": REPO, "revision": REV, "laya": laya.__version__,
        "torch": torch.__version__, "prompt_sha": prompt_sha}
json.dump(meta, open(a.out + ".meta.json", "w"), indent=1)
print(json.dumps(meta))
