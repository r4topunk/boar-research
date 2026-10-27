#!/usr/bin/env python3
"""prep_judge.py <dir>: seed judge.v1-med verdict files for judge.mjs resume, CHANGED ITEMS ONLY for the judge.
ONE named source run: of all earlier runs' judge.v1-med files (bench v0.1 refs), the run directory whose verdicts (both orders,
byte-identical answer text) cover the most of this run's control items over both seeds is the source; control verdicts come from it only.
Items it does not cover are judged fresh on the control (changed items) or, if unchanged (identical text in both arms, so the same
verdict for both), carried identically into both sides from the same source else any earlier run is NOT used: they are dropped from the pooled ratio
and listed. Writes <dir>/{ctl,arm}-v01-sNN.judgments.v1-med.jsonl (seeds) and *.tojudge.traces.jsonl (changed items only)."""
import json, sys, glob, os, collections
D = sys.argv[1]
KILN = "<workspace>/boar-eval/runs/kiln"
REFS = "bd235bb9811f"
ld = lambda p: {t["itemId"]: t for t in map(json.loads, open(p))}
rows = lambda p: [json.loads(l) for l in open(p) if l.strip()]
txt = lambda t: t["answer"]["text"]
ctl = {s: ld(f"{D}/ctl-v01-s{s}.traces.jsonl") for s in ("44", "45")}
arm = {s: ld(f"{D}/arm-v01-s{s}.traces.jsonl") for s in ("44", "45")}
# index per source run dir: (seed-agnostic) (item, text) -> {order: row}
idx = collections.defaultdict(dict)
for jp in sorted(glob.glob(f"{KILN}/**/*.judgments.v1-med.jsonl", recursive=True)):
    if f"/cryptotruth/" in jp: continue
    tp = jp.replace(".judgments.v1-med.jsonl", ".traces.jsonl")
    if not os.path.exists(tp): continue
    try: tr = ld(tp)
    except Exception: continue
    for r in rows(jp):
        if not r.get("ok") or not r.get("refsSha256", "").startswith(REFS) or r["queryId"] not in tr: continue
        idx[os.path.dirname(jp)].setdefault((r["queryId"], txt(tr[r["queryId"]])), {})[r["order"]] = (r, os.path.basename(jp))
def cover(src, s):
    return {i for i, t in ctl[s].items() if len(idx[src].get((i, txt(t)), {})) == 2}
best = max(idx, key=lambda d: sum(len(cover(d, s)) for s in ctl))
print("SOURCE RUN:", os.path.relpath(best, KILN), {s: f"{len(cover(best, s))}/{len(ctl[s])}" for s in ctl})
info = {"source_run": os.path.relpath(best, KILN)}
for s in ("44", "45"):
    c, a = ctl[s], arm[s]
    changed = sorted(i for i in a if txt(a[i]) != txt(c[i]))
    cj = []; src_files = set(); uncovered_unchanged = []; need_fresh = []
    for i, t in c.items():
        slot = idx[best].get((i, txt(t)), {})
        if len(slot) == 2:
            cj += [r for r, _ in slot.values()]; src_files |= {f for _, f in slot.values()}
        elif i in changed: need_fresh.append(i)
        else: uncovered_unchanged.append(i)
    open(f"{D}/ctl-v01-s{s}.judgments.v1-med.jsonl", "w").write("".join(json.dumps(r) + "\n" for r in cj))
    # the arm: unchanged items carry the control's verdicts (same text); changed ones are judged fresh
    byq = collections.defaultdict(list)
    for r in cj: byq[r["queryId"]].append(r)
    aj = [r for i in a if i not in changed for r in byq.get(i, [])]
    open(f"{D}/arm-v01-s{s}.judgments.v1-med.jsonl", "w").write("".join(json.dumps(r) + "\n" for r in aj))
    for side, tr in (("ctl", c), ("arm", a)):
        keep = [i for i in changed if side == "arm" or i in need_fresh]
        open(f"{D}/{side}-v01-s{s}.tojudge.traces.jsonl", "w").write("".join(json.dumps(tr[i]) + "\n" for i in keep))
    info[s] = dict(changed=changed, ctl_fresh=need_fresh, uncovered_unchanged=uncovered_unchanged, source_files=sorted(src_files))
    print(f"s{s}: changed {len(changed)}; control verdicts reused {len(c) - len(need_fresh) - len(uncovered_unchanged)}; changed items judged fresh on the control {need_fresh}; unchanged items with no source verdict {uncovered_unchanged}")
json.dump(info, open(f"{D}/prep.json", "w"), indent=1)
