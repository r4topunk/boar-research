#!/usr/bin/env python3
"""RU items + gate inputs (0 LLM). Usage: python3 -I build_items.py <out gate inputs.jsonl> <out items.json> <out label prep.json (outside the repo)>
Answers/labels = the MacBook LITEPACKS K3 traces (arms/litepacks/traces/lp-K3-{v01,cm,st}-s42) and their Haiku judgments (reused, never re-judged).
Context = the mini --dump-prompts regeneration (traces/ru-K3-dump-s42.*): the system message text after "\\n\\nContext:\\n" of the item's last
dumped generate prompt (what the 1.7B saw), valid only where the mini retrieval.kept list equals the MacBook one (title, section, source).
Gate scope ("source-present") = LLM answer (timing.outputTokens > 0), not a decline (reread.py definition), MacBook retrieval.kept non-empty,
mini kept identical, and a Context block present. Response = answer text with the warning first line removed (as gate17).
Gate prompt = arms/gate17/tools/build_items.py render() (card RUBRIC, Qwen3 template, thinking off), imported, not copied."""
import json, re, sys, importlib.util
A = "<workspace>/rnd/research/coordinator/arms"
D = f"{A}/refuse-unsupported"
sp = importlib.util.spec_from_file_location("g17", f"{A}/gate17/tools/build_items.py"); g17 = importlib.util.module_from_spec(sp); sp.loader.exec_module(g17)
W = g17.WARN
ENGINE_DECLINE = re.compile(
    r"I don't have a reliable offline source on this, so I won't give health advice from memory"
    r"|offline places pack is not installed"
    r"|I didn't find (this in this phone's library|safe first-aid instructions)"
    r"|^The offline source doesn't give first-aid steps for this\. In an emergency, call your local emergency number \(911 in the US, 112 in Europe\)\.$"
    r"|N(ã|a)o encontrei isso no acervo deste celular", re.I)
MODEL_DECLINE = re.compile(
    r"\b(i (do not|don't) know|i'?m not sure|i cannot answer|i can'?t answer|i don'?t have (enough |reliable )?information|not able to answer"
    r"|not enough information|(sources?|context|passages?) (do|does) not (contain|provide|mention)|unanswerable)\b", re.I)


def is_decline(t, declined):  # = arms/reread-2026-10-20/reread.py is_decline
    body = t[len(W):].strip() if t.startswith(W) else t
    return bool(declined) or bool(ENGINE_DECLINE.search(t)) or (len(body) < 300 and bool(MODEL_DECLINE.search(body))) or body == ""


kk = lambda t: [(k.get("title"), k.get("section"), k.get("source")) for k in t["retrieval"]["kept"]]


def main():
    TR = {}
    for s in ("v01", "cm", "st"):
        for l in open(f"{A}/litepacks/traces/lp-K3-{s}-s42.traces.jsonl"):
            t = json.loads(l); TR[t["itemId"]] = t
    MT = {json.loads(l)["itemId"]: json.loads(l) for l in open(f"{D}/traces/ru-K3-dump-s42.traces.jsonl")}
    PR = {}
    for l in open(f"{D}/traces/ru-K3-dump-s42.prompts.jsonl"):
        p = json.loads(l); PR.setdefault(p["itemId"], []).append(p)
    main_ids = [l.strip() for l in open(f"{A}/lp-screens/main-97.ids") if l.strip()]
    cand = sorted(i for i in TR if i.startswith("st-boar-"))
    items, rows, prep = [], [], []
    rep = {"mini_text_identical": 0, "mini_kept_identical": 0, "mini_prompt_tokens_equal": 0, "kept_mismatch_ids": [], "kept_but_no_context": []}
    for i in main_ids + cand:
        t, m = TR[i], MT[i]; txt = t["answer"]["text"]
        rep["mini_text_identical"] += m["answer"]["text"] == txt
        same_kept = kk(m) == kk(t); rep["mini_kept_identical"] += same_kept
        rep["mini_prompt_tokens_equal"] += m["timing"].get("promptTokens") == t["timing"].get("promptTokens")
        dec = is_decline(txt, t["answer"].get("declined")); warned = txt.startswith(W)
        llm = (t["timing"].get("outputTokens") or 0) > 0; kept = bool(t["retrieval"]["kept"])
        ps = [p for p in PR.get(i, []) if p.get("messages")]
        sysm = ps[-1]["messages"][0]["content"] if ps else ""
        ctx = sysm.split("\n\nContext:\n", 1)[1] if "\n\nContext:\n" in sysm else None
        if llm and not dec and kept and not same_kept: rep["kept_mismatch_ids"].append(i)
        if llm and not dec and kept and same_kept and ctx is None: rep["kept_but_no_context"].append(i)
        gated = llm and not dec and kept and same_kept and ctx is not None
        resp = txt[len(W) + 1:] if txt.startswith(W + "\n") else txt
        resp = resp.strip()
        x = {"key": i, "set": "MAIN" if i in main_ids else "CAND", "decline": dec, "warned": warned, "llm": llm, "kept": kept,
             "kept_same_mini": same_kept, "mini_text_same": m["answer"]["text"] == txt, "gated": gated,
             "answer_prompt_tokens": t["timing"].get("promptTokens"), "ctx_chars": len(ctx) if gated else None}
        items.append(x)
        if gated:
            rows.append({"key": i, "prompt": g17.render(t["question"], ctx, resp)})
            ch = re.split(r"\n\n(?=\[\d+\] )", ctx); strip = lambda c: re.sub(r"^\[\d+\] ", "", c)
            prep.append({"key": i, "warned": warned, "question": t["question"], "response": resp, "chunks": ctx,
                         "chunks_rev": "\n\n".join(f"[{k + 1}] {strip(c)}" for k, c in enumerate(reversed(ch))), "n": len(ch)})
    with open(sys.argv[1], "w") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"report": rep, "items": items}, open(sys.argv[2], "w"), indent=1, ensure_ascii=False)
    json.dump(prep, open(sys.argv[3], "w"))
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in rep.items()}))
    print(f"items {len(items)} gated {len(rows)} (unwarned {sum(1 for x in items if x['gated'] and not x['warned'])}, warned {sum(1 for x in items if x['gated'] and x['warned'])}); "
          f"mismatch {rep['kept_mismatch_ids']} no-ctx {rep['kept_but_no_context']}")


if __name__ == "__main__":
    main()
