#!/usr/bin/env python3
"""Context-assembly audit over the captured LITEPACKS prompts (0 LLM, 0 judge calls).
Usage: python3 -I analyze.py > ../context-analysis.json
Inputs: cap/<run>.prompts.jsonl + cap/<run>.traces.jsonl (stub capture, retrieval/context codes identical to LITEPACKS 100 %),
LITEPACKS traces (real promptTokens) and judgments (correctness), bench selftest in_pack_facts quotes."""
import json, re, glob, statistics as S, sys
C = "<workspace>/rnd/research/coordinator/research-2026-10-20/model-usage/context-tools/cap"
L = "<workspace>/rnd/research/coordinator/arms/litepacks"
BE = "<workspace>/boar-eval/bench/selftest"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
W = "Not found in this phone's offline library."

def judg(arm):
    by = {}
    for f in sorted(glob.glob(f"{L}/judgments/lp-{arm}-*.judgments.jsonl")):
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]["boar"]["correctness"]
    return {k: S.mean(v.values()) for k, v in by.items()}
J0 = judg("K0")
JA = {a: judg(a) for a in ("K0", "K1", "K3")}
ANS = {a: {t["itemId"]: t["answer"]["text"] for f in glob.glob(f"{L}/traces/lp-{a}-*-s42.traces.jsonl") if "smoke" not in f for t in rd(f)} for a in ("K0", "K1", "K3")}
def corr(arm, i):
    if i in JA[arm]: return JA[arm][i]
    if ANS[arm].get(i) == ANS["K0"].get(i): return J0.get(i)
    return None

def parse(msgs):
    sysm = msgs[0]["content"]
    if "\n\nContext:\n" not in sysm: return sysm, []
    head, ctx = sysm.split("\n\nContext:\n", 1)
    parts = re.split(r"\n\n(?=\[\d+\] )", ctx)
    out = []
    for p in parts:
        m = re.match(r"\[(\d+)\] (.*?)\n(.*)", p, re.S)
        out.append({"n": int(m.group(1)), "title": m.group(2), "body": m.group(3)})
    return head, out

norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[“”\"'’‘]", "", s)).strip().lower()
def frag(body):
    b = re.sub(r"^[A-Z][^:\n]{0,60}: ", "", body.strip())  # "Section: " prefix of pack chunks
    start_bad = bool(re.match(r"^[a-z,;)\]–\-]", b))
    end_bad = not re.search(r"[.!?:\"')\]»]\s*$", b)
    return start_bad, end_bad

TOK = {}
for f in glob.glob(f"{L}/traces/lp-*-s42.traces.jsonl"):
    for t in rd(f): TOK[(t["runId"], t["itemId"])] = t["timing"].get("promptTokens") or 0

res = {}
quotes = {}
for p in ("boar-simplewiki-en", "boar-factbook", "boar-medlineplus-en", "boar-firstaid-en"):
    for q in rd(f"{BE}/{p}/questions.jsonl"): quotes[q["id"]] = [x["quote"] for x in q["selftest"]["in_pack_facts"] if x.get("quote")]

for run in ["lp-K0-v01-s42", "lp-K0-cm-s42", "lp-K1-v01-s42", "lp-K1-cm-s42", "lp-K1-st-s42", "lp-K3-st-s42"]:
    arm = run.split("-")[1]
    tr = {t["itemId"]: t for t in rd(f"{C}/{run}.traces.jsonl")}
    rows = []
    for pr in rd(f"{C}/{run}.prompts.jsonl"):
        i = pr["itemId"]; t = tr[i]; rc = t["route"]["reasonCodes"]
        head, ch = parse(pr["messages"])
        n_app = sum(c.startswith(("headpass:add:", "headpass:dense:add:")) for c in rc)
        n_comp = len(ch) - n_app
        ngs = "grounding:no-good-source" in rc
        m = next((re.match(r"context:(\d+)->(\d+)", c) for c in rc if re.match(r"context:\d+->\d+", c)), None)
        fr = [frag(c["body"]) for c in ch]
        titles = [c["title"] for c in ch]
        r = {"id": i, "tok": TOK.get((run, i), 0), "sys_chars": len(head), "ctx_chars": sum(len(c["title"]) + len(c["body"]) for c in ch),
             "app_chars": sum(len(c["title"]) + len(c["body"]) for c in ch[n_comp:]) if n_app else 0,
             "n": len(ch), "n_comp": n_comp, "n_app": n_app, "ngs": ngs, "only_app": n_comp == 0 and n_app > 0,
             "before": int(m.group(1)) if m else None, "after": int(m.group(2)) if m else None,
             "frag_start": sum(a for a, _ in fr), "frag_end": sum(b for _, b in fr),
             "frag_start_comp": sum(a for a, _ in fr[:n_comp]), "frag_end_comp": sum(b for _, b in fr[:n_comp]),
             "frag_start_app": sum(a for a, _ in fr[n_comp:]), "frag_end_app": sum(b for _, b in fr[n_comp:]),
             "dup_title": len(titles) - len(set(titles)), "warned": ANS[arm].get(i, "").startswith(W), "corr": corr(arm, i)}
        if run.endswith("st-s42") and i in quotes:
            pos = []
            for q in quotes[i]:
                nq = norm(q); where = None; kind = "absent"
                for k, c in enumerate(ch):
                    nb = norm(c["body"])
                    if nq in nb: where, kind = k, "full"; break
                if where is None:
                    w = nq.split()
                    for k, c in enumerate(ch):
                        nb = norm(c["body"])
                        if len(w) >= 8 and (" ".join(w[:6]) in nb or " ".join(w[-6:]) in nb): where, kind = k, "partial"; break
                pos.append({"kind": kind, "pos": where, "of": len(ch), "origin": None if where is None else ("comp" if where < n_comp else "app")})
            r["quotes"] = pos
        rows.append(r)
    res[run] = rows

