#!/usr/bin/env python3
"""BOAR in-app benchmark rows (eval-iphone / `npm run eval:iphone`, Plumb's runs) -> device-metrics JSON (kind=device).

Per answer that reached the model (receipt.tokens > 0; this includes drafts the citation gate later declined, because
the latency was spent):
  ttft_e2e_ms    = stages[generating].atMs              question sent -> first MODEL token (includes retrieval, routing)
  ttft_model_ms  = stages[generating].atMs - stages[prefill].atMs   prompt submitted to llama.rn -> first token (MLPerf)
  first_visible_ms (per_query only) = receipt.ttftMs: the app's own TTFT = first visible text of ANY tier, which is the
                   instant snippet when one is shown ('instant:preview'), i.e. it can precede the model entirely.
                   (Fixed 2026-09-30: using receipt.ttftMs as the model's first token gave ttft_model_ms = -2.3 ms.)
  tps            = null: MLPerf TPS needs the LAST-token timestamp, which the rows do not record; receipt.totalMs
                   also includes post-generation work (citation gate, attribution), so (tokens-1)/(totalMs-ttftMs)
                   underestimates TPS badly on short answers (checked 2026-09-30: 3.8 vs 12.5 tok/s)
  tps_engine_reported = receipt.tokPerSec (the app's own decode rate); the sustained block uses it
  prefill_tps    = receipt.ctxTokens / receipt.prefillMs. UPPER BOUND: llama.rn reuses the KV prefix, so fewer than
                   ctxTokens may be processed (and receipt.cachedTokens is known to be unreliable, 02-medicoes §6)
  context_tokens = receipt.ctxTokens; retrieval_ms = receipt.retrievalMs; total_ms = receipt.totalMs (scope e2e)
Not in the rows (null, with a note): peak memory, thermal state, OS version, offline proof. Pass them with flags when
measured separately.
Usage:
  python3 from_eval_iphone.py --rows <run.jsonl> --build 14de107 --question-set <id> --out <file.json>
      [--device-model "iPhone 13 (iPhone14,5)"] [--soc "Apple A15 Bionic"] [--ram-bytes 4294967296] [--os "iOS 26.6.2"]
      [--peak-anon-bytes N] [--thermal-start S] [--thermal-end S]
"""
import argparse, json, os
from bench_common import SCHEMA_VERSION, sha256_file, stat, sustained, now, write

