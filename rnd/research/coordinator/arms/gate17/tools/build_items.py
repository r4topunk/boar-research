#!/usr/bin/env python3
"""GATE17 inputs (0 LLM). Usage:
  python3 -I build_items.py smoke <out inputs.jsonl>
  python3 -I build_items.py boar <out inputs.jsonl> <out items.json>
Card prompt (aaryand/qwen3-1.7b-context-adherence-guardrail @ daa91b0d, README "Usage"), rendered byte-for-byte:
  prompt = RUBRIC + "\\n\\n" + ("QUESTION: {q}\\n\\n" if q) + "CONTEXT:\\n{context[:24000]}\\n\\nRESPONSE:\\n{response}" + "\\nAnswer with exactly one word: PASS or FAIL."
  then the Qwen3 chat template, one user turn, add_generation_prompt, enable_thinking=False:
  "<|im_start|>user\\n{prompt}<|im_end|>\\n<|im_start|>assistant\\n<think>\\n\\n</think>\\n\\n"
BOAR rows (per GATE17-criterion.md): the dump re-runs of the mini controls lpctl-K0-main-s42 and lpctl-K1-screen-s42 (traces + --dump-prompts rows).
  - labels valid only where answer.text is byte-identical to the control (control aggregate 'text'); others excluded and listed.
  - in scope: retrieval.kept non-empty AND the item's last dumped generate prompt has a "\\n\\nContext:\\n" block in the system message.
  - question = trace.question (used in the prompt, not stored in items.json: rnd pre-commit hook); context = the system message text after "\\n\\nContext:\\n" (verbatim, "[n] Title\\ntext" blocks as the 1.7B saw them);
    response = answer.text with the engine's warning first line removed when it is exactly WARN.
  - K1-screen rows whose (id, context, response) equal a K0-MAIN row are dropped as duplicates."""
import json, sys

RUBRIC = """You are a groundedness guardrail for retrieval-augmented generation. \
Judge whether the RESPONSE is fully supported by the CONTEXT.

Rules:
- Verdict FAIL if the response makes at least one factual claim that is unsupported \
by or contradicts the context. Whether a claim is true in the real world is \
irrelevant: a claim absent from the context is still unsupported (FAIL).
- Verdict PASS otherwise. A response that declines to answer or says the context \
lacks the information is faithful (PASS)."""
WARN = "Not found in this phone's offline library. From the model's memory, may be wrong:"
A = "<workspace>/rnd/research/coordinator/arms"
RUNS = [("K0main", "lpctl-K0-main-s42", "gate17dump-K0-main-s42"), ("K1screen", "lpctl-K1-screen-s42", "gate17dump-K1-screen-s42")]


def render(question, context, response):
    body = (f"QUESTION: {question}\n\n" if question else "") + f"CONTEXT:\n{context[:24000]}\n\nRESPONSE:\n{response}"
    prompt = f"{RUBRIC}\n\n{body}\nAnswer with exactly one word: PASS or FAIL."
    return f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"


SMOKE = [  # the card's own example + two variants of it (grounded; decline)
    ("smoke-card-nobel", "Who wrote it?", "The report was written by Dr. Chen in 2019.", "Dr. Chen wrote it in 2019, and she also won a Nobel Prize.", "FAIL"),
    ("smoke-card-grounded", "Who wrote it?", "The report was written by Dr. Chen in 2019.", "Dr. Chen wrote it in 2019.", "PASS"),
    ("smoke-card-decline", "Who funded it?", "The report was written by Dr. Chen in 2019.", "The context does not say who funded the report.", "PASS"),
]


def main():
    mode, out = sys.argv[1], sys.argv[2]
    if mode == "smoke":
        with open(out, "w") as f:
            for k, q, c, r, exp in SMOKE:
                f.write(json.dumps({"key": k, "expected": exp, "prompt": render(q, c, r)}) + "\n")
        return
    items, rows, report = [], [], {"excluded_non_identical": {}, "out_of_scope_no_source": {}, "source_but_no_context_prompt": {},
                                    "dup_dropped": [], "warn_stripped": 0}
    seen = {}
    for tag, ctl, dump in RUNS:
        ag = json.load(open(f"{A}/lp-screens/control/aggregates/{ctl}.json"))["items"]
        prom = {}
        for l in open(f"{A}/gate17/traces/{dump}.prompts.jsonl"):
            p = json.loads(l); prom.setdefault(p["itemId"], []).append(p)
        ex, oos, nc = [], [], []
        for l in open(f"{A}/gate17/traces/{dump}.traces.jsonl"):
            t = json.loads(l); i = t["itemId"]; a = ag[i]; txt = t["answer"]["text"]
            if txt != a["text"]:
                ex.append(i); continue
            if not t["retrieval"]["kept"]:
                oos.append(i); continue
            ps = [p for p in prom.get(i, []) if p.get("messages")]
            sysm = ps[-1]["messages"][0]["content"] if ps else ""
            if "\n\nContext:\n" not in sysm:
                nc.append(i); continue
            ctx = sysm.split("\n\nContext:\n", 1)[1]
            resp = txt
            if resp.startswith(WARN + "\n"):
                resp = resp[len(WARN) + 1:]; report["warn_stripped"] += 1
            resp = resp.strip()
            if tag == "K1screen" and seen.get(i) == (ctx, resp):
                report["dup_dropped"].append(i); continue
            if tag == "K0main":
                seen[i] = (ctx, resp)
            key = f"{tag}:{i}"
            items.append({"key": key, "set": tag, "id": i, "CE": bool(a["CE"]), "corr": a["corr"], "warned": bool(a["warned"]),
                          "declined": bool(a["declined"]), "n_gens": len(ps), "ctx_chars": len(ctx),
                          "context": ctx, "response": resp})
            rows.append({"key": key, "prompt": render(t["question"], ctx, resp)})
        report["excluded_non_identical"][tag] = ex; report["out_of_scope_no_source"][tag] = oos; report["source_but_no_context_prompt"][tag] = nc
    with open(out, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"report": report, "items": items}, open(sys.argv[3], "w"), indent=1, ensure_ascii=False)
    print(json.dumps({k: ({kk: len(vv) for kk, vv in v.items()} if isinstance(v, dict) else (len(v) if isinstance(v, list) else v)) for k, v in report.items()}))
    print(f"in scope {len(items)} (K0main {sum(x['set'] == 'K0main' for x in items)}, K1screen {sum(x['set'] == 'K1screen' for x in items)}), "
          f"CE {sum(x['CE'] for x in items)}, corr>=4 {sum(x['corr'] >= 4 for x in items)}, corr<=2 {sum(x['corr'] <= 2 for x in items)}")


if __name__ == "__main__":
    main()
