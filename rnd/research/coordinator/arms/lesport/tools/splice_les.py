#!/usr/bin/env python3
"""LESPORT-L1 splice (derived from arms/deeppar/tools/splice.py): control-A trace rows + LES fork results -> les-R450.traces.jsonl.
usage: python3 splice_les.py <control.traces.jsonl> <results.jsonl> <out.traces.jsonl> <fork_commit> <binary_sha256> <model_sha256>"""
import json, re, sys, copy
ctl, resp, outp, commit, bsha, msha = sys.argv[1:7]
R = {}
for l in open(resp):
    if l.strip(): d = json.loads(l); R[d["id"]] = d
think = 0; eot = 0; trunc = 0; rows = []
for l in open(ctl):
    if not l.strip(): continue
    t = json.loads(l); r = R.get(t["itemId"]); n = copy.deepcopy(t)
    n["runId"] = "lesport-l1-les-R450"
    n["engine"] = {**t.get("engine", {}), "arm": "oracle-R450-les"}
    n["runtime"]["adapter"] = "llama-completion (llama-omni fork, LES)"
    n["runtime"]["backend"] = "llama.cpp-omni fork CPU, LES expert streaming bank 1280, lookahead prefetch"
    n["runtime"]["host"] = "Mac mini M4 CPU x4 (llama-completion LES)"
    n["runtime"]["model"] = f"llama-omni fork {commit[:8]} (LES, bank 1280) + deep35 Q2_K_XL"
    n["runtime"]["sampler"] = {"temperature": 0.7, "top_k": 40, "top_p": 0.95, "min_p": 0.05, "seed": 42}
    n["runtime"]["versions"] = {**t["runtime"]["versions"], "llama-completion.sha256": bsha, "llama-omni": commit, "model.sha256": msha}
    n["runtime"]["versions"].pop("llama-server", None)
    txt = None if r is None or r.get("rc") != 0 else (r.get("text") or "")
    if txt is not None:
        m = re.findall(r"<think>[\s\S]*?</think>", txt); think += len(m)
        txt = re.sub(r"<think>[\s\S]*?</think>", "", txt)
        if re.search(r"\s*\[end of text\]\s*$", txt): eot += 1
        txt = re.sub(r"\s*\[end of text\]\s*$", "", txt).strip()
        if r.get("out_tokens") and r["out_tokens"] >= 512: trunc += 1
    n["answer"]["text"] = txt or ""
    n["error"] = None if txt else ("no-fork-output" if r is None or r.get("rc") != 0 else "empty-answer")
    if r:
        n["timing"] = {"prefillS": r.get("prefill_s"), "decodeTokPerSec": r.get("tok_s"), "totalS": r.get("wall_s"),
                       "promptTokens": r.get("n_prompt"), "outputTokens": r.get("out_tokens"), "loadS": r.get("load_s")}
        n["resources"] = {"peakRssGiB": r.get("rss_gib"), "peakFootprintGiB": r.get("footprint_gib")}
    rows.append(n)
open(outp, "w").write("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows))
print(f"rows={len(rows)} errors={sum(1 for x in rows if x['error'])} think_blocks_stripped={think} end_of_text_markers_stripped={eot} hit_512={trunc}")
