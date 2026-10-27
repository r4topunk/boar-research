"""LITESAFETY requests (0 LLM): warnspec/runs/warn-replay-{probes,v01}.pr1+warn.requests.jsonl with runId set and modelId per model;
items, kit, seed, settings unchanged. Usage: python3 -I mkreq_ls.py <out dir>"""
import json, sys
W = "<workspace>/rnd/research/coordinator/arms/warnspec/runs"; out = sys.argv[1]
M = {"1p7b": "qwen3-1.7b-q4km", "4b": "qwen3-4b-instruct-2507-q4km"}
for s in ["probes", "v01"]:
    rows = [json.loads(l) for l in open(f"{W}/warn-replay-{s}.pr1+warn.requests.jsonl") if l.strip()]
    for m, mid in M.items():
        with open(f"{out}/ls-{s}-{m}.requests.jsonl", "w") as o:
            for r in rows:
                r = json.loads(json.dumps(r)); r["runId"] = f"ls-{s}-{m}-s42"; r["config"]["modelId"] = mid
                o.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
        print(s, m, len(rows))
