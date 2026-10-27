#!/usr/bin/env python3
"""Stratified random 20-id slices (RANDOM20), seed 7. Replaces signal20 for arms frozen after 2026-10-11.

Usage: make_random_slice.py            (writes arms/random20-v02.ids, arms/random20-vpara.ids, arms/random20-sets.sha256)
Sets : v02   = the 110 judged ids in blind/bench-v02/runs-deepvpara/judged.ids; category = 2nd '-' token of the id.
       vpara = the 51 judged ids in blind/V-para/runs-cut6/judged.ids; category = 'category' field of
               blind/V-para/items.jsonl (scoped exception: ONLY the id and category fields are read/kept; nothing else is printed).
Rule : random.Random(7). Proportional allocation of 20 slots over categories by largest remainder (quota = 20*n_c/N,
       floor, then remaining slots to the largest fractional parts, ties broken by category name). If 20 >= #categories, every
       category with >= 1 id gets >= 1 slot (slots are taken from the categories with the most surplus over their quota).
       Inside a category, ids are drawn with rng.sample over the sorted id list; categories processed in sorted order.
       Output ids sorted, one per line. Prints per-category counts (set size / slice size) to stdout.
"""
import json, random, hashlib, os, sys, collections
B = "<workspace>/blind"
ARMS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
K = 20

def ids_of(p): return sorted({l.strip() for l in open(p) if l.strip()})

def v02():
    ids = ids_of(f"{B}/bench-v02/runs-deepvpara/judged.ids")
    return {i: i.split("-")[1] for i in ids}

def vpara():
    ids = set(ids_of(f"{B}/V-para/runs-cut6/judged.ids")); cat = {}
    for l in open(f"{B}/V-para/items.jsonl"):
        if not l.strip(): continue
        x = json.loads(l)
        if x.get("id") in ids: cat[x["id"]] = x.get("category", "?")
        del x
    miss = ids - set(cat)
    if miss: sys.exit(f"{len(miss)} ids without category")
    return cat

def alloc(counts, k=K):
    n = sum(counts.values()); q = {c: k * v / n for c, v in counts.items()}
    a = {c: int(q[c]) for c in counts}
    rest = k - sum(a.values())
    for c in sorted(counts, key=lambda c: (-(q[c] - a[c]), c))[:rest]: a[c] += 1
    if k >= len(counts):
        for c in sorted(counts):
            while a[c] < 1:
                d = max((x for x in counts if a[x] > 1), key=lambda x: (a[x] - q[x], x)); a[d] -= 1; a[c] += 1
    return {c: min(a[c], counts[c]) for c in counts}

def pick(cat):
    rng = random.Random(7); by = collections.defaultdict(list)
    for i, c in cat.items(): by[c].append(i)
    cnt = {c: len(v) for c, v in by.items()}; a = alloc(cnt); out = []
    for c in sorted(by): out += rng.sample(sorted(by[c]), a[c])
    return sorted(out), cnt, a

def main():
    for name, f, out in (("v0.2", v02, "random20-v02.ids"), ("V-para", vpara, "random20-vpara.ids")):
        sel, cnt, a = pick(f()); assert len(sel) == K
        open(f"{ARMS}/{out}", "w").write("\n".join(sel) + "\n")
        print(f"{name}: set {sum(cnt.values())} ids -> slice {len(sel)}  ({out})\n  category        set  slice")
        for c in sorted(cnt, key=lambda c: (-cnt[c], c)): print(f"  {c:<14} {cnt[c]:>4} {a[c]:>6}")
    with open(f"{ARMS}/random20-sets.sha256", "w") as w:
        for p in ("random20-v02.ids", "random20-vpara.ids", "_lib/make_random_slice.py"):
            w.write(f"{hashlib.sha256(open(f'{ARMS}/{p}','rb').read()).hexdigest()}  {p}\n")
if __name__ == "__main__": main()