def summ(rows):
    tok = [r["tok"] for r in rows if r["tok"]]
    n = len(rows); ch = sum(r["n"] for r in rows); comp = sum(r["n_comp"] for r in rows); app = sum(r["n_app"] for r in rows)
    o = {"prompts": n, "promptTokens_mean": round(S.mean(tok)), "p50": S.median(tok), "p90": sorted(tok)[int(0.9 * len(tok))], "max": max(tok),
         "sys_chars_mean": round(S.mean(r["sys_chars"] for r in rows)), "ctx_chars_mean": round(S.mean(r["ctx_chars"] for r in rows)),
         "app_share_of_ctx_chars": round(sum(r["app_chars"] for r in rows) / max(1, sum(r["ctx_chars"] for r in rows)), 3),
         "chunks_mean": round(ch / n, 2), "chunks_comp": comp, "chunks_app": app,
         "prompts_with_app": sum(r["n_app"] > 0 for r in rows), "prompts_no_good_source_but_app": sum(r["ngs"] and r["n_app"] > 0 for r in rows),
         "prompts_only_app_chunks": sum(r["only_app"] for r in rows),
         "frag_start_comp": f'{sum(r["frag_start_comp"] for r in rows)}/{comp}', "frag_end_comp": f'{sum(r["frag_end_comp"] for r in rows)}/{comp}',
         "frag_start_app": f'{sum(r["frag_start_app"] for r in rows)}/{app}', "frag_end_app": f'{sum(r["frag_end_app"] for r in rows)}/{app}',
         "prompts_dup_title": sum(r["dup_title"] > 0 for r in rows)}
    oa = [r for r in rows if r["only_app"]]
    if oa:
        cs = [r["corr"] for r in oa if r["corr"] is not None]
        o["only_app_warned"] = sum(r["warned"] for r in oa)
        o["only_app_CE(<=1.5)"] = f'{sum(c <= 1.5 for c in cs)}/{len(cs)}'
        rest = [r["corr"] for r in rows if not r["only_app"] and r["corr"] is not None]
        o["only_app_corr_mean"] = round(S.mean(cs), 2) if cs else None; o["rest_corr_mean"] = round(S.mean(rest), 2) if rest else None
    qs = [q for r in rows for q in r.get("quotes", [])]
    if qs:
        o["quotes"] = len(qs)
        o["quote_full"] = sum(q["kind"] == "full" for q in qs); o["quote_partial"] = sum(q["kind"] == "partial" for q in qs); o["quote_absent"] = sum(q["kind"] == "absent" for q in qs)
        f = [q for q in qs if q["kind"] != "absent"]
        o["quote_in_comp"] = sum(q["origin"] == "comp" for q in f); o["quote_in_app"] = sum(q["origin"] == "app" for q in f)
        o["quote_at_pos1"] = sum(q["pos"] == 0 for q in f); o["quote_in_last_chunk"] = sum(q["pos"] == q["of"] - 1 and q["of"] > 1 for q in f)
        items = [r for r in rows if r.get("quotes")]
        o["items_with_quotes"] = len(items)
        o["items_any_quote_full"] = sum(any(q["kind"] == "full" for q in r["quotes"]) for r in items)
        o["items_all_quotes_absent"] = sum(all(q["kind"] == "absent" for q in r["quotes"]) for r in items)
        # correctness by where the first found quote sits
        by = {}
        for r in items:
            f1 = [q for q in r["quotes"] if q["kind"] != "absent"]
            key = "absent" if not f1 else ("pos1" if min(q["pos"] for q in f1) == 0 else "later") + "-" + f1[0]["origin"]
            if r["corr"] is not None: by.setdefault(key, []).append(r["corr"])
        o["corr_by_first_quote_slot"] = {k: [len(v), round(S.mean(v), 2)] for k, v in sorted(by.items())}
    return o

out = {run: summ(rows) for run, rows in res.items()}
main = {a: summ(res[f"lp-{a}-v01-s42"] + res[f"lp-{a}-cm-s42"]) for a in ("K0", "K1")}
out["MAIN-K0"] = main["K0"]; out["MAIN-K1"] = main["K1"]
st80 = {a: summ([r for r in res[f"lp-{a}-st-s42"] if r["id"] in quotes]) for a in ("K1", "K3")}
out["ST80-K1(pack-matched simplewiki only)"] = st80["K1"]; out["ST80-K3(all 4 packs matched)"] = st80["K3"]
json.dump(out, sys.stdout, indent=1)
json.dump(res, open(f"{C}/../rows.json", "w"))
