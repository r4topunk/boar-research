#!/usr/bin/env python3
"""Kiln harness runs (exp-01 / exp-02: llama-server replaying BOAR's captured app contexts on the Mac mini) ->
device-metrics JSON, marked measurement.kind = "proxy".

Per LLM answer (serve-bench.py row):
  ttft_model_ms  = firstTokenMs  (request sent -> first streamed token of any kind; prompt already in the request, so
                                  this is MLPerf TTFT at engine level, plus localhost HTTP overhead of ~1 ms)
  ttft_answer_ms = ttftMs        (-> first visible answer token; differs only for reasoning models, e.g. Maple)
  tps            = (predictedN - 1) / (totalMs - firstTokenMs)   (MLPerf TPS, from wall-clock stream timestamps)
  tps_engine_reported = llama.cpp predicted_per_second
  prefill_tps    = llama.cpp prompt_per_second;  context_tokens = prompt_n (cache_prompt=false: full prefill)
  ttft_e2e_ms    = null (the proxy has no retrieval/UI; the contexts were captured once)
Memory: the clean probe (--cache-ram 0) if given, else the main run, flagged invalid when the server prompt cache was on.
Usage:
  python3 from_kiln_harness.py --model <id> --runs <runs.jsonl> [--mem-meta <runs-mem/X.jsonl.meta.json>] --out <file.json>
"""
import argparse, json, os
from bench_common import SCHEMA_VERSION, sha256_file, stat, mlperf_tps, sustained, now, write

MODELS = {
    "qwen2.5-1.5b": dict(name="Qwen2.5-1.5B-Instruct", quant="Q4_K_M", total=1.54, active=1.54, file="Qwen2.5-1.5B-Instruct-Q4_K_M.gguf", bytes=986048768),
    "qwen3-4b": dict(name="Qwen3-4B-Instruct-2507", quant="Q4_K_M", total=4.02, active=4.02, file="Qwen3-4B-Instruct-2507-Q4_K_M.gguf", bytes=2497281120),
    "qwen3-4b-b11010": dict(name="Qwen3-4B-Instruct-2507", quant="Q4_K_M", total=4.02, active=4.02, file="Qwen3-4B-Instruct-2507-Q4_K_M.gguf", bytes=2497281120),
    "ling-3.0-tiny": dict(name="Ling-3.0-tiny", quant="Q4_K_M", total=7.9, active=1.3, file="Ling-3.0-tiny-Q4_K_M.gguf", bytes=4823894944),
    "maple-preview": dict(name="Maple-Preview 20B-A1B", quant="TQ2_0-head-Q4_K", total=20.0, active=1.0, file="maple-preview-TQ2_0-head-Q4_K.gguf", bytes=5901782560),
}
ENGINES = {"bmoe/third_party/llama.cpp": "llama-server, llama.cpp 0e8c83e (2026-08-28, CPU build, GGML_METAL=OFF)",
           "llama-b11010": "llama-server, llama.cpp b11010 4bc272f (2026-09-16, CPU build, GGML_METAL=OFF)"}

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True, choices=sorted(MODELS))
ap.add_argument("--runs", required=True)
ap.add_argument("--mem-meta")
ap.add_argument("--question-set", default="kiln-exp01: v2-hard12 + lantern52 (64 items)")
ap.add_argument("--out", required=True)
a = ap.parse_args()

rows = [json.loads(l) for l in open(a.runs) if l.strip()]
meta = json.load(open(a.runs + ".meta.json"))
llm = [r for r in rows if r["route"] == "llm"]
M = MODELS[a.model]
engine = next((v for k, v in ENGINES.items() if k in meta["server"]), meta["server"])
server_args = meta.get("serverArgs") or []
cache_off = "--cache-ram" in server_args and server_args[server_args.index("--cache-ram") + 1] == "0"

per = []
for r in llm:
    per.append({"query_id": r["queryId"], "route": "llm", "context_tokens": r.get("promptN"),
                "ttft_model_ms": r["firstTokenMs"], "ttft_answer_ms": r["ttftMs"], "ttft_e2e_ms": None,
                "tps": mlperf_tps(r.get("predictedN"), r["firstTokenMs"], r["totalMs"]),
                "prefill_tps": round(r["prefillTokPerS"], 3) if r.get("prefillTokPerS") else None,
                "total_ms": r["totalMs"], "generated_tokens": r.get("predictedN"),
                "flagged": bool(r.get("contaminated"))})
col = lambda k: [p[k] for p in per]
reasoning = [r["ttftMs"] - r["firstTokenMs"] for r in llm]
has_reasoning = any(x > 50 for x in reasoning)

