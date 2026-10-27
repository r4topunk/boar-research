#!/usr/bin/env python3
"""QUANTCEIL smoke gate (argv1 = traces.jsonl; rc 0 = pass): 3/3 deep-thinking on the iq3xxs model, 0 errors, 1 <= reasoning <= 522, non-empty answers,
peak RSS <= 12 GB. Prints counts + timing (load/ttft/total/decode) only."""
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
codes = [set(r.get("route", {}).get("reasonCodes") or []) for r in rows]
deep = sum("generate:deep-thinking" in c for c in codes); model = sum("generate:deep-model-qwen3.6-35b-a3b-ud-iq3xxs" in c for c in codes)
err = sum(1 for r in rows if r.get("error")); ans = sum(1 for r in rows if (r.get("answer") or {}).get("text"))
rt = [int((r.get("timing") or {}).get("reasoningTokens") or 0) for r in rows]; rok = sum(1 <= t <= 522 for t in rt)
rss = [((r.get("resources") or {}).get("peakRssMb") or 0) for r in rows]; tot = [round((r.get("timing") or {}).get("totalMs", 0) / 1000) for r in rows]
ttft = [round((r.get("timing") or {}).get("ttftMs", 0) / 1000) for r in rows]; dec = [(r.get("timing") or {}).get("decodeTokPerSec") for r in rows]
print(f"n={len(rows)} deep={deep} iq3model={model} errors={err} answers={ans} reasoning={rt} rss_mb={rss} ttft_s={ttft} total_s={tot} decode_tps={dec}")
ok = len(rows) >= 3 and deep == len(rows) and model == len(rows) and err == 0 and ans == len(rows) and rok == len(rows) and max(rss) <= 12288
print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
