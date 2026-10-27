#!/usr/bin/env python3
"""LITELAT stage breakdown from one BOAR Bench run (rows.jsonl + bench.json timeline from the litelat build).

usage: analyze.py <results dir> [--json out.json] [--detail]
Per question: route tier, TTFT/total from the row, and the measured spans (ms):
  pre      = question start -> "retrieving" stage (detector, routing, telemetry read)
  detector = deviceEmergencyScore wall (mmBERT detector)
  retrieve = retrieve() wall (retrieveTap); inside it: embed (query embedding, native), corpusFts / corpusDense
             (main DB SQL incl. row transfer), wikipacks (searchWikiPacks wall), packSqlN / packSqlMs (pack SQL calls,
             serial sum), titleSql (title + redirect lookups inside it), f1packs (searchPacks wall)
  post     = end of retrieve -> prefill stage (compression, grounding, model select, route gate) minus load
  load     = llm-init + loadSession (model load / KV prefix restore)
  gate     = completions without a callback (route gate / prefix warm), wall
  prefill  = llama.cpp prompt_ms of the answer completion (promptN tokens, cacheN cached)
  ttftGap  = prefill stage -> first token, minus prefill (sampling of token 1, JS)
  decode   = predicted_ms; tokS = predicted tokens/s
"""
import json, statistics, sys
from pathlib import Path


def load(d: Path):
    rows = [json.loads(l) for l in (d / "rows.jsonl").read_text().splitlines() if l.strip()]
    bench = json.loads((d / "bench.json").read_text())
    tl = [q for q in bench.get("timeline", []) if q.get("query") != "(before first question)"]
    return rows, bench, tl


def per_question(row, q):
    it = q["items"] if q else []
    spans = [i for i in it if i.get("kind") == "span"]
    ev = [i for i in it if i.get("kind") == "event" and i.get("type") == "stage"]
    stage_at = {}
    for e in ev:
        stage_at.setdefault(e["stage"], e.get("at", e["t"]))
    ret = [i for i in it if i.get("kind") == "retrieve"]
    s = lambda name, pred=lambda i: True: sum(i["ms"] for i in spans if i["name"] == name and pred(i))
    sql = [i for i in spans if i["name"] == "sql"]
    pack_sql = [i for i in sql if not i.get("label", "").startswith("aoair_knowledge.db")]
    title_sql = [i for i in pack_sql if "FROM articles WHERE title" in i.get("label", "") or "FROM redirects" in i.get("label", "")]
    comps = [i for i in spans if i["name"] == "llm-completion"]
    nocb = [i for i in spans if i["name"] == "llm-completion-nocb"]
    rc = row.get("receipt", {})
    out = {
        "id": row["queryId"], "tier": row["tier"], "model": rc.get("modelId"),
        "ttft": round(row.get("ttftMs") or 0), "total": round(row.get("totalLatencyMs") or 0),
        "tokens": row.get("tokensGenerated"), "tokS": round(row.get("tokPerSec") or 0, 2),
        "retrievalMs_receipt": round(rc.get("retrievalMs") or 0),
        "pre": round(stage_at.get("retrieving", 0)),
        "detector": round(s("detector", lambda i: "p" in (i.get("extra") or {}))),
        "detectorInit": round(s("detector-init")),
        "knowledgeReady": round(s("knowledge-ready")),
        "retrieve": round(sum(r["ms"] for r in ret)),
        "nRetrieve": len(ret),
        "embed": round(s("embed")),
        "corpusFts": round(sum(i["ms"] for i in sql if i.get("label", "").startswith("aoair_knowledge.db|fts"))),
        "corpusDense": round(sum(i["ms"] for i in sql if i.get("label", "").startswith("aoair_knowledge.db|dense"))),
        "wikipacks": round(s("search-wikipacks")),
        "f1packs": round(s("search-packs-f1")),
        "packSqlN": len(pack_sql), "packSqlMs": round(sum(i["ms"] for i in pack_sql)),
        "titleSqlN": len(title_sql), "titleSqlMs": round(sum(i["ms"] for i in title_sql)),
        "llmInit": round(s("llm-init")), "loadSession": round(s("llm-loadSession")), "saveSession": round(s("llm-saveSession")),
        "gateN": len(nocb), "gate": round(sum(i["ms"] for i in nocb)),
        "gatePrefill": round(sum((i.get("extra") or {}).get("promptMs") or 0 for i in nocb)),
        "prefill": round(sum((i.get("extra") or {}).get("promptMs") or 0 for i in comps)),
        "promptN": sum((i.get("extra") or {}).get("promptN") or 0 for i in comps),
        "cacheN": sum((i.get("extra") or {}).get("cacheN") or 0 for i in comps),
        "decode": round(sum((i.get("extra") or {}).get("predictedMs") or 0 for i in comps)),
        "firstTokenAt": q.get("firstTokenAt") if q else None,
        "prefillStageAt": round(stage_at["prefill"]) if "prefill" in stage_at else None,
        "loadStageAt": round(stage_at["loading_model"]) if "loading_model" in stage_at else None,
    }
    if ret:
        rs = stage_at.get("retrieving", 0)
        end = max(r["t"] for r in ret)
        start_llm = out["loadStageAt"] if out["loadStageAt"] is not None else out["prefillStageAt"]
        out["post"] = round(start_llm - end) if start_llm is not None else None
        out["retrieveOverhead"] = round(end - rs - out["retrieve"])  # knowledge-ready wait etc.
    if out["prefillStageAt"] is not None and out["firstTokenAt"] is not None:
        out["ttftGap"] = round(out["firstTokenAt"] - out["prefillStageAt"] - out["prefill"])
        out["loadPhase"] = round(out["prefillStageAt"] - out["loadStageAt"]) if out["loadStageAt"] is not None else 0
    return out


