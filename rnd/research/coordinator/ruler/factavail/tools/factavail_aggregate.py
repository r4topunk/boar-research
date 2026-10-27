#!/usr/bin/env python3
"""FACT-AVAIL aggregation (0 LLM), per FACT-AVAIL-criterion.md.
  python3 -I factavail_aggregate.py sample   -> out/validation.keys (20 Haiku-yes + 20 Haiku-no, first in sha256(key) order)
  python3 -I factavail_aggregate.py final    -> out/factavail-items.json (+ .sha256): agreement, primary labeller, per-item share/label/support
Prints counts only (QUARANTINE, spec r4 §2.4: the item lists stay in the file, coordinator-only)."""
import hashlib, json, sys, collections
from pathlib import Path
D = Path(__file__).resolve().parent.parent
rd = lambda p: [json.loads(l) for l in open(p) if l.strip()]
units = {u["key"]: u for u in rd(D / "in/units.jsonl")}
assert len(units) == 329
def labels(name):
    p = D / f"out/{name}.jsonl"
    return {r["key"]: r for r in rd(p) if r.get("ok")} if p.exists() else {}
H = labels("haiku")
key_order = lambda k: hashlib.sha256(k.encode()).hexdigest()
if sys.argv[1] == "sample":
    assert len(H) == 329, f"haiku incomplete {len(H)}/329"
    yes = sorted([k for k, r in H.items() if r["stated"] == "yes"], key=key_order)
    no = sorted([k for k, r in H.items() if r["stated"] == "no"], key=key_order)
    ny = min(20, len(yes)); nn = 40 - ny
    if len(no) < nn: nn = len(no); ny = min(len(yes), 40 - nn)
    keys = yes[:ny] + no[:nn]
    (D / "out/validation.keys").write_text("\n".join(keys) + "\n")
    print(json.dumps({"validation_keys": len(keys), "haiku_yes_in_sample": ny, "haiku_no_in_sample": nn}))
    sys.exit(0)
O = labels("opus"); OA = labels("opus-all")
vk = [k for k in (D / "out/validation.keys").read_text().split() if k]
assert all(k in O for k in vk), "opus validation incomplete"
agree = sum(H[k]["stated"] == O[k]["stated"] for k in vk)
primary_name, P = ("haiku", H) if agree >= 34 else ("opus-all", OA)
assert len(P) == 329, f"primary labeller {primary_name} incomplete {len(P)}/329"
items = collections.defaultdict(lambda: {"K": 0, "stated": 0, "support": []})
for k, u in units.items():
    it = items[u["id"]]; it["K"] = u["n_points"]
    r = P[k]
    if r["stated"] == "yes" and r.get("pack"):
        it["stated"] += 1; it["support"].append({"point": u["point_index"], "pack": r["pack"], "chunk": r["chunk"], "title": r["title"]})
def lab(sh): return "AVAILABLE" if sh >= 0.5 else "PARTIAL" if sh > 0 else "NONE"
out = {}
for i, it in sorted(items.items()):
    sh = it["stated"] / it["K"]; out[i] = {"K": it["K"], "stated": it["stated"], "share": round(sh, 4), "label": lab(sh), "support": it["support"]}
    # addendum 1: strict = points both Haiku and Opus say yes (Opus labels every Haiku-yes point)
    ks = [k for k, u in units.items() if u["id"] == i]
    hy = [k for k in ks if H[k]["stated"] == "yes"]
    if all(k in O for k in hy):
        st = sum(O[k]["stated"] == "yes" for k in hy); out[i].update({"stated_strict": st, "label_strict": lab(st / it["K"])})
# item-level agreement on the items of the validated points (H7): label from Haiku vs label from Opus on those points only
vi = sorted({units[k]["id"] for k in vk})
def item_lab(src, i):
    ks = [k for k in vk if units[k]["id"] == i]; st = sum(src[k]["stated"] == "yes" for k in ks); return lab(st / len(ks))
item_agree = sum(item_lab(H, i) == item_lab(O, i) for i in vi)
res = {"criterion": "FACT-AVAIL-criterion.md sha b9527555", "primary": primary_name, "validation": {"n": len(vk), "agree": agree, "bar": 34},
       "item_level_agreement_on_validated_items": [item_agree, len(vi)],
       "counts": dict(collections.Counter(v["label"] for v in out.values())), "counts_strict": dict(collections.Counter(v.get("label_strict") for v in out.values())), "items": out}
p = D / "out/factavail-items.json"; p.write_text(json.dumps(res, indent=1) + "\n")
h = hashlib.sha256(p.read_bytes()).hexdigest(); (D / "out/factavail-items.sha256").write_text(f"{h}  factavail-items.json\n")
print(json.dumps({k: res[k] for k in ("primary", "validation", "item_level_agreement_on_validated_items", "counts", "counts_strict")} | {"sha256": h}))
