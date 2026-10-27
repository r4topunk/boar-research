#!/usr/bin/env python3
"""Per-item dossier for the 27 CE-taxonomy items (0 LLM): question, rubric, reference answer, and per arm K0/K1/K4 the kept titles
(with pack attribution as LITEPACKS agg.py), answer text, correctness (mean of both orders; K1/K4 reuse K0 rows for byte-identical answers)
and CE flag. Writes dossier.json next to the tools dir. Usage: python3 -I dossier.py [id ...] (prints a text view)."""
import json, glob, os, re, sys, sqlite3
A = "<workspace>/rnd/research/coordinator/arms"; LP = A + "/litepacks"; BE = "<workspace>/boar-eval/bench"
OUT = "/tmp/k1-coverage-dossier.json"  # local only: holds question+rubric+ref rows (pre-commit blind-text hook)
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
CE = rd(A + "/ce-taxonomy/ce-taxonomy.jsonl")
Q, R = {}, {}
for d in ["v0.1", "selftest/qa-cooking-se", "selftest/qa-money-se"]:
    qf = f"{BE}/{d}/questions.public.jsonl" if d == "v0.1" else f"{BE}/{d}/questions.jsonl"
    for q in rd(qf): Q[q["id"]] = q
    for r in rd(f"{BE}/{d}/refs/refs.jsonl"): R[r["id"]] = r.get("answer")
CRYPTO = {r[0].lower() for r in sqlite3.connect("file:<workspace>/shared-data/crypto/boar-crypto.sqlite?mode=ro", uri=True).execute("select title from articles")}
DOM = {"en.wikivoyage.org": "wikivoyage", "simple.wikipedia.org": "simplewiki", "ethereum.org": "crypto", "eips.ethereum.org": "crypto", "ercs.ethereum.org": "crypto"}
def pack_of(k, arm):
    m = re.match(r"^.*? — https?://([^/]+)", k.get("source") or "")
    if not m: return "other"
    d = m.group(1)
    if d in DOM: return DOM[d]
    if d == "en.wikipedia.org": return "crypto" if (arm != "K4" or (k.get("title") or "").lower() in CRYPTO) else "top100k"
    return "other:" + d
def traces(arm):
    out = {}
    for f in glob.glob(f"{LP}/traces/lp-{arm}-*-s42.traces.jsonl"):
        if "smoke" in f: continue
        for t in rd(f): out[t["itemId"]] = t
    return out
def judg(arm):
    by = {}
    for f in glob.glob(f"{LP}/judgments/lp-{arm}-*.judgments.jsonl"):
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r
    return {q: dict(corr=sum(r["mapped"]["boar"]["correctness"] for r in v.values()) / 2, rat=[r["verdict"]["rationale"] for r in v.values()])
            for q, v in by.items() if len(v) == 2}
TR = {a: traces(a) for a in ["K0", "K1", "K4"]}; JJ = {a: judg(a) for a in ["K0", "K1", "K4"]}
out = []
for c in CE:
    i = c["id"]; q = Q[i]; e = dict(id=i, question=q["question"], rubric=q.get("rubric"), notes={k: q[k] for k in ("selftest", "notes", "author_notes") if k in q},
                                   ref=R.get(i), ce_label=c, arms={})
    for a in ["K0", "K1", "K4"]:
        t = TR[a][i]; same = a != "K0" and t["answer"]["text"] == TR["K0"][i]["answer"]["text"]
        j = JJ["K0"][i] if (a == "K0" or same) else JJ[a].get(i)
        e["arms"][a] = dict(kept=[(k["title"], pack_of(k, a)) for k in t["retrieval"]["kept"]], raw=[(k["title"], pack_of(k, a)) for k in t["retrieval"]["raw"]],
                            answer=t["answer"]["text"], declined=t["answer"].get("declined"), same_as_K0=same,
                            corr=j["corr"] if j else None, ce=(j["corr"] <= 1.5 and not t["answer"].get("declined")) if j else None, rationale=j["rat"] if j else None)
    out.append(e)
json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
for e in out:
    if len(sys.argv) > 1 and e["id"] not in sys.argv[1:]: continue
    print(f"\n######## {e['id']} [{e['ce_label']['had_relevant_source']}/{e['ce_label']['error_kind']}] {e['question']}")
    print("RUBRIC:", json.dumps(e["rubric"], ensure_ascii=False)[:900])
    if e["notes"]: print("NOTES:", json.dumps(e["notes"], ensure_ascii=False)[:700])
    print("REF:", (e["ref"] or "")[:700].replace("\n", " "))
    for a, v in e["arms"].items():
        print(f"  {a} corr={v['corr']} ce={v['ce']} same={v['same_as_K0']} kept={v['kept']}")
        print(f"     raw={v['raw']}")
        print(f"     ANS: {v['answer'][:400]!r}")
        if a != "K0" and not v["same_as_K0"] and v["rationale"]: print(f"     WHY: {v['rationale'][0][:300]}")
