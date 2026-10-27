#!/usr/bin/env python3
"""analyze.py <traces.jsonl>: CHATGATE confusion matrix + G1-G3. Labels: dev chat slices v0/v1/v2 expected_search yes/no/either."""
import json, sys, re, statistics, collections
C = "<workspace>/rnd/research/compass/chat-slice"
lab = {}
for p in ("slice.v0.jsonl", "v1-fresh/slice.v1.jsonl", "v2-fresh/slice.v2.jsonl"):
    for l in open(f"{C}/{p}"):
        r = json.loads(l); lab[r["id"]] = (r["expected_search"], r["kind"], len(r["turns"]) - 1)
ts = [json.loads(l) for l in open(sys.argv[1])]
rows = []
for t in ts:
    rc = t["route"]["reasonCodes"]
    gate = [e for e in t["events"] if e.get("kind") == "route-gate"]
    if any(c == "route-gate:skip-rules" for c in rc): dec = "skip-rules"
    elif any(c == "route-gate:search" for c in rc): dec = "gate-SEARCH"
    elif any(c == "route-gate:answer" for c in rc): dec = "gate-CONVERSATION"
    elif any(c == "route-gate:unavailable" for c in rc): dec = "gate-unavailable"
    elif t["route"]["tier"] == "instant" and any(c.startswith("answer:") for c in rc): dec = "rules-no-gate"
    else: dec = "no-gate-other"
    ps = next((float(c.split("score-")[1]) for c in rc if c.startswith("route-gate:score-") and c.split("score-")[1] != "none"), None)
    r = t.get("retrieval") or {}
    kept = len(r.get("kept") or []); raw = len(r.get("raw") or [])
    titles = {x.get("title") for k in ("raw", "kept", "dropped") for x in (r.get(k) or []) if x.get("title")}
    text = t["answer"]["text"] or ""
    paste = [ti for ti in titles if len(ti) >= 4 and ti.lower() in text.lower()]
    tm = t.get("timing") or {}
    rows.append(dict(id=t["itemId"], exp=lab[t["itemId"]][0], kind=lab[t["itemId"]][1], hist=lab[t["itemId"]][2], dec=dec, p=ps, tier=t["route"]["tier"], task=t["route"]["task"],
                     used=kept > 0, retrieved=raw > 0, empty=not text.strip(), err=bool(t.get("error")), paste=bool(paste), toks=tm.get("outputTokens"), ms=tm.get("totalMs"),
                     det=[c for c in rc if c.startswith("detector:")], codes=[c for c in rc if c.startswith("answer:")]))
n = len(rows); print("traces", n, "(expected 192)")
for e in ("yes", "no", "either"):
    s = [r for r in rows if r["exp"] == e]
    print(f"expected {e}: {len(s)}  sources used {sum(r['used'] for r in s)}  retrieval ran {sum(r['retrieved'] for r in s)}  decisions {dict(collections.Counter(r['dec'] for r in s))}")
print("\nconfusion (rows = expected, cols = sources used):")
for e in ("yes", "no", "either"):
    s = [r for r in rows if r["exp"] == e]; print(f"  {e:7s} used {sum(r['used'] for r in s):3d}  not used {sum(not r['used'] for r in s):3d}")
yes = [r for r in rows if r["exp"] == "yes"]; no = [r for r in rows if r["exp"] == "no"]
miss = [r for r in yes if not r["used"]]; fs = [r for r in no if r["used"]]
print(f"\nG1 missed search {len(miss)}/{len(yes)} = {100*len(miss)/len(yes):.1f}% (bar <= 5%)  {'PASS' if len(miss)/len(yes) <= .05 else 'FAIL'}")
print(f"G2 false search  {len(fs)}/{len(no)} = {100*len(fs)/len(no):.1f}% (bar <= 15%) {'PASS' if len(fs)/len(no) <= .15 else 'FAIL'}")
emp = [r for r in rows if r["empty"]]; er = [r for r in rows if r["err"]]; pa = [r for r in no if r["paste"]]
print(f"G3 empty {len(emp)}, errors {len(er)}, expected-no answers containing a retrieved title {len(pa)}  {'PASS' if not (emp or er or pa) else 'FAIL'}")
print("\nfailing items (id, kind, history turns, decision, p(SEARCH), tier):")
for tag, L in (("G1 missed", miss), ("G2 false", fs), ("G3 empty", emp), ("G3 error", er), ("G3 paste", pa)):
    for r in L: print(f"  {tag}: {r['id']} {r['kind']} h{r['hist']} {r['dec']} p={r['p']} tier={r['tier']} task={r['task']}")
g = [r for r in rows if r["dec"].startswith("gate-")]
ps = [r["p"] for r in g if r["p"] is not None]
print(f"\ngate calls {len(g)}, p(SEARCH) range {min(ps):.3f}-{max(ps):.3f}" if ps else "\nno gate calls")
print("all decisions:", dict(collections.Counter(r["dec"] for r in rows)))
print("gate CONVERSATION by expected:", dict(collections.Counter(r["exp"] for r in rows if r["dec"] == "gate-CONVERSATION")))
tk = [r["toks"] for r in rows if r["toks"] is not None]; lt = [r["ms"] for r in rows if r["ms"] is not None]
print(f"answer tokens median {statistics.median(tk):.0f} max {max(tk)}; latency ms median {statistics.median(lt):.0f} p90 {sorted(lt)[int(.9*len(lt))]:.0f}")
json.dump(rows, open(sys.argv[1].replace(".traces.jsonl", ".rows.json"), "w"), ensure_ascii=False)
