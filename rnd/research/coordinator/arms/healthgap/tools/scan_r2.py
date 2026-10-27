"""HEALTHGAP-r2 scan (0 LLM): runs tools/healthgap_scan_v12.py (rule v1.2 §1 normative source, sha256 44343ff8…) unchanged, then
classifies the r2 reviewer's 30 new probes (review/r2-probes.json) and the rule v1.2 §4 multi-turn goldens with the same functions,
and writes every input (304 + 35 review examples + 30 + §4) to a JSONL for the TS parity check (tools/parity_r2.mts).
Usage: python3 -I scan_r2.py <boar root> <out.json> <inputs.jsonl> [ts-out.jsonl]"""
import json, sys, io, contextlib
root, out_p, inp_p = sys.argv[1:4]; ts_p = sys.argv[4] if len(sys.argv) > 4 else None
H = f"{root}/rnd/research/coordinator/arms/healthgap"
g = {"__name__": "scan_v12"}; sys.argv = ["scan", root]; buf = io.StringIO()
with contextlib.redirect_stdout(buf): exec(compile(open(f"{H}/tools/healthgap_scan_v12.py").read(), "healthgap_scan_v12.py", "exec"), g)
out = g["out"]; classify = g["classify"]
def cls(c): return None if not c else ("poison-event" if c["event"] else c["cls"])
probes = json.load(open(f"{H}/review/r2-probes.json"))
rev = {json.loads(l)["id"]: json.loads(l) for l in open(f"{H}/review/r2-probes-fixed.jsonl") if l.strip()}
out["r2_probes"] = []
for pid, q, turns, exp, note in probes:
    c = classify(q, turns); got = cls(c)
    out["r2_probes"].append({"id": pid, "q": q, "turns": turns, "exp": exp, "got": got, "prev": bool(c and c["prev"]), "reviewer_fix_got": rev[pid]["got"], "meets_exp": got == exp, "note": note})
S4 = [("mt-calpol-more", "when can she have more?", ["I gave her Calpol at 9."], "dose"), ("mt-calpol-lisbon", "when can I visit Lisbon again?", ["I gave her Calpol at 9."], None),
      ("mt-ibu-kid", "and for a 30 kg kid?", ["How much ibuprofen can I take?"], "dose"), ("mt-nutmeg", "what about 2 g?", ["Is 5 g of nutmeg toxic?"], "poison"),
      ("mt-baggage", "and for a 30 kg kid?", ["What's the airline baggage limit?"], None),
      ("mt-es-para", "¿y para un niño de 20 kg?", ["¿Cuánto paracetamol puedo tomar?"], "dose")]
out["s4_multiturn"] = []
for sid, q, turns, exp in S4:
    c = classify(q, turns); out["s4_multiturn"].append({"id": sid, "q": q, "turns": turns, "exp": exp, "got": c and c["cls"], "prev": bool(c and c["prev"]), "ok": (c and c["cls"]) == exp})
rows = []
pub = g["pub"]; prb = g["probes"]
for i, q, s in pub: rows.append({"k": f"pub:{i}", "q": q, "turns": []})
for pid, r in prb.items(): rows.append({"k": f"q2:{pid}", "q": r["question"], "turns": r.get("turns", [])})
for n, (t, turns, exp) in enumerate(g["REVIEW"]): rows.append({"k": f"rev:{n}", "q": t, "turns": turns})
for p in out["r2_probes"]: rows.append({"k": f"r2:{p['id']}", "q": p["q"], "turns": p["turns"]})
for p in out["s4_multiturn"]: rows.append({"k": f"s4:{p['id']}", "q": p["q"], "turns": p["turns"]})
for r in rows:
    c = classify(r["q"], r["turns"]); r["py"] = None if not c else {"cls": c["cls"], "event": c["event"], "prev": c["prev"]}
open(inp_p, "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
if ts_p:
    ts = {json.loads(l)["k"]: json.loads(l)["ts"] for l in open(ts_p) if l.strip()}
    mism = [r["k"] for r in rows if r["py"] != ts.get(r["k"], "MISSING")]
    out["parity"] = {"n": len(rows), "mismatch": mism}
c = out["counts"]
c["r2_probes_meet_exp"] = sum(p["meets_exp"] for p in out["r2_probes"]); c["r2_probes_eq_reviewer_fix"] = sum(p["got"] == ((p["reviewer_fix_got"] or "").replace("+prev", "") or None) for p in out["r2_probes"])
c["s4_ok"] = sum(p["ok"] for p in out["s4_multiturn"]); c["s4_n"] = len(S4)
json.dump(out, open(out_p, "w"), indent=1, ensure_ascii=False)
print(buf.getvalue().split("\n")[0]); print(json.dumps({k: c[k] for k in ("r2_probes_meet_exp", "r2_probes_eq_reviewer_fix", "s4_ok", "s4_n")}))
for p in out["r2_probes"]: print(f'R2 {p["id"]} exp={p["exp"]} got={p["got"]} prev={int(p["prev"])} reviewer+fix={p["reviewer_fix_got"]}{"" if p["meets_exp"] else "  (exp miss)"}')
for p in out["s4_multiturn"]: print("S4", p)
if ts_p: print("PARITY", out["parity"]["n"], "mismatch", out["parity"]["mismatch"][:20])
