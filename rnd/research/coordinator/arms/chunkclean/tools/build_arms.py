#!/usr/bin/env python3
"""CHUNKCLEAN inputs (0 LLM). Checks every extraction span is a verbatim substring of its gold chunk text, builds the clean text
(spans joined by `join`, or per-gap `joins`), and writes the C and P oracle files ({question, pack, chunk_id, orig, text}) and the
C/P request files (ORACLE-REAL requests, runId/arm renamed). Usage: build_arms.py"""
import json, hashlib
CC = "<workspace>/rnd/research/coordinator/arms/chunkclean/"; OR = CC + "../oracle-real/"
G = json.load(open(CC + "gold-chunks.json")); X = json.load(open(CC + "extractions.json"))
IDS = [l.strip() for l in open(OR + "items.ids") if l.strip()]
assert sorted(G) == sorted(IDS) == sorted(X), "item sets differ"
clean = {}
for i in IDS:
    sp = X[i]["spans"]; js = X[i].get("joins") or [X[i]["join"]] * (len(sp) - 1)
    for s in sp: assert s in G[i]["text"], f"{i}: span not verbatim: {s[:60]}"
    t = sp[0] + "".join(j + s for j, s in zip(js, sp[1:])); clean[i] = t
log = []
for arm in ("C", "P"):
    o = {}
    for i in IDS:
        g = G[i]; t = clean[i] if arm == "C" else clean[i] + "\n\n" + g["text"]
        o[i] = dict(question=g["question"], pack=g["pack"], chunk_id=g["chunk_id"], orig=g["text"], text=t)
    open(CC + f"tools/oracle-{arm}.json", "w").write(json.dumps(o, indent=1, ensure_ascii=False) + "\n")
    run = f"chunkclean-{arm}-K3-v01gold-s42"
    with open(CC + f"runs/req/{run}.requests.jsonl", "w") as w:
        for l in open(OR + "runs/req/oracle-K3-v01gold-s42.requests.jsonl"):
            r = json.loads(l); r["runId"] = run; r["config"]["arm"] = f"cut7-headpass-x2+litepacks+chunkclean-{arm}"; w.write(json.dumps(r) + "\n")
for i in IDS:
    log.append(dict(item=i, source=f"pack:{G[i]['pack']}:{G[i]['chunk_id']}", chunk_chars=len(G[i]["text"]), clean_chars=len(clean[i]), n_spans=len(X[i]["spans"]), clean=clean[i]))
open(CC + "extraction-log.jsonl", "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in log))
cc = sorted(r["clean_chars"] for r in log); oc = sorted(r["chunk_chars"] for r in log)
print("ok 30 verbatim; clean chars median", cc[15], "max", cc[-1], "| chunk median", oc[15])
for f in ("tools/oracle-C.json", "tools/oracle-P.json", "runs/req/chunkclean-C-K3-v01gold-s42.requests.jsonl", "runs/req/chunkclean-P-K3-v01gold-s42.requests.jsonl", "extractions.json", "gold-chunks.json"):
    print(hashlib.sha256(open(CC + f, "rb").read()).hexdigest(), f)
