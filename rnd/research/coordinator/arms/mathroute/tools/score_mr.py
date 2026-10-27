"""MATHROUTE deterministic scorer (0 LLM calls).
Usage: python3 -I score_mr.py <gold.jsonl> <out.json> <arm>=<traces.jsonl> [...]
Per item and arm:
  correct   = any number in answer.text within tol of any accept value, or any gold pattern matches (lenient, the primary metric)
  headline  = same test restricted to the first sentence (strict: the answer leads with the number)
  sentences = sentence count (split on . ! ? followed by whitespace/end, and on newlines; decimals and abbreviations kept)
  extra     = sentences > 2 (more than 'number + formula/one-line explanation')
  cited     = answer.cited non-empty OR a [n] marker in the text
  calc      = route.reasonCodes contains answer:calculator-* / answer:temperature-conversion (engine shortcut fired)
  task, retrieved (retrieval.raw non-empty), kept, totalMs."""
import json, re, sys, statistics as st
NUM = re.compile(r"(?<![\w.])([-−]?)(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?")
def nums(s):
    out = []
    for m in NUM.finditer(s):
        v = float(m.group(2).replace(",", "") + (m.group(3) or ""))
        out.append(-v if m.group(1) else v)
    return out
def hit(text, g):
    if any(re.search(p, text, re.I) for p in g["patterns"]): return True
    return any(abs(n - v) <= tol for n in nums(text) for v, tol in g["accept"])
SPLIT = re.compile(r"(?<!\be\.g)(?<!\bi\.e)(?<!\bapprox)(?<!\bvs)[.!?](?=\s|$)|\n+")
def sentences(t):
    return [s.strip() for s in SPLIT.split(t.replace("•", "\n")) if s and len(re.sub(r"[\W_]", "", s.strip())) >= 3]
def main():
    G = {g["id"]: g for g in map(json.loads, open(sys.argv[1]))}
    res = {"items": {}, "arms": {}}
    for spec in sys.argv[3:]:
        arm, path = spec.split("=", 1)
        rows = {}
        for l in open(path):
            if not l.strip(): continue
            t = json.loads(l); a = t.get("answer") or {}; txt = a.get("text") or ""
            rc = (t.get("route") or {}).get("reasonCodes") or []
            ss = sentences(txt)
            rows[t["itemId"]] = r = {
                "correct": bool(txt) and hit(txt, G[t["itemId"]]), "headline": bool(ss) and hit(ss[0], G[t["itemId"]]),
                "sentences": len(ss), "extra": len(ss) > 2, "cited": bool(a.get("cited")) or bool(re.search(r"\[\d+\]", txt)),
                "calc": any(c.startswith("answer:calculator-") or c == "answer:temperature-conversion" for c in rc),
                "task": (t.get("route") or {}).get("task"), "retrieved": bool((t.get("retrieval") or {}).get("raw")),
                "kept": len((t.get("retrieval") or {}).get("kept") or []), "declined": bool(a.get("declined")),
                "totalMs": (t.get("timing") or {}).get("totalMs"), "error": t.get("error"), "text": txt}
            res["items"].setdefault(t["itemId"], {})[arm] = r
        missing = sorted(set(G) - set(rows))
        n = len(G); L = [r["totalMs"] for r in rows.values() if r["totalMs"] is not None]
        M = [r["totalMs"] for i, r in rows.items() if r["totalMs"] is not None and not r["calc"]]
        res["arms"][arm] = {"n": n, "rows": len(rows), "missing": missing, "errors": sum(1 for r in rows.values() if r["error"]),
            "correct": sum(r["correct"] for r in rows.values()), "headline": sum(r["headline"] for r in rows.values()),
            "extra": sum(r["extra"] for r in rows.values()), "cited": sum(r["cited"] for r in rows.values()),
            "calc": sum(r["calc"] for r in rows.values()), "retrieved": sum(r["retrieved"] for r in rows.values()),
            "declined": sum(r["declined"] for r in rows.values()),
            "sentences_mean": round(st.mean(r["sentences"] for r in rows.values()), 2) if rows else None,
            "p50_ms": round(st.median(L)) if L else None, "p50_ms_model_only": round(st.median(M)) if M else None,
            "by_group": {}}
        for g in ("v01", "unit", "arith", "trap"):
            ids = [i for i in G if (i.startswith("vit") and g == "v01") or i.startswith({"unit": "mr-u", "arith": "mr-a", "trap": "mr-t"}.get(g, "@"))]
            res["arms"][arm]["by_group"][g] = f"{sum(rows[i]['correct'] for i in ids if i in rows)}/{len(ids)}"
    json.dump(res, open(sys.argv[2], "w"), indent=1, ensure_ascii=False)
    for arm, s in res["arms"].items():
        print(arm, {k: v for k, v in s.items() if k != "missing"}, "missing", s["missing"])
if __name__ == "__main__": main()
