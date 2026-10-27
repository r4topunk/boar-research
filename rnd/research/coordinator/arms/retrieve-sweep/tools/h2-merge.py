"""H2 merge (0 LLM): full-set replay files for tools/h2-score.py = the switch-off baseline row of every item, with the rows of the
health-strict items replaced by their switch-on replay (tools/run_h2.sh). Valid because healthTopicFallback is called only inside
`if (health)` branches of answer.ts, so an item without grounding:health-strict in the switch-off replay cannot differ (20/20 + sub-set
off-identity proofs in replay/h2/run_h2.log)."""
import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
def merge(base, sub, out):
    s = {r["id"]: r for r in rd(os.path.join(R, sub))}
    # wall/retrieve ms stay the baseline's (quiet-machine) values: the sub-set replays ran under load average 60-100 shared with other arms
    rows = [({**s[r["id"]], "wallMs": r.get("wallMs"), "ms": r.get("ms")} if r["id"] in s else r) for r in rd(base)]
    with open(os.path.join(R, out), "w") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(out, len(rows), "replaced", sum(r["id"] in s for r in rows))
# B0w = the QFORM B0 replay (432/432 same ids) re-run with the wall-time tool
QB = os.path.join(R, "replay/B0w.qform.jsonl"); MB = os.path.join(R, "replay/B0.main.jsonl")
merge(MB, "replay/h2/H2.main.sub.jsonl", "replay/h2/H2.main.jsonl"); merge(MB, "replay/h2/H2b.main.sub.jsonl", "replay/h2/H2b.main.jsonl")
merge(QB, "replay/h2/H2.qform.sub.jsonl", "replay/h2/H2.qform.jsonl"); merge(QB, "replay/h2/H2b.qform.sub.jsonl", "replay/h2/H2b.qform.jsonl")
