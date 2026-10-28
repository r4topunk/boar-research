#!/usr/bin/env python3
"""Similarity gates for bench v0.2-new (item-spec 6) -> bench/v0.2/similarity.json (numbers only).

Collision = word-Jaccard > 0.30 (tokens() of bench/v0.1/validate.py) OR BAAI/bge-small-en-v1.5 cosine >= 0.90
(sentence-transformers, normalize_embeddings=True). Pools: the 110 items among themselves, v0.1 public, safety track v0.3,
held-out v0.1 (rnd/veil files, read as bench/v0.1/build.py reads them) and a competitor team @87bb6e9 (sha-pinned, git show).
Held-out and a competitor team text is used for numbers only: neither text nor ids are written (opaque indices).
The topic review (duplicates the thresholds miss) is a human/agent judgment recorded in TOPIC_REVIEW below.

Needs: pip install sentence-transformers (a throwaway venv is fine). Usage: <venv>/bin/python bench/v0.2/similarity.py
"""
import hashlib, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
B = Path("<workspace>")
V01 = B / "boar-eval/bench/v0.1"
VEIL = B / "rnd/veil"
FA_REPO, FA_COMMIT = B / "competitors/<testcase-repo>", "87bb6e9"
FA_FILES = {"tools/e2e_cases.json": ("8644d835445db3f0bb272cb9593c54f88334c2397b74133cfda9f0f5fd0d7f13", "question"),
            "tools/e2e_battery_cases.json": ("c2da3ee0b67df720aa83e42d3d6c3631b08386d519c1f63d910f6d9f66142963", "q")}
J_MAX, COS_MAX = 0.30, 0.90
sys.path.insert(0, str(V01))
from validate import tokens, jacc  # noqa: E402  (same normalization as v0.1 build.py)

TOPIC_REVIEW = {
    "collisions": [],
    "watch_not_counted": [
        {"ids": ["v02-health-A01", "v02-comparison-A03"], "note": "both touch why antibiotics don't treat viral infections; A01 is a situational cold question, A03 a general comparison"},
        {"ids": ["v02-reasoning-A06", "v02-danger-B04"], "note": "both include outdoor lightning safety; A06 is mainly the 9 s distance calculation, B04 the ridge conduct"},
        {"ids": ["v02-comparison-A01", "v02-reasoning-B10"], "note": "both rest on Australia's area (~7.7 M km2); different comparator (US vs UK) and task"},
        {"ids": ["v02-danger-A03", "dng-002", "saf-001"], "note": "moderate-hypothermia branch overlaps; spec 3 asks for the mild vs moderate contrast"},
        {"ids": ["v02-danger-B03", "saf-012"], "note": "escalation-to-heatstroke clause overlaps; the item is heat exhaustion in an alert person"},
    ],
}


def rows(p): return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def main():
    qf = HERE / "questions.v02-new.jsonl"
    new = rows(qf)
    pools = {"v0.1-public": [(r["id"], r["question"]) for r in rows(V01 / "questions.public.jsonl")],
             "safety-track": [(r["id"], r["question"]) for r in rows(V01 / "safety/track.v0.3.jsonl")]}
    held = [r["question"] for f in ("o2-blind-items.jsonl", "o2-blind-items-b2.jsonl") for r in rows(VEIL / f)]
    pools["heldout-v0.1"] = [(f"heldout#{i}", q) for i, q in enumerate(held)]
    fa = []
    for f, (h, key) in FA_FILES.items():
        raw = subprocess.run(["git", "-C", str(FA_REPO), "show", f"{FA_COMMIT}:{f}"], capture_output=True, check=True).stdout
        if hashlib.sha256(raw).hexdigest() != h: sys.exit(f"ABORT: a competitor team {f} sha changed")
        fa += [c[key] for c in json.loads(raw)]
    pools["competitor"] = [(f"competitor#{i}", q) for i, q in enumerate(fa)]

    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer("BAAI/bge-small-en-v1.5")
    enc = lambda ts: m.encode(ts, normalize_embeddings=True, batch_size=64)
    En = enc([n["question"] for n in new]); Tn = [tokens(n["question"]) for n in new]
    Ep = {k: enc([t for _, t in v]) for k, v in pools.items()}; Tp = {k: [tokens(t) for _, t in v] for k, v in pools.items()}

    collisions, internal, per = [], [], {}
    for i, a in enumerate(new):
        for j in range(i + 1, len(new)):
            jc, cs = jacc(Tn[i], Tn[j]), float(En[i] @ En[j])
            internal.append({"a": a["id"], "b": new[j]["id"], "jaccard": round(jc, 4), "cosine": round(cs, 4)})
            if jc > J_MAX or cs >= COS_MAX: collisions.append({"kind": "internal", **internal[-1]})
        per[a["id"]] = {}
        for k, v in pools.items():
            sc = [(jacc(Tn[i], t), float(En[i] @ Ep[k][x]), v[x][0]) for x, t in enumerate(Tp[k])]
            mj, mc = max(sc, key=lambda s: s[0]), max(sc, key=lambda s: s[1])
            per[a["id"]][k] = {"max_jaccard": round(mj[0], 4), "jaccard_nearest": mj[2], "max_cosine": round(mc[1], 4), "cosine_nearest": mc[2]}
            collisions += [{"kind": k, "a": a["id"], "b": o, "jaccard": round(jc, 4), "cosine": round(cs, 4)}
                           for jc, cs, o in sc if jc > J_MAX or cs >= COS_MAX]
    out = {
        "about": __doc__.split("\n\n")[1].replace("\n", " "),
        "questions_sha256": hashlib.sha256(qf.read_bytes()).hexdigest(),
        "model": "BAAI/bge-small-en-v1.5", "thresholds": {"jaccard_gt": J_MAX, "cosine_ge": COS_MAX},
        "pool_sizes": {k: len(v) for k, v in pools.items()},
        "threshold_collisions": collisions,
        "max_internal": {"jaccard": max(p["jaccard"] for p in internal), "cosine": max(p["cosine"] for p in internal)},
        "top_internal_cosine": sorted(internal, key=lambda p: -p["cosine"])[:10],
        "max_vs_pools": {k: {"max_jaccard": max(p[k]["max_jaccard"] for p in per.values()),
                             "max_cosine": max(p[k]["max_cosine"] for p in per.values())} for k in pools},
        "topic_review": TOPIC_REVIEW,
        "per_item": per,
    }
    (HERE / "similarity.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(collisions)} threshold collisions; max internal {out['max_internal']}; vs pools {out['max_vs_pools']}")


if __name__ == "__main__":
    main()
