"""FOLLOWUP replay questions (0 LLM). t1: python3 -I mkq.py t1  -> runs/q/t1-<pack>.jsonl (id fu-XX-t1, the self-test question)
t2: python3 -I mkq.py t2  -> runs/q/t2-<pack>.jsonl (id fu-XX-t2; history = [user t1, assistant placeholder + sources = t1 OFF replay kept titles])"""
import json, os, sys
A = "<workspace>/rnd/research/coordinator/arms/followup"; os.makedirs(f"{A}/runs/q", exist_ok=True)
P = [json.loads(l) for l in open(f"{A}/pairs.jsonl")]; packs = sorted({p["pack"] for p in P}, key=[p["pack"] for p in P].index)
PLACEHOLDER = "(previous answer)"
for pk in packs:
    rows = []
    if sys.argv[1] == "t1":
        rows = [{"id": f"{p['id']}-t1", "question": p["t1"]} for p in P if p["pack"] == pk]
    else:
        off = {}
        for l in open(f"{A}/runs/replay/t1-{pk}.fu.jsonl"):
            r = json.loads(l)
            if r["mode"] == "off" and r["id"] not in off: off[r["id"]] = [x["title"] for x in r["kept"]]
        for p in P:
            if p["pack"] != pk: continue
            src = list(dict.fromkeys(off[f"{p['id']}-t1"]))
            rows.append({"id": f"{p['id']}-t2", "question": p["t2"], "history": {"turns": [{"role": "user", "text": p["t1"]},
                         {"role": "assistant", "text": PLACEHOLDER, **({"sources": src} if src else {})}]}})
    open(f"{A}/runs/q/{sys.argv[1]}-{pk}.jsonl", "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    print(sys.argv[1], pk, len(rows))
