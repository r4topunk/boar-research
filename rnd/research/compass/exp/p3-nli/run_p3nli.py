# P3-NLI-0 runner (implements protocol.md, frozen 2fe0ffd5…). Usage: .venv/bin/python run_p3nli.py out.jsonl
import json, re, sys, time, math
import numpy as np, onnxruntime as ort
from transformers import AutoTokenizer
P = json.load(open("<workspace>/rnd/research/anvil/exp/p3-selfcheck/protocol.json"))
RUNS = "<workspace>/boar-eval/runs/night-2026-10-01/"
S44 = "<workspace>/boar-eval/runs/and-qwen-s44/and-qwen-s44."
load = lambda p: [json.loads(l) for l in open(p) if l.strip()]
dump = {r["itemId"]: r["messages"] for r in load(S44 + "prompts.jsonl")}
t44 = {r["itemId"]: r for r in load(S44 + "traces.jsonl")}
traces = {}
def trace(run, i):
    if run not in traces: traces[run] = {r["itemId"]: r for r in load(RUNS + run + ".traces.jsonl")}
    return traces[run].get(i)
titles = lambda r: [s["title"] for s in ((r or {}).get("retrieval") or {}).get("kept") or []]
split = lambda t: [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", t) if s.strip()]
tok = AutoTokenizer.from_pretrained("model")
so = ort.SessionOptions(); so.intra_op_num_threads = 4
sess = ort.InferenceSession("model/onnx/model_quantized.onnx", so, providers=["CPUExecutionProvider"])
names = [i.name for i in sess.get_inputs()]
def sources(system):
    ctx = system.split("Context:", 1)[1] if "Context:" in system else ""
    return [b.strip() for b in re.split(r"\n\s*\n(?=\[\d+\])", ctx.strip()) if b.strip()]
def windows(src):
    body = re.sub(r"^\[\d+\]\s*", "", src)
    ss = split(body)
    return [" ".join(ss[i:i + 3]) for i in range(max(1, len(ss) - 2))] if ss else []
def nli(prem, hyps):
    enc = tok([prem] * len(hyps), hyps, truncation="only_first", max_length=512, padding=True, return_tensors="np")
    feed = {n: enc[n].astype(np.int64) for n in names if n in enc}
    lg = sess.run(None, feed)[0]; e = np.exp(lg - lg.max(1, keepdims=True)); return e / e.sum(1, keepdims=True)
def truncate400(p): ids = tok(p, add_special_tokens=False)["input_ids"]; return p if len(ids) <= 400 else tok.decode(ids[:400])
out = open(sys.argv[1], "w"); res = []
for kind, items in (("pos", P["positives"]), ("neg", P["negatives"])):
    for it in items:
        tr, msgs = trace(it["run"], it["id"]), dump.get(it["id"])
        if not tr or not msgs or titles(tr) != titles(t44.get(it["id"])):
            r = {"kind": kind, **it, "excluded": True, "why": "no dump" if not msgs else "shown sources differ"}; out.write(json.dumps(r) + "\n"); res.append(r); continue
        sents = split(tr["answer"]["text"]); system = next(m["content"] for m in msgs if m["role"] == "system")
        wins = [truncate400(w) for s in sources(system) for w in windows(s)]
        hyps = [(i + 1, re.sub(r"\s*\[\d+\]", "", s).strip()) for i, s in enumerate(sents)]
        hyps = [(i, h) for i, h in hyps if len(h.split()) >= 4]
        t0 = time.process_time(); w0 = time.time()
        best = {i: (0.0, 0.0, 0.0, -1) for i, _ in hyps}  # maxC, entail-in-that-window, also max any window, window idx
        flagged_by = {i: set() for i, _ in hyps}
        for wi, w in enumerate(wins):
            if not hyps: break
            pr = nli(w, [h for _, h in hyps])
            for (i, _), (pe, pn, pc) in zip(hyps, pr):
                if pc > best[i][0]: best[i] = (float(pc), float(pe), 0.0, wi)
                if pc >= 0.90 and pc > pe: flagged_by[i].add(0.90)
                if pc >= 0.70 and pc > pe: flagged_by[i].add(0.70)
                if pc >= 0.50 and pc > pe: flagged_by[i].add(0.50)
        cpu, wall = time.process_time() - t0, time.time() - w0
        labels = {th: sorted(i for i in flagged_by if th in flagged_by[i]) for th in (0.90, 0.70, 0.50)}
        r = {"kind": kind, **it, "k": len(sents), "nWindows": len(wins), "nHyps": len(hyps), "labels": labels[0.90], "sweep": {str(k): v for k, v in labels.items()},
             "maxC": {i: round(b[0], 3) for i, b in best.items()}, "wall_s": round(wall, 2), "cpu_s": round(cpu, 2)}
        if kind == "pos": r["hit"] = bool(set(labels[0.90]) & set(it["targets"]))
        else: r["falseFlag"] = bool(labels[0.90])
        r["guardKeep"] = len(labels[0.90]) > len(sents) / 2
        out.write(json.dumps(r) + "\n"); res.append(r)
pos = [r for r in res if r["kind"] == "pos" and not r.get("excluded")]; neg = [r for r in res if r["kind"] == "neg" and not r.get("excluded")]
nh = sum(r["hit"] for r in pos); nf = sum(r["falseFlag"] for r in neg)
need_h = math.ceil(4 / 7 * len(pos)); max_f = math.floor(2 / 20 * len(neg))
print(f"excluded {len(res)-len(pos)-len(neg)}; hits {nh}/{len(pos)} (need >= {need_h}); false flags {nf}/{len(neg)} (max {max_f}) -> {'PASS' if nh >= need_h and nf <= max_f else 'FAIL'}")
for th in ("0.9", "0.7", "0.5"):
    print(f"sweep {th}: hits {sum(bool(set(r['sweep'][th]) & set(r['targets'])) for r in pos)}/{len(pos)}, false flags {sum(bool(r['sweep'][th]) for r in neg)}/{len(neg)}")
eff = sum(1 for r in pos if r["hit"] and not r["guardKeep"]); bad = sum(1 for r in neg if r["falseFlag"] and not r["guardKeep"])
w = sorted(r["wall_s"] for r in pos + neg)
print(f"after guard: effective target drops {eff}/{len(pos)}, correct answers losing a sentence {bad}/{len(neg)}; wall s/answer p50 {w[len(w)//2]} max {w[-1]} (4 threads, M1); windows p50 {sorted(r['nWindows'] for r in pos+neg)[len(w)//2]}")
