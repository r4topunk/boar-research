#!/usr/bin/env python3
"""reuse.py <traces> <judged.ids> <baseline run base | none> <out tojudge.ids> <out reused.jsonl>
A judged item whose answer text is byte-identical to the baseline run's (same seed) reuses the baseline's ok judgment rows (both orders),
tagged reusedFrom; every other judged item goes to tojudge.ids. 'none' -> everything is judged. Prints one summary line."""
import json, os, sys
tr, idf, base, out_ids, out_rows = sys.argv[1:6]
ids = [x for x in open(idf).read().split() if x]
T = {json.loads(l)["itemId"]: json.loads(l) for l in open(tr) if l.strip()}
txt = lambda t: ((t or {}).get("answer") or {}).get("text")
reuse, rows = [], []
if base != "none" and os.path.exists(base + ".traces.jsonl") and os.path.exists(base + ".judgments.jsonl"):
    B = {json.loads(l)["itemId"]: json.loads(l) for l in open(base + ".traces.jsonl") if l.strip()}
    J = [json.loads(l) for l in open(base + ".judgments.jsonl") if l.strip()]
    for i in ids:
        a, b = txt(T.get(i)), txt(B.get(i))
        jr = [r for r in J if r.get("queryId") == i and r.get("ok")]
        if a is not None and a == b and {r["order"] for r in jr} == {"boarA", "boarB"} and len(jr) == 2:
            reuse.append(i); rows += [dict(r, reusedFrom=os.path.basename(base)) for r in jr]
todo = [i for i in ids if i not in reuse]
open(out_ids, "w").write("".join(i + "\n" for i in todo))
open(out_rows, "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
print(f"reuse {os.path.basename(tr)}: identical-to-baseline {len(reuse)} ({','.join(reuse) or '-'}), to judge {len(todo)}")
