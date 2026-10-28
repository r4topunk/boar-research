#!/usr/bin/env python3
"""Majority label per blind item from 3 Opus raters + Jev (rule of rnd/bench/calibration/agents-v0/PANEL.md). No map access.

    python3 rnd/veil/o2-ab-labels/work/aggregate.py     # from <workspace>

Rule: of the 4 panel votes, >=3 wins; else plurality; a 2-2 tie is broken by the Opus raters' majority.
Jev mapping: correct->pass, confident_wrong->cw, wrong_or_incomplete_hedged->fail, refused->refused.
Writes majority.json and SHA256SUMS (all label files), and prints Fleiss' kappa.
"""
import collections, hashlib, json, os

D = "rnd/veil/o2-ab-labels"
LABELS = ("pass", "fail", "cw", "refused")
JEV = {"correct": "pass", "confident_wrong": "cw", "wrong_or_incomplete_hedged": "fail", "refused": "refused"}


def load(path, key="label", mapping=None):
    out = {}
    for l in open(path, encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            lab = mapping[r[key]] if mapping else r[key]
            if lab not in LABELS:
                raise SystemExit(f"{path}: bad label {lab!r} on {r['id']}")
            out[r["id"]] = lab
    return out


def fleiss(rows, k=LABELS):
    n = len(rows[0]); N = len(rows)
    P = [(sum(r.count(c) ** 2 for c in k) - n) / (n * (n - 1)) for r in rows]
    p = [sum(r.count(c) for r in rows) / (N * n) for c in k]
    Pbar, Pe = sum(P) / N, sum(x * x for x in p)
    return (Pbar - Pe) / (1 - Pe) if Pe < 1 else 1.0


def main():
    blind = [json.loads(l)["id"] for l in open("rnd/plumb/data/o2-ab-blind/o2-ab.blind.jsonl", encoding="utf-8")]
    raters = {f"opus-{i}": load(f"{D}/rater-opus-{i}.jsonl") for i in (1, 2, 3)}
    raters["jev"] = load(f"{D}/rater-jev.raw.jsonl", mapping=JEV)
    for name, lab in raters.items():
        if set(lab) != set(blind):
            raise SystemExit(f"{name}: ids differ from the blind file ({len(lab)} vs {len(blind)})")
    items, ties, dist = {}, 0, collections.Counter()
    for i in blind:
        votes = {n: raters[n][i] for n in raters}
        c = collections.Counter(votes.values())
        top = c.most_common()
        if top[0][1] >= 3 or len(top) == 1 or top[0][1] > top[1][1]:
            maj, how = top[0][0], f"{top[0][1]}/4"
        else:  # 2-2 tie: Opus majority among the tied labels
            tied = [l for l, n in top if n == top[0][1]]
            oc = collections.Counter(v for n, v in votes.items() if n.startswith("opus") and v in tied)
            maj, how = oc.most_common(1)[0][0], "2-2, Opus break"
            ties += 1
        dist[how] += 1
        items[i] = {"votes": votes, "majority": maj, "agreement": how}
    rows = [[raters[n][i] for n in raters] for i in blind]
    opus_rows = [[raters[n][i] for n in raters if n.startswith("opus")] for i in blind]
    out = {"rule": ">=3 of 4 votes; else plurality; 2-2 tie broken by the Opus majority (PANEL.md)",
           "raters": {"opus-1..3": "Agent tool, model opus, general-purpose, fresh context, read one copied input file only",
                      "jev": "rnd/kiln/exp-04-jev/jev_label.py, prompt v2 (3426670d...), cache jev-cache/"},
           "fleiss_kappa_4": round(fleiss(rows), 3), "fleiss_kappa_opus3": round(fleiss(opus_rows), 3),
           "agreement": dict(dist), "ties": ties,
           "majority_counts": dict(collections.Counter(v["majority"] for v in items.values())), "items": items}
    json.dump(out, open(f"{D}/majority.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    files = ["rater-opus-1.jsonl", "rater-opus-2.jsonl", "rater-opus-3.jsonl", "rater-jev.raw.jsonl", "majority.json",
             "work/rater_input.md", "work/jev_items.jsonl", "work/refs.all.jsonl", "work/refs.evalset.jsonl"]
    with open(f"{D}/SHA256SUMS", "w") as f:
        for p in files:
            f.write(f"{hashlib.sha256(open(os.path.join(D, p), 'rb').read()).hexdigest()}  {p}\n")
    print(json.dumps({k: out[k] for k in ("fleiss_kappa_4", "fleiss_kappa_opus3", "agreement", "ties", "majority_counts")}))


if __name__ == "__main__":
    main()
