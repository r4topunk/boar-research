#!/usr/bin/env python3
"""exp-07: T2 (expansion on a miss) off vs on, per profile, same tree (14de107 + patch), same seed.

Per profile:
- counts over the 54 vitalik58 questions: declined, weak_sources, declined AND weak_sources, 0 shown sources;
  the "0 sources (off)" subset separately (where T2 acts);
- T2 fired (expansion:* codes): hit / miss; extra latency = expansion:ms-N (and total-time delta for those ids);
- regressions: questions where T2 did NOT fire must be byte-identical off vs on (same seed, same code path);
  any difference is listed;
- outcome changes on fired questions, scored with the cheap bench pieces: Lantern's precheck v2.2 and Jev v2
  (exp-04 jev_label.py, frozen prompt; reference = Opus+web answers, rnd/plumb/data/claude-code__opus.jsonl).
Usage: python3 compare_t2.py runs/<profile>-off.jsonl runs/<profile>-on.jsonl <profile> [--jev] > out.md
"""
import json, os, re, statistics, subprocess, sys, tempfile

off_p, on_p, prof = sys.argv[1:4]
JEV = "--jev" in sys.argv
B = "<workspace>"
OFF = {r["id"]: r for r in map(json.loads, open(off_p))}
ON = {r["id"]: r for r in map(json.loads, open(on_p))}
ids = sorted(OFF)
xp = lambda r: [c for c in r["reasonCodes"] if c.startswith("expansion:")]
fired = [i for i in ids if xp(ON[i])]
hit = [i for i in fired if any(c.startswith("expansion:hit") for c in xp(ON[i]))]
ms = {i: int(next(c for c in xp(ON[i]) if c.startswith("expansion:ms-")).split("-")[-1]) for i in fired}


def counts(R, sel):
    rs = [R[i] for i in sel]
    return {"declined": sum(r["flags"]["declined"] for r in rs), "weak": sum(r["flags"]["weak_sources"] for r in rs),
            "declined_and_weak": sum(r["flags"]["declined"] and r["flags"]["weak_sources"] for r in rs),
            "zero_sources": sum(not r["shownSources"] for r in rs), "n": len(rs)}


zero_off = [i for i in ids if not OFF[i]["shownSources"]]
untouched = [i for i in ids if i not in fired]
regress = [i for i in untouched if OFF[i]["answer"] != ON[i]["answer"] or [s["title"] for s in OFF[i]["shownSources"]] != [s["title"] for s in ON[i]["shownSources"]]]

# precheck v2.2 on the fired rows (off vs on)
LT = f"{B}/rnd/lantern"


def precheck(rows):
    with tempfile.TemporaryDirectory() as d:
        f, sub, js = f"{d}/r.jsonl", f"{d}/s.json", f"{d}/o.json"
        with open(f, "w") as fh:
            for r in rows:
                fh.write(json.dumps({"queryId": r["id"], "answer": r["answer"], "declined": r["flags"]["declined"]}) + "\n")
        json.dump({"ids": [r["id"] for r in rows]}, open(sub, "w"))
        subprocess.run(["python3", f"{LT}/tools/precheck.py", f, "--subset", sub, "--json", js], cwd=LT, check=True, capture_output=True)
        return {x["id"]: x["status"] + ("/ok" if x["status"] == "refused" and x["why"] == "ok" else "") for x in json.load(open(js))}


pc_off = precheck([OFF[i] for i in fired]) if fired else {}
pc_on = precheck([ON[i] for i in fired]) if fired else {}
jv_off, jv_on = {}, {}
if JEV and fired:
    sys.path.insert(0, f"{B}/rnd/kiln/exp-04-jev")
    from jev_label import label_items
    refs = {r["id"]: r for r in map(json.loads, open(f"{B}/rnd/plumb/data/claude-code__opus.jsonl"))}
    qs = {q["id"]: q for q in map(json.loads, open(f"{LT}/handoff/questions.vitalik-lantern.jsonl"))}
    for tag, R, outd in (("off", OFF, jv_off), ("on", ON, jv_on)):
        items = [{"id": i, "question": R[i]["question"], "reference": refs[i]["answer"], "rubric": qs.get(i, {}).get("notes", ""),
                  "answer": R[i]["answer"], "retrieved_titles": [s["title"] for s in R[i]["shownSources"]]} for i in fired if i in refs]
        for o in label_items(items, budget_usd=0.05):
            outd[o["id"]] = o["label"]

co, cn = counts(OFF, ids), counts(ON, ids)
zo, zn = counts(OFF, zero_off), counts(ON, zero_off)
L = [f"## {prof}", "",
     "| over all 54 | T2 off | T2 on |", "|---|---:|---:|"]
for k in ("declined", "weak", "declined_and_weak", "zero_sources"):
    L.append(f"| {k} | {co[k]} | {cn[k]} |")
L += ["", f"| subset: 0 shown sources with T2 off (n={len(zero_off)}) | T2 off | T2 on |", "|---|---:|---:|"]
for k in ("declined", "weak", "declined_and_weak", "zero_sources"):
    L.append(f"| {k} | {zo[k]} | {zn[k]} |")
tot_delta = [ON[i]["receipt"]["totalMs"] - OFF[i]["receipt"]["totalMs"] for i in fired]
L += ["", f"- T2 fired on {len(fired)} questions; found sources on {len(hit)} (`expansion:hit`), missed on {len(fired) - len(hit)}.",
      f"- Extra latency (expansion step, `expansion:ms`): median {statistics.median(ms.values()) if ms else 0:.0f} ms, max {max(ms.values()) if ms else 0} ms; "
      f"total-time delta on fired questions: median {statistics.median(tot_delta) if tot_delta else 0:.0f} ms.",
      f"- Regressions (T2 did not fire but the answer or the sources changed): {len(regress)} {regress or ''}", "",
      "| id | T2 terms | outcome | sources (on) | declined off→on | weak off→on | precheck off→on | Jev off→on | answer on (start) |", "|---|---|---|---|---|---|---|---|---|"]
for i in fired:
    t = next((c[len("expansion:t="):] for c in xp(ON[i]) if c.startswith("expansion:t=")), "")
    oc = "hit" if i in hit else "miss"
    L.append(f"| {i} | {t.replace('|', ' / ')} | {oc} | {'; '.join(s['title'] for s in ON[i]['shownSources'][:3])} | "
             f"{OFF[i]['flags']['declined']}→{ON[i]['flags']['declined']} | {OFF[i]['flags']['weak_sources']}→{ON[i]['flags']['weak_sources']} | "
             f"{pc_off.get(i, '—')}→{pc_on.get(i, '—')} | {jv_off.get(i, '—')}→{jv_on.get(i, '—')} | {ON[i]['answer'][:90].replace('|', '/')} |")
print("\n".join(L) + "\n")
json.dump({"profile": prof, "off": co, "on": cn, "zero_off": {"off": zo, "on": zn}, "fired": fired, "hit": hit, "ms": ms,
           "regressions": regress, "precheck": {"off": pc_off, "on": pc_on}, "jev": {"off": jv_off, "on": jv_on}},
          open(f"results-{prof}.json", "w"), indent=1)
