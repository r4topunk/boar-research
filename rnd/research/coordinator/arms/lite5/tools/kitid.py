#!/usr/bin/env python3
"""LITE5 stage 6 identity (script-only; counts only): ON kit traces vs LITE2 l-kit-v02-s42-slice traces: kept (title, section), promptTokens, headpass:* codes, errors."""
import json
B = "<private held-out dir>"
ld = lambda f: {(t := json.loads(l))["itemId"]: t for l in open(f) if l.strip()}
ON = ld(f"{B}/runs-lite5/lite5-on-kit-v02-s42-slice.traces.jsonl"); OFF = ld(f"{B}/runs-lite2/l-kit-v02-s42-slice.traces.jsonl")
kept = lambda t: [(s.get("title"), s.get("section")) for s in (t.get("retrieval") or {}).get("kept") or []]
pt = lambda t: (t.get("timing") or {}).get("promptTokens")
ids = sorted(ON); assert set(ids) == set(OFF) and len(ids) == 20
out = {"n": 20, "errors_on": sum(bool(ON[i].get("error")) for i in ids), "reasoning_tokens_on": sum((ON[i].get("timing") or {}).get("reasoningTokens") or 0 for i in ids),
       "kept_same": sum(kept(ON[i]) == kept(OFF[i]) for i in ids), "promptTokens_same": sum(pt(ON[i]) == pt(OFF[i]) for i in ids),
       "headpass_add_items": sum(any(c.startswith(("headpass:add:", "headpass:dense:add:")) for c in ON[i]["route"]["reasonCodes"]) for i in ids),
       "headpass_any_code_items": sum(any(c.startswith("headpass") for c in ON[i]["route"]["reasonCodes"]) for i in ids),
       "answer_same": sum(((ON[i].get("answer") or {}).get("text") or "").split() == ((OFF[i].get("answer") or {}).get("text") or "").split() for i in ids)}
json.dump(out, open("<workspace>/rnd/research/coordinator/arms/lite5/aggregates/kit-identity.json", "w"), indent=1); print(json.dumps(out))
