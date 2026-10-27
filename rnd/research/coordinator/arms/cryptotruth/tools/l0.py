#!/usr/bin/env python3
"""l0.py <run dir>: G2 report. ctl-* vs arm-* traces: changed items, truth:* fires, changes outside fires, chat fires, probes."""
import json, sys
D = sys.argv[1]
ld = lambda p: {t["itemId"]: t for t in map(json.loads, open(p))}
codes = lambda t: t["route"]["reasonCodes"]
fires = lambda t: [c for c in codes(t) if c.startswith("truth:") and c != "truth:eip-card-none"]
def cmp(setname):
    c, a = ld(f"{D}/ctl-{setname}.traces.jsonl"), ld(f"{D}/arm-{setname}.traces.jsonl")
    changed = [i for i in a if i in c and a[i]["answer"]["text"] != c[i]["answer"]["text"]]
    fired = [i for i in a if fires(a[i])]
    return c, a, changed, fired
tot_out = 0
for s in ("v01-s44", "v01-s45"):
    c, a, changed, fired = cmp(s)
    out = [i for i in changed if i not in fired]
    tot_out += len(out)
    print(f"== {s}: items {len(a)}, text changed {len(changed)}, fired {len(fired)}, changed outside fires {len(out)} {out}; fired-but-same-text {[i for i in fired if i not in changed]}")
    print(f"   tier changes {[i for i in a if a[i]['route']['tier'] != c[i]['route']['tier']]}; errors ctl {sum(1 for t in c.values() if t.get('error'))} arm {sum(1 for t in a.values() if t.get('error'))}")
    for i in changed:
        print(f"  [{i}] {fires(a[i])}\n    Q: {a[i]['question']}\n    CTL: {c[i]['answer']['text'][:400]!r}\n    ARM: {a[i]['answer']['text'][:400]!r}")
print("changes outside fires, both seeds:", tot_out)
c, a, changed, fired = cmp("chat")
nonc = [i for i in fired]
print(f"== chat: {len(a)} messages, fires {len(fired)}, text changed {len(changed)}, changed outside fires {[i for i in changed if i not in fired]}")
for i in fired: print(f"  [{i}] {fires(a[i])} Q: {a[i]['question']!r}\n    CTL: {c[i]['answer']['text'][:300]!r}\n    ARM: {a[i]['answer']['text'][:300]!r}")
c, a, changed, fired = cmp("probes")
print(f"== probes: changed {len(changed)}, fired {len(fired)}")
for i in a:
    print(f"  [{i}] fires {fires(a[i])} {'eip-card-none' if 'truth:eip-card-none' in codes(a[i]) else ''}\n    Q: {a[i]['question']}\n    CTL: {c[i]['answer']['text'][:350]!r}\n    ARM: {a[i]['answer']['text'][:350]!r}")