ap = argparse.ArgumentParser()
ap.add_argument("--rows", required=True)
ap.add_argument("--build", required=True)
ap.add_argument("--question-set", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--device-model", default="iPhone 13 (iPhone14,5)")
ap.add_argument("--soc", default="Apple A15 Bionic")
ap.add_argument("--ram-bytes", type=int, default=4 * 1024 ** 3)
ap.add_argument("--os", default=None)
ap.add_argument("--corpus", default=None)
ap.add_argument("--peak-anon-bytes", type=int)
ap.add_argument("--thermal-start")
ap.add_argument("--thermal-end")
a = ap.parse_args()

rows = [json.loads(l) for l in open(a.rows) if l.strip()]
rows.sort(key=lambda r: r.get("createdAt") or 0)
llm = [r for r in rows if (r.get("receipt") or {}).get("tokens")]
model_ids = sorted({(r.get("receipt") or {}).get("modelId") for r in llm})
per = []
for r in llm:
    rc = r["receipt"]
    st = {s["stage"]: s["atMs"] for s in reversed(r.get("stages") or [])}  # first occurrence wins
    pre_at, gen_at = st.get("prefill"), st.get("generating")
    ttft_e2e, total = gen_at, rc.get("totalMs")
    per.append({"query_id": r["queryId"], "route": r.get("tier"), "context_tokens": rc.get("ctxTokens"),
                "ttft_model_ms": round(gen_at - pre_at, 1) if gen_at is not None and pre_at is not None else None,
                "first_visible_ms": round(rc["ttftMs"], 1) if rc.get("ttftMs") is not None else None,
                "ttft_answer_ms": None, "ttft_e2e_ms": round(ttft_e2e, 1) if ttft_e2e is not None else None,
                "tps": None,
                "tps_app": rc.get("tokPerSec"),
                "prefill_tps": round(rc["ctxTokens"] / (rc["prefillMs"] / 1000), 3) if rc.get("ctxTokens") and rc.get("prefillMs") else None,
                "total_ms": round(total, 1) if total is not None else None, "generated_tokens": rc.get("tokens"),
                "flagged": bool(r.get("declined"))})
col = lambda k: [p[k] for p in per]
started = [r.get("createdAt") for r in rows if r.get("createdAt")]
notes = [f"Rows from BOAR's in-app benchmark on a physical {a.device_model}; model(s) {', '.join(model_ids)}.",
         "ttft_model_ms = stages[generating].atMs - stages[prefill].atMs; ttft_e2e_ms = stages[generating].atMs (first MODEL token). The app's receipt.ttftMs is the first visible text of any tier (often the instant snippet) and is kept per query as first_visible_ms. prefill_tps is an upper bound (KV prefix reuse).",
         "latency.tps (MLPerf) is null: the last-token time is not recorded. Use tps_engine_reported (app tokPerSec); sustained.* uses it too.",
         f"{sum(p['flagged'] for p in per)} of the {len(per)} timed answers were declined by the app after drafting (citation gate); their latency still counts.",
         "Peak memory, thermal state and OS version are not recorded in these rows" + (" (OS version taken from review/IPHONE-MODEL-AB-rc6.md)." if a.os else ".")]
out = {
    "schema_version": SCHEMA_VERSION,
    "system": {"app": "BOAR", "app_version": None, "build": a.build, "apk_sha256": None,
               "model": {"name": "Qwen2.5-1.5B-Instruct" if model_ids == ["qwen2.5-1.5b-instruct-q4km"] else ",".join(model_ids),
                         "file": "Qwen2.5-1.5B-Instruct-Q4_K_M.gguf" if model_ids == ["qwen2.5-1.5b-instruct-q4km"] else None,
                         "sha256": "1adf0b11065d8ad2e8123ea110d1ec956dab4ab038eab665614adba04b6c3370" if model_ids == ["qwen2.5-1.5b-instruct-q4km"] else None,
                         "quant": "Q4_K_M", "params_total_b": 1.54, "params_active_b": 1.54, "file_bytes": 986048768},
               "runtime": {"engine": "llama.rn 0.13.0-rc.4 (llama.cpp b11010)", "backend": "cpu (Metal off)", "threads": None,
                           "n_ctx": None, "weight_repack": True, "thinking": "off",
                           "sampling": {"temperature": 0.7, "note": "app defaults (LlamaEngine.ts)"}}},
    "measurement": {"kind": "device", "method": "in-app-benchmark",
                    "date": None, "operator": "Plumb (R&D)", "conditions": (rows[0].get("answerSettings") and f"answerSettings={json.dumps(rows[0]['answerSettings'])}") or None,
                    "notes": notes},
    "device": {"class": "phone", "model": a.device_model, "soc": a.soc, "cpu": "6-core (2P+4E)", "ram_bytes": a.ram_bytes,
               "os": a.os, "build_fingerprint": None},
    "workload": {"question_set": a.question_set, "question_set_sha256": None, "n_questions": len(rows), "n_llm_answers": len(llm),
                 "context_tokens": stat(col("context_tokens")), "corpus": a.corpus},
    "latency": {"ttft_model_ms": stat(col("ttft_model_ms")), "ttft_answer_ms": stat([]), "ttft_e2e_ms": stat(col("ttft_e2e_ms")),
                "includes_model_load": False, "tps": stat(col("tps")),
                "tps_engine_reported": stat([r["receipt"].get("tokPerSec") for r in llm]), "prefill_tps": stat(col("prefill_tps")),
                "reasoning_ms": stat([]), "total_ms": stat(col("total_ms")), "total_scope": "e2e",
                "retrieval_ms": stat([r.get("receipt", {}).get("retrievalMs") for r in rows]),
                "model_load_ms": max([r["receipt"].get("loadMs") or 0 for r in llm] or [0]) or None,
                "empty_answers": sum(1 for r in llm if not (r.get("answer") or "").strip())},
    "memory": {"peak_rss_bytes": None, "peak_anon_bytes": a.peak_anon_bytes, "peak_pss_bytes": None,
               "method": "not recorded by the in-app benchmark rows" if a.peak_anon_bytes is None else "passed in (--peak-anon-bytes)",
               "valid": None, "low_memory_kills": None},
    "sustained": {"n_queries_in_session": len(rows),
                  "session_minutes": round((max(started) - min(started)) / 60000, 1) if len(started) > 1 else None,
                  **sustained(col("tps_app"), col("ttft_e2e_ms")),
                  "thermal_status_start": a.thermal_start, "thermal_status_end": a.thermal_end,
                  "battery_temp_c_start": None, "battery_temp_c_end": None, "battery_pct_drop": None},
    "offline_proof": {"status": "not-run", "tool": None, "report_sha256": None, "runtime_traffic": None},
    "per_query": per,
    "provenance": {"sources": [{"path": os.path.relpath(a.rows, "<workspace>"), "sha256": sha256_file(a.rows)}],
                   "converter": "rnd/bench/device/from_eval_iphone.py", "generated_at": now()},
}
write(out, a.out)
L = out["latency"]
print(f"{os.path.basename(a.rows)}: n_llm={len(llm)}/{len(rows)} ttft_e2e p50 {L['ttft_e2e_ms']['p50']} ms, ttft_model p50 "
      f"{L['ttft_model_ms']['p50']} ms, tps p50 {L['tps']['p50']}, ctx p50 {out['workload']['context_tokens']['p50']} -> {a.out}")
