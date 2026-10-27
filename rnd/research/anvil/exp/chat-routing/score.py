import json, statistics as st
C = {r["id"]: r for r in map(json.loads, open("runs-C.jsonl"))}
def acc(rows, f):
    s = [r for r in rows if r["label"] == "SEARCH"]; a = [r for r in rows if r["label"] == "ANSWER"]
    rec = sum(f(r) == "SEARCH" for r in s); spec = sum(f(r) == "ANSWER" for r in a)
    return rec + spec, rec, len(s), spec, len(a)
def best_thr(rows, key):
    best = None
    for t in sorted({key(r) for r in rows} | {0.5}):
        n = sum((key(r) >= t) == (r["label"] == "SEARCH") for r in rows)
        if best is None or n > best[0]: best = (n, t)
    return best
for tag in ("q15", "q4b"):
    rows = [json.loads(l) for l in open(f"runs-{tag}.jsonl")]
    print(f"== {tag}")
    for name, f in [("C classify.ts", lambda r: C[r["id"]]["decision"]), ("A tool call", lambda r: r["A"]["decision"]),
                    ("B label gate @0.5", lambda r: r["B"]["decision"]),
                    ("A or B", lambda r: "SEARCH" if "SEARCH" in (r["A"]["decision"], r["B"]["decision"]) else "ANSWER")]:
        n, rec, ns, spec, na = acc(rows, f)
        print(f"{name:20s} {n}/30  search recall {rec}/{ns}  no-search right {spec}/{na}  wrong={[r['id'] for r in rows if f(r)!=r['label']]}")
    print("B best thr", best_thr(rows, lambda r: r["B"]["score"]), " A-logit best thr", best_thr(rows, lambda r: r["A"]["pTool"]))
    calls = [r for r in rows if "<tool_call>" in r["A"]["text"]]
    print("A calls", len(calls), "format ok", sum(r["A"]["formatOk"] for r in calls), "plain-text call-like", sum(r["A"]["looksLikeCallInText"] for r in rows))
    for k in ("B", "A"):
        new = [r[k]["promptTokens"] - r[k]["staticPrefix"] for r in rows]
        print(f"{k}: prompt tokens p50 {st.median(r[k]['promptTokens'] for r in rows)}, static prefix {rows[0][k]['staticPrefix']}, new (uncached) p50 {st.median(new)} max {max(new)}; prefill ms p50 {st.median(r[k]['prefillMs'] for r in rows)}")
    print("A tool-call gen tokens p50", st.median([r["A"]["genTokens"] for r in calls]) if calls else None, "decode ms p50", st.median([r["A"]["decodeMs"] for r in calls]) if calls else None)
    print("queries:", [(r["id"], r["A"]["query"]) for r in calls])
