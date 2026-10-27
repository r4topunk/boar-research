"""WARNSPEC-PATCH replay requests: HEALTHGAP-r2's replay requests (probes 64, v0.1 60, self-tests 180; claim kit) re-labelled for the
tree under test (commit + arm); items, kit, seed, settings unchanged. Usage: python3 -I mkreq_warn.py <commit> <arm> <out dir>"""
import json, sys
H = "<workspace>/rnd/research/coordinator/arms/healthgap/runs/r2"; commit, arm, out = sys.argv[1:4]
for s in ["probes", "v01", "st"]:
    rows = [json.loads(l) for l in open(f"{H}/hg2-replay-{s}.requests.jsonl") if l.strip()]
    with open(f"{out}/warn-replay-{s}.{arm}.requests.jsonl", "w") as o:
        for r in rows:
            r["runId"] = f"warn-replay-{s}"; r["config"]["commit"] = commit; r["config"]["arm"] = arm
            o.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(s, len(rows))
