#!/usr/bin/env python3
"""GATELAT inputs (0 LLM). Usage: python3 -I build_inputs.py <out inputs.jsonl>
Per RU gated item (124): strings A (answer prompt + answer), V1, V2, V3 (see GATELAT-criterion.md), plus metadata.
Question / response / context exactly as RU build_items.py (MacBook K3 answer minus the warning line; mini-dumped context)."""
import json, re, sys, importlib.util
A = "<workspace>/rnd/research/coordinator/arms"
RU = f"{A}/refuse-unsupported"
sp = importlib.util.spec_from_file_location("g17", f"{A}/gate17/tools/build_items.py"); g17 = importlib.util.module_from_spec(sp); sp.loader.exec_module(g17)
W = g17.WARN
TAIL = ("\n\nThe CONTEXT is the numbered passages in the system message above, the QUESTION is the user message above, and the RESPONSE is "
        "the assistant reply above.\nAnswer with exactly one word: PASS or FAIL.")
GATE_TURN = "<|im_end|>\n<|im_start|>user\n" + g17.RUBRIC + TAIL + "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
INVOCATION = "<|im_start|>user\nYou are a groundedness guardrail"


def ans_prompt(system, user):
    return f"<|im_start|>system\n{system}<|im_end|>\n<|im_start|>user\n{user}<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"


def main():
    TR = {}
    for s in ("v01", "cm", "st"):
        for l in open(f"{A}/litepacks/traces/lp-K3-{s}-s42.traces.jsonl"):
            t = json.loads(l); TR[t["itemId"]] = t
    PR = {}
    for l in open(f"{RU}/traces/ru-K3-dump-s42.prompts.jsonl"):
        p = json.loads(l); PR.setdefault(p["itemId"], []).append(p)
    items = [x for x in json.load(open(f"{RU}/gate/items.json"))["items"] if x["gated"]]
    v0 = {json.loads(l)["key"]: json.loads(l) for l in open(f"{RU}/gate/boar.outputs.jsonl")}
    out = open(sys.argv[1], "w"); ncit = 0
    for x in items:
        i = x["key"]; t = TR[i]; txt = t["answer"]["text"]
        msgs = [p for p in PR[i] if p.get("messages")][-1]["messages"]
        assert [m["role"] for m in msgs] == ["system", "user"]
        system, user = msgs[0]["content"], msgs[1]["content"]
        instr, ctx = system.split("\n\nContext:\n", 1)
        resp = (txt[len(W) + 1:] if txt.startswith(W + "\n") else txt).strip()
        assert g17.render(t["question"], ctx, resp) == json.loads(next(l for l in open(f"{RU}/gate/ru.inputs.jsonl") if json.loads(l)["key"] == i))["prompt"]
        chunks = re.split(r"\n\n(?=\[\d+\] )", ctx)
        num = [int(re.match(r"\[(\d+)\] ", c).group(1)) for c in chunks]
        cited = {int(n) for n in re.findall(r"\[(\d+)\]", resp)} & set(num)
        keep = [c for c, n in zip(chunks, num) if n in cited] if cited else chunks[:2]
        ncit += bool(cited)
        tctx = "\n\n".join(keep)
        a = ans_prompt(system, user) + resp
        out.write(json.dumps({
            "key": i, "warned": x["warned"], "set": x["set"], "answer_prompt_tokens_trace": x["answer_prompt_tokens"],
            "n_chunks": len(chunks), "n_kept_trim": len(keep), "cited": sorted(cited), "ctx_chars": len(ctx), "tctx_chars": len(tctx),
            "A_prompt": ans_prompt(system, user), "A": a,
            "V1": a + GATE_TURN,
            "V2": g17.render(t["question"], tctx, resp),
            "V3": ans_prompt(instr + "\n\nContext:\n" + tctx, user) + resp + GATE_TURN,
            "V0_prompt_n": v0[i]["prompt_n"],
        }, ensure_ascii=False) + "\n")
    print(f"rows {len(items)} cited {ncit} invocation={INVOCATION!r}")


if __name__ == "__main__":
    main()
