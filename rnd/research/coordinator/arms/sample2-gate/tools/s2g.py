#!/usr/bin/env python3
"""SAMPLE2-GATE (0 LLM). Two steps.
  python3 -I s2g.py inputs <out gate inputs.jsonl> <out items.json>
      For every stage1-pool id: S42 = the mini K0 control answer (seed 42; traces lp-screens lpctl-K0-main-s42 + null-cal poolctl-K0-st180-s42),
      S43 = traces/s2g-K0-stage1-pool-s43dump (seed 43, same request). Context = the system message text after "\\n\\nContext:\\n" of the
      item's last dumped generate prompt of the S43 run; it stands for S42's context iff the S43 retrieval.kept list equals the control's
      (title, section, source). ELIGIBLE = texts differ, both are LLM answers (timing.outputTokens > 0), neither is a decline
      (null-cal/tools/labels.py is_decline), kept parity, context present. Gate rows (keys <id>|s42, <id>|s43) use gate17 render();
      response = answer minus the warning first line (as gate17/RU).
  python3 -I s2g.py select <gate outputs.jsonl> <items.json> <out composite traces.jsonl> <out selection.json>
      Per eligible item: keep S43 iff round(P_FAIL(S43), 4) < round(P_FAIL(S42), 4); else S42 (ties keep seed 42). Not eligible -> S42.
      Composite traces = the control trace rows with the selected S43 rows swapped in (so only S43 picks differ from the control)."""
import json, re, sys, importlib.util
A = "<workspace>/rnd/research/coordinator/arms"; D = f"{A}/sample2-gate"
def load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
g17 = load("g17", f"{A}/gate17/tools/build_items.py"); lab = load("lab", f"{A}/null-cal/tools/labels.py")
W = g17.WARN
IDS = [x for x in open(f"{A}/../ruler/ids/stage1-pool.ids").read().split() if x]
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
kk = lambda t: [(k.get("title"), k.get("section"), k.get("source")) for k in t["retrieval"]["kept"]]
resp = lambda txt: (txt[len(W) + 1:] if txt.startswith(W + "\n") else txt).strip()

def control():
    C = {}
    for f in (f"{A}/lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl", f"{A}/null-cal/control/traces/poolctl-K0-st180-s42.traces.jsonl"):
        for t in rd(f): C[t["itemId"]] = t
    return C

def inputs(out, itemsf):
    C = control(); S = {t["itemId"]: t for t in rd(f"{D}/traces/s2g-K0-stage1-pool-s43dump.traces.jsonl")}
    PR = {}
    for p in rd(f"{D}/traces/s2g-K0-stage1-pool-s43dump.prompts.jsonl"): PR.setdefault(p["itemId"], []).append(p)
    rows, items = [], []
    for i in IDS:
        a, b = C[i], S[i]; ta, tb = a["answer"]["text"], b["answer"]["text"]
        ps = [p for p in PR.get(i, []) if p.get("messages")]
        sysm = ps[-1]["messages"][0]["content"] if ps else ""
        ctx = sysm.split("\n\nContext:\n", 1)[1] if "\n\nContext:\n" in sysm else None
        llm = lambda t: (t["timing"].get("outputTokens") or 0) > 0
        dec = lambda t: lab.is_decline(t["answer"]["text"], t["answer"].get("declined"))
        x = dict(id=i, differ=ta != tb, llm42=llm(a), llm43=llm(b), dec42=dec(a), dec43=dec(b), kept_parity=kk(a) == kk(b), ctx=ctx is not None,
                 out42=a["timing"].get("outputTokens") or 0, out43=b["timing"].get("outputTokens") or 0,
                 prompt42=a["timing"].get("promptTokens"), prompt43=b["timing"].get("promptTokens"))
        x["eligible"] = x["differ"] and x["llm42"] and x["llm43"] and not x["dec42"] and not x["dec43"] and x["kept_parity"] and x["ctx"]
        items.append(x)
        if x["eligible"]:
            rows.append({"key": f"{i}|s42", "prompt": g17.render(a["question"], ctx, resp(ta))})
            rows.append({"key": f"{i}|s43", "prompt": g17.render(b["question"], ctx, resp(tb))})
    with open(out, "w") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump(items, open(itemsf, "w"), indent=0)
    n = lambda k: sum(1 for x in items if x[k])
    print(f"items {len(items)} differ {n('differ')} kept_parity {n('kept_parity')} ctx {n('ctx')} eligible {n('eligible')} gate rows {len(rows)}")

def select(gout, itemsf, outtr, outsel):
    C = control(); S = {t["itemId"]: t for t in rd(f"{D}/traces/s2g-K0-stage1-pool-s43dump.traces.jsonl")}
    G = {r["key"]: r for r in rd(gout)}; items = json.load(open(itemsf)); sel = {}
    for x in items:
        i = x["id"]
        if x["eligible"]:
            p42, p43 = G[f"{i}|s42"]["P_FAIL"], G[f"{i}|s43"]["P_FAIL"]
            pick = "s43" if round(p43, 4) < round(p42, 4) else "s42"
            sel[i] = dict(pick=pick, p42=p42, p43=p43)
        else: sel[i] = dict(pick="s42")
    with open(outtr, "w") as f:
        for i in IDS: f.write(json.dumps(S[i] if sel[i]["pick"] == "s43" else C[i], ensure_ascii=False) + "\n")
    json.dump(sel, open(outsel, "w"), indent=0)
    e = [v for v in sel.values() if "p42" in v]
    print(f"eligible {len(e)} picked s43 {sum(v['pick'] == 's43' for v in sel.values())} ties {sum(round(v['p42'],4) == round(v['p43'],4) for v in e)}")

if __name__ == "__main__":
    {"inputs": lambda: inputs(*sys.argv[2:4]), "select": lambda: select(*sys.argv[2:6])}[sys.argv[1]]()
