#!/usr/bin/env python3
"""RELGATE Phase 1: build labelled sets C (chunks), K (contexts), S (safety) from PUBLIC selftest data.
Writes ../data/{chunks,contexts,safety}.jsonl (public selftest text only) and prints class balance."""
import json, glob, os, re, hashlib, unicodedata
from collections import Counter

ROOT = "<workspace>"
ARM = f"{ROOT}/rnd/research/coordinator/arms/relgate"
GEN = f"{ROOT}/rnd/research/coordinator/arms/headpass-st/gen-x2b"
OUT = f"{ARM}/data"
os.makedirs(OUT, exist_ok=True)

def norm(s):
    s = unicodedata.normalize("NFKC", s).lower()
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"[‐-―]", "-", s)
    return re.sub(r"\s+", " ", s).strip()

def toks(s):
    return re.findall(r"[a-z0-9]+", norm(s))

def match(quote, chunk):
    q, c = norm(quote), norm(chunk)
    if q and q in c:
        return "exact"
    qt = toks(quote)
    if len(qt) >= 8:
        ct = Counter(toks(chunk)); qc = Counter(qt)
        hit = sum(min(n, ct[w]) for w, n in qc.items())
        if hit / len(qt) >= 0.80:
            return "fuzzy"
    return None

def half(item_id):
    return "A" if int(hashlib.sha256(item_id.encode()).hexdigest()[:8], 16) % 2 == 0 else "B"

def split_context(system):
    i = system.find("\n\nContext:\n")
    if i < 0:
        return None, None, None
    head = system[: i]
    ctx = system[i + len("\n\nContext:\n"):]
    # sources start with "[n] " at line start
    parts = re.split(r"(?:^|\n\n)\[(\d+)\] ", ctx)
    chunks = []
    for k in range(1, len(parts), 2):
        chunks.append((int(parts[k]), parts[k + 1].rstrip("\n")))
    return head, ctx, chunks

ids54 = set(open(f"{ROOT}/rnd/research/coordinator/arms/packread/ids-54.ids").read().split())
C, K = [], []
excluded = []
for f in sorted(glob.glob(f"{GEN}/st-*-cut7-headpassx2b-s42.prompts.jsonl")):
    pack = os.path.basename(f)[3:].split("-cut7")[0]
    Q = {json.loads(l)["question"]: json.loads(l) for l in open(f"{ROOT}/boar-eval/bench/selftest/{pack}/questions.jsonl")}
    for line in open(f):
        p = json.loads(line)
        it = Q[p["query"]]
        sysm = p["prompt"][0]["content"]
        head, ctx, chunks = split_context(sysm)
        if not chunks:
            excluded.append(it["id"]); continue
        quotes = [x["quote"] for x in it["selftest"]["in_pack_facts"]]
        found_q = set(); rows = []
        for n, (num, body) in enumerate(chunks):
            m = [(qi, match(q, body)) for qi, q in enumerate(quotes)]
            kinds = [k for _, k in m if k]
            for qi, k in m:
                if k: found_q.add(qi)
            pos = bool(kinds)
            rows.append({"cid": f"{it['id']}#{num}", "id": it["id"], "pack": pack, "half": half(it["id"]), "rank": n + 1, "num": num,
                         "question": it["question"], "chunk": body, "label": int(pos),
                         "rule": ("exact" if "exact" in kinds else ("fuzzy" if kinds else None)),
                         "in54": it["id"] in ids54})
        C.extend(rows)
        K.append({"id": it["id"], "pack": pack, "half": half(it["id"]), "question": it["question"], "in54": it["id"] in ids54,
                  "prompt": p["prompt"], "n_src": len(chunks), "label": int(any(r["label"] for r in rows)),
                  "label_all": int(len(found_q) == len(quotes)), "n_facts": len(quotes), "n_found": len(found_q),
                  "pos_nums": [r["num"] for r in rows if r["label"]]})

# Safety set
SQ = [json.loads(l) for l in open(f"{ROOT}/boar-eval/bench/selftest/safepack/questions.jsonl")]
OR = {r["id"]: r for r in json.load(open(f"{ROOT}/rnd/research/coordinator/arms/safepack/oracle-ctx.json"))["rows"]}
S = []
for i, q in enumerate(SQ):
    o = OR[q["id"]]
    S.append({"sid": q["id"] + "#pos", "id": q["id"], "half": half(q["id"]), "question": q["question"], "title": o["title"], "passage": o["passage"], "label": 1})
    for j in range(1, len(SQ)):
        o2 = OR[SQ[(i + j) % len(SQ)]["id"]]
        if o2["title"] != o["title"]:
            break
    S.append({"sid": q["id"] + "#neg", "id": q["id"], "half": half(q["id"]), "question": q["question"], "title": o2["title"], "passage": o2["passage"], "label": 0, "neg_from": o2["id"]})

for name, rows in (("chunks", C), ("contexts", K), ("safety", S)):
    with open(f"{OUT}/{name}.jsonl", "w") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

def bal(rows, key="label"):
    return {"n": len(rows), "pos": sum(r[key] for r in rows),
            "A": sum(1 for r in rows if r["half"] == "A"), "B": sum(1 for r in rows if r["half"] == "B"),
            "pos_A": sum(r[key] for r in rows if r["half"] == "A"), "pos_B": sum(r[key] for r in rows if r["half"] == "B")}

summary = {
    "excluded_no_context": excluded,
    "chunks": bal(C), "chunks_54": bal([r for r in C if r["in54"]]),
    "chunk_label_rule": dict(Counter(r["rule"] for r in C if r["label"])),
    "contexts": bal(K), "contexts_54": bal([r for r in K if r["in54"]]),
    "contexts_label_all": bal(K, "label_all"),
    "n_src_dist": dict(sorted(Counter(r["n_src"] for r in K).items())),
    "pos_chunks_per_pos_context": dict(sorted(Counter(len(r["pos_nums"]) for r in K if r["label"]).items())),
    "pos_at_rank1": sum(1 for r in K if 1 in r["pos_nums"]),
    "by_pack": {p: [sum(1 for r in K if r["pack"] == p), sum(r["label"] for r in K if r["pack"] == p)] for p in sorted({r["pack"] for r in K})},
    "safety": bal(S),
}
json.dump(summary, open(f"{ARM}/aggregates/sets.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
