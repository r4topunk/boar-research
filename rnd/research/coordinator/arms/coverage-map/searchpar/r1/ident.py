"""Switch-off identity: python3 -I ident.py <off.jsonl> <ref.jsonl>  -> compares per id raw/wide/kept chunk ids and reason codes."""
import json, sys
rd = lambda f: {r["id"]: r for r in (json.loads(l) for l in open(f) if l.strip())}
a, b = rd(sys.argv[1]), rd(sys.argv[2])
same = 0; bad = []
for i, r in a.items():
    s = b[i]; ok = all([c["chunkId"] for c in r[k]] == [c["chunkId"] for c in s[k]] for k in ("rawFull", "wideFull", "keptFull")) and r["reasonCodes"] == s["reasonCodes"]
    same += ok
    if not ok: bad.append(i)
print(f"identical {same}/{len(a)}", bad)
