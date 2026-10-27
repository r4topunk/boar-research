#!/usr/bin/env python3
"""RD1 replay checks (0 LLM). python3 -I ident_replay_rd1.py off|on
off: switch unset replay (RD1 tree) vs sefix/replays/main.v3-extra.jsonl (F1b replay): keptFull, sources, reasonCodes must be identical.
on: BOAR_READ_SEQ=1 replay vs the same file: lists the changed-context ids (keptFull order/ids/body or sources or reasonCodes differ)."""
import json, sys
C = "<workspace>/rnd/research/coordinator/arms/coverage-map"
ld = lambda p: {json.loads(l)["id"]: json.loads(l) for l in open(p) if l.strip()}
mode = sys.argv[1]
ref = ld(C + "/sefix/replays/main.v3-extra.jsonl"); new = ld(C + f"/reader/rd1/replays/main.{mode}.jsonl")
def kf(r): return [(c.get("chunkId"), c.get("title"), c.get("body")) for c in (r.get("keptFull") or [])]
res = {}
for i, r in ref.items():
    n = new.get(i)
    if n is None: res[i] = dict(missing=True); continue
    res[i] = dict(keptFull=kf(n) == kf(r), sources=n.get("sources") == r.get("sources"), reasonCodes=n.get("reasonCodes") == r.get("reasonCodes"))
bad = {i: v for i, v in res.items() if v.get("missing") or not all(v.values())}
out = dict(mode=mode, n_ref=len(ref), n_new=len(new), n_identical=len(ref) - len(bad), all_identical=not bad)
if mode == "off": out["not_identical"] = bad
else:
    se = lambda r: any((c.get("chunkId") or "").startswith("pack:local-qa-") for c in (r.get("keptFull") or []))
    out["changed_ids"] = sorted(bad); out["n_changed"] = len(bad); out["changed_with_qa_pack_chunk_kept"] = sum(1 for i in bad if se(ref[i]))
    out["changed_by_kind"] = {k: sum(1 for i in bad if not res[i].get(k, True)) for k in ("keptFull", "sources", "reasonCodes")}
    out["readseq_codes"] = {i: [c for c in new[i].get("reasonCodes", []) if c.startswith("readseq:")] for i in sorted(new) if any(c.startswith("readseq:") for c in new[i].get("reasonCodes", []))}
json.dump(out, open(C + f"/reader/rd1/replay-{mode}.json", "w"), indent=1); print(json.dumps(out, indent=1)[:3000])
