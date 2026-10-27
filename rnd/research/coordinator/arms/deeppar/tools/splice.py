#!/usr/bin/env python3
"""DEEPPAR-L1 splice: control-A trace rows + bmoe results -> bmoe-R450.traces.jsonl (criterion 'Traces' bullet).
usage: python3 splice.py <control.traces.jsonl> <results.jsonl> <out.traces.jsonl> <bmoe_sha256> [peak_footprint_gib]"""
import json, re, sys, copy
ctl, resp, outp, bsha = sys.argv[1:5]
peak = float(sys.argv[5]) if len(sys.argv) > 5 else None
R = {}
for l in open(resp):
    if l.strip(): d = json.loads(l); R[d["id"]] = d
think = 0; rows = []
for l in open(ctl):
    if not l.strip(): continue
    t = json.loads(l); r = R.get(t["itemId"]); n = copy.deepcopy(t)
    n["runId"] = "deeppar-l1-bmoe-R450"
    n["runtime"]["model"] = "bmoe-cli v0.28.0 374f562c (prints 0.27.0) + deep35 Q2_K_XL"
    n["runtime"]["versions"] = {**t["runtime"]["versions"], "bmoe-cli.sha256": bsha, "bmoe": "v0.28.0 374f562c"}
    n["runtime"]["versions"].pop("llama-server", None)
    txt = None if r is None or "error" in r else (r.get("text") or "")
    if txt is not None:
        m = re.findall(r"<think>[\s\S]*?</think>", txt); think += len(m)
        txt = re.sub(r"<think>[\s\S]*?</think>", "", txt).rstrip()
    n["answer"]["text"] = txt or ""
    n["error"] = None if txt else ("no-bmoe-output" if r is None or "error" in r else "empty-answer")
    if r and "error" not in r:
        n["timing"] = {"prefillS": r.get("prefill_s"), "decodeTokPerSec": r.get("tok_s"), "totalS": r.get("total_s"),
                       "promptTokens": r.get("n_prompt"), "outputTokens": r.get("tokens"), "loadS": r.get("load_s")}
    n["resources"] = {"peakFootprintGiB": peak}
    rows.append(n)
open(outp, "w").write("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows))
print(f"rows={len(rows)} errors={sum(1 for x in rows if x['error'])} think_blocks_stripped={think}")
