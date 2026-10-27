"""Switch-off identity: raw / wide / kept chunk ids and reason codes of two replays. python3 -I ident.py A.jsonl B.jsonl"""
import json, sys
rd = lambda f: {r["id"]: r for r in (json.loads(l) for l in open(f) if l.strip())}
a, b = rd(sys.argv[1]), rd(sys.argv[2])
ids = lambda r, k: [c["chunkId"] for c in r[k]]
same = {k: sum(ids(a[i], k) == ids(b[i], k) for i in a if i in b) for k in ("rawFull", "wideFull", "keptFull")}
rc = sum(a[i]["reasonCodes"] == b[i]["reasonCodes"] for i in a if i in b)
allsame = sum(all(ids(a[i], k) == ids(b[i], k) for k in ("rawFull", "wideFull", "keptFull")) and a[i]["reasonCodes"] == b[i]["reasonCodes"] for i in a if i in b)
print(json.dumps(dict(n=len(a), same=same, reason_codes=rc, all_identical=allsame)))
