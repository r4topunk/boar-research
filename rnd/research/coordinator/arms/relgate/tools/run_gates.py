#!/usr/bin/env python3
"""RELGATE Phase 2 runner: next-token P(yes)/(P(yes)+P(no)) and digit distributions from a llama-server.
usage: run_gates.py --url http://127.0.0.1:18191 --model m4|q17 --out ../runs/<model>.jsonl [--limit N]
Rows: {key, kind: main|G1|G2|G3|S1|S2, wording, p, py, pn, mass, digits, prompt_n, cache_n, prompt_ms}. Resumable."""
import json, os, sys, time, argparse, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("--url", required=True); ap.add_argument("--model", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--limit", type=int, default=0)
a = ap.parse_args()
ARM = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = f"{ARM}/data"

YES = ["yes", "Yes", "YES", " yes", " Yes"]; NO = ["no", "No", "NO", " no", " No"]
DIG = [str(i) for i in range(10)]
G1SYS = "You check whether a passage contains information needed to answer a question."
W = {
    "W1": "Does this passage contain the specific fact needed to answer the question? Reply yes or no.",
    "W2": ("Does this passage contain the specific fact needed to answer the question?\n"
           "- yes: the passage states the concrete fact, figure, name, step or mechanism the question asks for\n"
           "- no: the passage is about something else, only touches the topic in general terms, or lacks that specific content\n"
           "Reply yes or no."),
    "W3": ("A specific fact means the concrete value, name, date, step or explanation the question asks for, not just the topic. "
           "Does this passage contain the specific fact needed to answer the question? Reply yes or no."),
}
G2Q = "Before answering: does the context above contain the answer to my question? Reply yes or no."
G3Q = "Before answering: which source number above contains the answer to my question? Reply with one number, or 0 if none."
ASST = "<|im_start|>assistant\n" + ("<think>\n\n</think>\n\n" if a.model == "q17" else "")

def call(prompt):
    body = json.dumps({"prompt": prompt, "n_predict": 1, "n_probs": 100, "temperature": 0, "cache_prompt": True}).encode()
    for k in range(5):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(a.url + "/completion", body, {"Content-Type": "application/json"}), timeout=600))
            break
        except Exception as e:
            print("retry", e, file=sys.stderr); time.sleep(5)
    else:
        raise SystemExit("server failed")
    top = {t["token"]: 2.718281828459045 ** t["logprob"] for t in r["completion_probabilities"][0]["top_logprobs"]}
    t = r["timings"]
    return top, {"prompt_n": t["prompt_n"], "cache_n": t.get("cache_n"), "prompt_ms": round(t["prompt_ms"], 1), "pred_ms": round(t["predicted_ms"], 1)}

def yn(top):
    py = sum(top.get(x, 0) for x in YES); pn = sum(top.get(x, 0) for x in NO)
    return (py / (py + pn) if py + pn > 0 else 0.5), py, pn

def chat(system, user):
    return f"<|im_start|>system\n{system}<|im_end|>\n<|im_start|>user\n{user}"

done = set()
if os.path.exists(a.out):
    done = {json.loads(l)["key"] for l in open(a.out)}
out = open(a.out, "a")
def emit(row):
    out.write(json.dumps(row) + "\n"); out.flush()

def g_yes(key, kind, prompt, wording=None):
    if key in done: return
    top, tm = call(prompt)
    p, py, pn = yn(top)
    emit({"key": key, "kind": kind, "wording": wording, "p": p, "py": py, "pn": pn, "mass": py + pn, **tm})

K = [json.loads(l) for l in open(f"{D}/contexts.jsonl")]
C = [json.loads(l) for l in open(f"{D}/chunks.jsonl")]
S = [json.loads(l) for l in open(f"{D}/safety.jsonl")]
byid = {}
for c in C: byid.setdefault(c["id"], []).append(c)
if a.limit: K = K[: a.limit]
t0 = time.time()
for i, k in enumerate(K):
    sysm, user = k["prompt"][0]["content"], k["prompt"][1]["content"]
    base = chat(sysm, user)
    mk = f"{k['id']}|main"
    if mk not in done:
        top, tm = call(base + "<|im_end|>\n" + ASST)
        emit({"key": mk, "kind": "main", **tm})
    g_yes(f"{k['id']}|G2", "G2", base + f"<|im_end|>\n<|im_start|>user\n{G2Q}<|im_end|>\n" + ASST)
    gk = f"{k['id']}|G3"
    if gk not in done:
        top, tm = call(base + f"<|im_end|>\n<|im_start|>user\n{G3Q}<|im_end|>\n" + ASST)
        dig = {d: top.get(d, 0) for d in DIG}
        emit({"key": gk, "kind": "G3", "digits": dig, "mass": sum(dig.values()), **tm})
    for c in byid[k["id"]]:
        pre = chat(G1SYS, f"Question: {c['question']}\n\nPassage:\n{c['chunk']}\n\n")
        for w, txt in W.items():
            g_yes(f"{c['cid']}|G1|{w}", "G1", pre + txt + "<|im_end|>\n" + ASST, w)
    print(f"[{a.model}] {i+1}/{len(K)} {time.time()-t0:.0f}s", file=sys.stderr, flush=True)

# Safety set: G1 (3 wordings) and G2 on an engine-shaped prompt
ref = K[0]["prompt"] if not a.limit else None
firstaid = next(json.loads(l) for l in open(f"{D}/contexts.jsonl") if json.loads(l)["pack"] == "boar-firstaid-en")
fs_sys = firstaid["prompt"][0]["content"].split("\n\nContext:\n")[0]
style = "\n\n(Response style:" + firstaid["prompt"][1]["content"].split("\n\n(Response style:")[1]
for s in S if not a.limit else []:
    pre = chat(G1SYS, f"Question: {s['question']}\n\nPassage:\n{s['title']}\n{s['passage']}\n\n")
    for w, txt in W.items():
        g_yes(f"{s['sid']}|S1|{w}", "S1", pre + txt + "<|im_end|>\n" + ASST, w)
    eng = chat(fs_sys + f"\n\nContext:\n[1] {s['title']}\n{s['passage']}", s["question"] + style)
    mk = f"{s['sid']}|Smain"
    if mk not in done:
        top, tm = call(eng + "<|im_end|>\n" + ASST); emit({"key": mk, "kind": "Smain", **tm})
    g_yes(f"{s['sid']}|S2", "S2", eng + f"<|im_end|>\n<|im_start|>user\n{G2Q}<|im_end|>\n" + ASST)
print(json.dumps({"model": a.model, "seconds": round(time.time() - t0, 1)}))
