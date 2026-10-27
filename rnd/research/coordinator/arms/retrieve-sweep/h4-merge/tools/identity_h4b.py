"""H4b identity checks (0 LLM): kept-list identity (ids of keptFull, per question) between replays.
 A: rs-H4b RS_MERGE=gidf  vs H4's gidf replays   B: rs-H4b unset vs H4's off replays   C: gidf2 on ONE pack (merged file) vs control
 D: switch-off 20/20 (proof sets, unset in H4b vs H4 off).   python3 -I tools/identity_h4b.py -> prints + h4b-identity.json"""
import json, os
H = "<workspace>/rnd/research/coordinator/arms/retrieve-sweep/h4-merge/replays/"
CP = "<workspace>/rnd/research/coordinator/arms/coverage-map/compose/replays/"
def rd(f): return {r["id"]: r for r in (json.loads(l) for l in open(f) if l.strip())}
def kept(r):
    return [c["chunkId"] for c in (r.get("keptFull") or [])]
def same(a, b, key=kept):
    if not (os.path.exists(a) and os.path.exists(b)): return None
    A, B = rd(a), rd(b)
    ids = [i for i in A if i in B]
    return f"{sum(key(A[i]) == key(B[i]) for i in ids)}/{len(ids)}"
out = {}
for s in ("q6", "qm", "K3", "K3CM", "K3W", "proof20", "proof6"):
    pre = "main." + s if s.startswith("K") else s
    out[s] = {"gidf(H4b tree) vs H4 gidf": same(H + f"{pre}.h4b-g1.jsonl", H + f"{pre}.gidf.jsonl"),
              "unset(H4b tree) vs H4 off": same(H + f"{pre}.h4b-off.jsonl", H + f"{pre}.off.jsonl"),
              "gidf2 vs gidf": same(H + f"{pre}.h4b-g2.jsonl", H + f"{pre}.gidf.jsonl"),
              "gidf2 vs off": same(H + f"{pre}.h4b-g2.jsonl", H + f"{pre}.off.jsonl")}
for n in (10,):
    out[f"compose N{n}"] = {"gidf(H4b tree) vs coverage-map gidf": same(H + f"compose.N{n}.h4b-g1.jsonl", CP + f"main.N{n}.gidf.jsonl"),
                            "unset(H4b tree) vs coverage-map stock": same(H + f"compose.N{n}.h4b-stock.jsonl", CP + f"main.N{n}.stock.jsonl"),
                            "gidf2 vs gidf": same(H + f"compose.N{n}.h4b-g2.jsonl", CP + f"main.N{n}.gidf.jsonl")}
# scores as well as lists: q6 / qm
json.dump(out, open(H + "../h4b-identity.json", "w"), indent=1)
for k, v in out.items(): print(k, v)