notes = ["PROXY: Mac mini M4 CPU with -t 4 stands in for a phone. Speeds are upper bounds, never ranked against device rows.",
         "cache_prompt=false: every answer pays the full prefill (the app reuses the fixed persona prefix on dense models).",
         f"Host 1-min load at request start: {min(r['loadStart'] for r in llm)}-{max(r['loadStart'] for r in llm)} (gate < 8, re-measure > 12; reruns: {sum(r.get('rerun', False) for r in llm)})."]
mem_src, mem_meta = "main run", meta
if a.mem_meta:
    mem_meta, mem_src = json.load(open(a.mem_meta)), "clean probe (--cache-ram 0, 6 longest v2 contexts, prompts <= 1,092 tokens)"
valid = cache_off or bool(a.mem_meta)
if not valid:
    notes.append("Memory INVALID: llama-server's host prompt cache (--cache-ram 8192 default) retained old prompt states.")

out = {
    "schema_version": SCHEMA_VERSION,
    "system": {"app": "BOAR harness (llama-server proxy of the app's answer step)", "app_version": None,
               "build": "boar-app 3bb0a3f (context builder) + eval runner feat/eval-frontier 0a024db", "apk_sha256": None,
               "model": {"name": M["name"], "file": M["file"], "sha256": meta["sha256"], "quant": M["quant"],
                         "params_total_b": M["total"], "params_active_b": M["active"], "file_bytes": M["bytes"]},
               "runtime": {"engine": engine, "backend": "cpu", "threads": meta["threads"], "n_ctx": 4096, "weight_repack": True,
                           "thinking": "always" if has_reasoning else "off", "sampling": meta["sampling"]}},
    "measurement": {"kind": "proxy", "method": "harness-llama-server", "date": meta["finishedAt"].replace(" ", "T") + "-03:00",
                    "operator": "Kiln (R&D)", "conditions": "Shared Mac mini, heavy queue, one job at a time", "notes": notes},
    "device": {"class": "desktop", "model": "Mac mini (M4)", "soc": "Apple M4", "cpu": "4P+6E, CPU only, 4 threads",
               "ram_bytes": 17179869184, "os": "macOS 26.6.2", "build_fingerprint": None},
    "workload": {"question_set": a.question_set, "question_set_sha256": None, "n_questions": len(rows), "n_llm_answers": len(llm),
                 "context_tokens": stat(col("context_tokens")),
                 "corpus": "--corpus essential + boar-crypto + boar-wikivoyage-en (app retrieval at 3bb0a3f)"},
    "latency": {"ttft_model_ms": stat(col("ttft_model_ms")), "ttft_answer_ms": stat(col("ttft_answer_ms")),
                "ttft_e2e_ms": stat([]), "includes_model_load": False, "tps": stat(col("tps")),
                "tps_engine_reported": stat([r.get("decodeTokPerS") for r in llm]), "prefill_tps": stat(col("prefill_tps")),
                "reasoning_ms": stat(reasoning) if has_reasoning else stat([]), "total_ms": stat(col("total_ms")),
                "total_scope": "model", "retrieval_ms": stat([]), "model_load_ms": round(meta["serverLoadS"] * 1000, 1),
                "empty_answers": sum(not r["answer"].strip() for r in llm)},
    "memory": {"peak_rss_bytes": mem_meta.get("peakRssSampledBytes"), "peak_anon_bytes": mem_meta.get("peakFootprintBytes"),
               "peak_pss_bytes": None, "method": f"ps rss sampled every 0.25 s + /usr/bin/time -l 'peak memory footprint'; {mem_src}",
               "valid": valid, "low_memory_kills": 0},
    "sustained": {"n_queries_in_session": len(llm), "session_minutes": None, **sustained(col("tps"), col("ttft_model_ms")),
                  "thermal_status_start": None, "thermal_status_end": None, "battery_temp_c_start": None,
                  "battery_temp_c_end": None, "battery_pct_drop": None},
    "offline_proof": {"status": "not-applicable", "tool": None, "report_sha256": None, "runtime_traffic": None},
    "per_query": per,
    "provenance": {"sources": [{"path": os.path.relpath(p, "<workspace>"), "sha256": sha256_file(p)}
                               for p in [a.runs, a.runs + ".meta.json"] + ([a.mem_meta] if a.mem_meta else [])],
                   "converter": "rnd/bench/device/from_kiln_harness.py", "generated_at": now()},
}
write(out, a.out)
L = out["latency"]
print(f"{a.model}: n={len(llm)} ttft_model p50 {L['ttft_model_ms']['p50']} ms, tps p50 {L['tps']['p50']}, "
      f"prefill p50 {L['prefill_tps']['p50']}, anon {out['memory']['peak_anon_bytes']} (valid={valid}) -> {a.out}")
