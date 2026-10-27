"""Compare placed contexts (last sources event with text) between two kic trace files: identical text per item?"""
import json, sys
def ctx(f):
    out = {}
    for l in open(f):
        r = json.loads(l)
        ev = [e for e in r.get("events") or [] if e.get("type") == "sources" and any(x.get("text") for x in e.get("sources", []))]
        out[r["itemId"]] = [(x.get("title"), x.get("text")) for x in (ev[-1]["sources"] if ev else [])]
    return out
a, b = ctx(sys.argv[1]), ctx(sys.argv[2])
same = [i for i in a if i in b and a[i] == b[i]]; diff = [i for i in a if i in b and a[i] != b[i]]
print(f"items {len(a)}/{len(b)}; identical placed context {len(same)}; different {len(diff)}: {diff[:12]}")