def summarize(per):
    keys = ["ttft", "total", "pre", "detector", "retrieve", "embed", "corpusFts", "corpusDense", "wikipacks", "packSqlN", "packSqlMs",
            "titleSqlN", "titleSqlMs", "post", "loadPhase", "gate", "prefill", "promptN", "ttftGap", "decode", "tokS", "tokens"]
    groups = {"fast-model": [p for p in per if p["model"] and p["model"].startswith("qwen")],
              "retrieval-card": [p for p in per if not (p["model"] or "").startswith("qwen") and p["nRetrieve"]]}
    out = {}
    for g, ps in groups.items():
        out[g] = {"n": len(ps)}
        for k in keys:
            v = [p[k] for p in ps if p.get(k) is not None]
            if v:
                out[g][k] = round(statistics.median(v), 1)
    return out


def main():
    d = Path(sys.argv[1])
    rows, bench, tl = load(d)
    per = [per_question(r, tl[i] if i < len(tl) else None) for i, r in enumerate(rows)]
    summ = summarize(per)
    if "--detail" in sys.argv:
        cols = ["id", "tier", "ttft", "total", "pre", "detector", "retrieve", "embed", "corpusDense", "wikipacks", "packSqlN", "packSqlMs", "titleSqlN",
                "titleSqlMs", "post", "loadPhase", "gate", "prefill", "promptN", "cacheN", "ttftGap", "decode", "tokens", "tokS"]
        print("\t".join(cols))
        for p in per:
            print("\t".join(str(p.get(c, "")) for c in cols))
    print(json.dumps(summ, indent=1))
    print("inits:", [(i.get("applied", {}).get("role", "llm"), i["ms"], {k: v for k, v in i.get("applied", {}).items() if k not in ("model",)}) for i in bench.get("llamaInits", [])])
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps({"per": per, "summary": summ, "overrides": bench.get("engineOverrides")}, indent=1))


if __name__ == "__main__":
    main()
