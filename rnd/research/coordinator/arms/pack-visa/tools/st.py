#!/usr/bin/env python3
"""PACK-VISA self-test helper = the shared pack self-test tools (arms/packs/tools: selftest_common, selftest_draw, selftest_check),
imported unchanged, with two module paths redirected: packs are looked up in shared-data/packs/wave4 first, and the self-test
files live in arms/pack-visa/selftest/ (this arm's directory) instead of rnd/research/packs/selftest/.
usage (run with arms/packs/.venv/bin/python -I, which has zstandard):
  st.py draw  boar-visa-en          seeded draw (seed 11): strata = article family (requirements / policy) x length tercile
  st.py show  boar-visa-en <id> [n] article text with chunk markers
  st.py fill  boar-visa-en <draft>  adds source{} and chunk_index from the pack
  st.py check boar-visa-en          the shared checks (selftest_check.check)
"""
import json, os, random, sys
B = "<workspace>"
sys.path.insert(0, f"{B}/rnd/research/coordinator/arms/packs/tools")
import selftest_common as C  # noqa: E402
C.PACK_DIRS.insert(0, f"{B}/shared-data/packs/wave4")
OUT = f"{B}/rnd/research/coordinator/arms/pack-visa/selftest"; os.makedirs(OUT, exist_ok=True)
C.OUT_DIR = OUT
import selftest_draw as D  # noqa: E402
import selftest_check as K  # noqa: E402
D.OUT_DIR = OUT; K.OUT_DIR = OUT

def draw(name, seed=11, n=60):
    pk = C.Pack(name)
    el = []
    for aid, src, title, views, b, o, l in pk.rows():
        if l < 1500: continue
        fam = "requirements" if title.startswith("Visa requirements for") else "policy"
        el.append({"id": aid, "title": title, "source": src, "views": views, "len": l, "fam": fam})
    cuts = {}
    for fam in ("requirements", "policy"):
        ls = sorted(x["len"] for x in el if x["fam"] == fam)
        cuts[fam] = [ls[len(ls) // 3], ls[2 * len(ls) // 3]]
    cells = {}
    for x in el:
        c = cuts[x["fam"]]; t = 0 if x["len"] < c[0] else 1 if x["len"] < c[1] else 2
        x["cell"] = [x["fam"], t]; cells.setdefault((x["fam"], t), []).append(x)
    rng = random.Random(seed)
    keys = sorted(cells)
    for k in keys: rng.shuffle(cells[k])
    cand = []
    while len(cand) < n and any(cells.values()):
        for k in keys:
            if cells[k] and len(cand) < n: cand.append(cells[k].pop())
    path = f"{OUT}/draw-{name}.json"
    prev = json.load(open(path)) if os.path.exists(path) else {}
    out = {"pack": name, "seed": seed, "eligible": len(el), "strata": "article family (requirements/policy) x length tercile; text >= 1500 bytes",
           "length_cuts": cuts, "candidates": [{k: x[k] for k in ("id", "title", "source", "views", "len", "cell")} for x in cand]}
    for k in ("chosen", "rejects", "replacements"):
        if k in prev: out[k] = prev[k]
    json.dump(out, open(path, "w"), indent=1, ensure_ascii=False)
    print(f"{name}: eligible {len(el)} candidates {len(cand)} -> {path}")

if __name__ == "__main__":
    cmd, name = sys.argv[1], sys.argv[2]
    if cmd == "draw": draw(name)
    elif cmd == "show": D.show(name, int(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 6000)
    elif cmd == "fill": D.fill(name, sys.argv[3])
    elif cmd == "check": sys.exit(0 if K.check(name) else 1)
