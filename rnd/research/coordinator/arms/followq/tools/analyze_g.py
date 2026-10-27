#!/usr/bin/env python3
"""analyze_g.py <runs dir>: FOLLOWQ-G G2 (identity) + G4 (retrieval latency) from ctl/arm traces; prints markdown."""
import json, sys, statistics as st
D = sys.argv[1]
def load(n): return {json.loads(l)["itemId"]: json.loads(l) for l in open(f"{D}/{n}.traces.jsonl")}
def key(t):
    r = t["retrieval"]
    return (t["answer"]["text"], t["route"]["tier"], [(s["title"], s["section"]) for s in r["kept"]])
def rkey(t):
    r = t["retrieval"]
    return ([(s["title"], s["section"]) for s in r["raw"]], [(s["title"], s["section"]) for s in r["kept"]])
c, a = load("ctl-v01-s44"), load("arm-v01-s44")
same = [i for i in c if i in a and key(c[i]) == key(a[i])]
fired = [i for i in a if "retrieve:followup-query" in a[i]["route"]["reasonCodes"]]
print(f"G2a v0.1 EN s44: identical text+tier+passages {len(same)}/{len(c)} (arm items {len(a)}); rule fired on {len(fired)} items; errors ctl {sum(bool(t['error']) for t in c.values())} arm {sum(bool(t['error']) for t in a.values())}")
for i in c:
    if i in a and key(c[i]) != key(a[i]): print("  DIFF", i, "text" if c[i]["answer"]["text"] != a[i]["answer"]["text"] else "", "tier" if c[i]["route"]["tier"] != a[i]["route"]["tier"] else "", "passages" if key(c[i])[2] != key(a[i])[2] else "")
c, a = load("ctl-chat"), load("arm-chat")
fl = [i for i in a if "retrieve:followup-query" in a[i]["route"]["reasonCodes"]]
non = [i for i in a if i not in fl]
diff = [i for i in non if rkey(c[i]) != rkey(a[i])]
print(f"G2b chat 192 (arm {len(a)}): flagged {len(fl)}: {fl}\n  non-flagged {len(non)}: retrieval (raw+kept) differs on {len(diff)} {diff}")
tdiff = [i for i in non if c[i]["answer"]["text"] != a[i]["answer"]["text"]]
print(f"  non-flagged answer text differs: {len(tdiff)} {tdiff} (informational: generation nondeterminism / seed)")
chg = [i for i in fl if c[i]["answer"]["text"].strip() != a[i]["answer"]["text"].strip()]
kchg = [i for i in fl if rkey(c[i])[1] != rkey(a[i])[1]]
print(f"  flagged: kept passages changed {len(kchg)} {kchg}; answer text changed {len(chg)} {chg}")
rc = [c[i]["timing"]["retrievalMs"] for i in fl if c[i]["timing"]["retrievalMs"] is not None]
ra = [a[i]["timing"]["retrievalMs"] for i in fl if a[i]["timing"]["retrievalMs"] is not None]
def ev_ms(t): return sum(e.get("ms", 0) for e in t["events"] if e["type"] == "retrieve")
ec = [ev_ms(c[i]) for i in fl]; ea = [ev_ms(a[i]) for i in fl]
print(f"G4 retrievalMs on {len(fl)} flagged: ctl mean {st.mean(rc):.1f} median {st.median(rc):.1f}; arm mean {st.mean(ra):.1f} median {st.median(ra):.1f}; ratio of means {st.mean(ra)/st.mean(rc):.2f}, of medians {st.median(ra)/st.median(rc):.2f}")
print(f"   retrieve-event ms: ctl mean {st.mean(ec):.1f}, arm mean {st.mean(ea):.1f}, ratio {st.mean(ea)/st.mean(ec):.2f}")
json.dump({"flagged": fl, "changed": chg}, open(f"{D}/g-sets.json", "w"))
