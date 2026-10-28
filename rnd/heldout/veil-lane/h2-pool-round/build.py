#!/usr/bin/env python3
"""Build rnd/veil/h2-pool.jsonl from specs.py + check.json (only route-ok, COVERED, verified items).

    python3 rnd/veil/h2-pool-round/build.py        # from <workspace>
"""
import hashlib, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from specs import S

D = "rnd/veil/h2-pool-round"
OUT = "rnd/veil/h2-pool.jsonl"
# must_any for non-numeric shapes, by spec index (1-based)
MUST = {
    9: [["ulaanbaatar", "ulan bator"]], 11: [["rabat"]], 12: [["astana"]], 13: [["sucre", "la paz"]], 15: [["abuja"]], 16: [["hanói", "hanoi"]],
    33: [["volga"]], 34: [["k2"]], 35: [["atlantic"]], 36: [["uranus"]],
    37: [["superior"]], 38: [["saara", "sahara"]], 39: [["kilimanjaro"]], 40: [["são paulo", "sao paulo"]],
    41: [["yes"]], 42: [["no", "huron"]], 43: [["yes"]], 44: [["no", "yellow"]], 45: [["yes"]],
    46: [["sim"]], 47: [["sim"]], 48: [["sim"]],
    49: [["russia"]], 50: [["india"]], 51: [["pacific"]], 52: [["vatican"]], 53: [["venus"]],
    54: [["brasil", "brazil"]], 55: [["nigéria", "nigeria"]], 56: [["argélia", "argelia", "algeria"]],
    57: [["spain"]], 58: [["brazil"], ["paraguay"], ["argentina"], ["chile"], ["peru"]], 59: [["washington"]], 60: [["augustus"]],
    61: [["leonardo", "da vinci"]], 62: [["pedro i", "pedro primeiro", "dom pedro"]], 63: [["fleming"]], 64: [["brasil", "brazil"], ["argentina"]],
    22: [["116"]], 23: [["24 horas", "24 h"], ["39"]], 3: [["6,650", "6.650", "6650", "7,088", "7.088", "7088"]], 6: [["6,300", "6.300", "6300", "6,236", "6.236", "6236"]], 24: [["1.500", "1500", "1,500", "1 500", "mil e quinhentas"]],
}
FORBID = {41: [["no, mount fuji is higher"]], 42: [["yes, lake michigan is larger"]], 44: [["yes, the mekong is longer"]],
          13: [["a capital é brasília"]], 38: [["o gobi é maior"]]}


def num_variants(tok):
    t = tok.replace(" ", "")
    v = {tok.lower(), t, t.replace(",", "."), t.replace(",", ""), t.replace(",", " ")}
    return sorted(x for x in v if x)


def default_must(ans, toks):
    """Numeric/year items: the first verify token that the reference answer states (PT answers write 1.500 for 1,500)."""
    norm = ans.replace(".", ",")
    for t in toks:
        if t in ans or t in norm:
            return [num_variants(t)]
    m = re.search(r"\d[\d.,]*", ans)  # PT answers paraphrase the English token ("50 estados" for "50 states")
    if m:
        return [num_variants(m.group(0).rstrip(".,"))]
    raise SystemExit(f"no verify token or number in the answer: {ans!r} {toks}")


def main():
    chk = {r["n"]: r for r in json.load(open(f"{D}/check.json"))}
    rows, dropped, evidence = [], [], []
    for i, (tpl, lang, q, pages, ans, verify, shape) in enumerate(S, 1):
        c = chk[i]
        why = [x for x, ok in (("route", c["route_ok"]), ("coverage", c["all_covered"]), ("verify", c["verified"])) if not ok]
        if why:
            dropped.append({"n": i, "question": q, "reasons": why, "coverage": c["coverage"], "checks": c["checks"]})
            continue
        must = MUST.get(i) or default_must(ans, verify[0][1])
        rid = f"vit-h2p-{len(rows) + 1:03d}"
        rows.append({
            "id": rid, "category": "comparison" if shape in ("comparative", "yes/no") else "reasoning", "question": q, "lang": lang,
            "shape": shape, "template": tpl, "words": c["words"],
            "coverage": c["coverage"], "answer_position": {k["page"]: k["position"] for k in c["checks"]},
            "answer_position_method": "English Wikipedia plain-text extract via the MediaWiki API on 2026-10-01 (proxy for the kit's article order)",
            "answer": ans, "why_1b_fails": "Short single-fact lookup in the instant-route shape; tests whether the served sentence is about the asked entity.",
            "rubric": ["States the key fact: " + ans],
            "reference_sources": ["https://en.wikipedia.org/wiki/" + p.replace(" ", "_") for p in pages],
            "origin": "veil-blind", "vitalik_source": [],
            "grading": {"must_any": must, "forbid": FORBID.get(i, []), "refuse_ok": False},
            "notes": "Answer checked against the source page text (MediaWiki API extract) on 2026-10-01; matching sentence recorded in h2-pool-round/evidence.jsonl.",
            "grading_version": "2.2"})
        evidence.append({"id": rid, "question": q, "checks": c["checks"]})
    with open(OUT, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(f"{D}/evidence.jsonl", "w", encoding="utf-8") as f:
        for r in evidence:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump(dropped, open(f"{D}/dropped.json", "w"), indent=1, ensure_ascii=False)
    bad = [r["id"] for r in rows if not all(any(t.lower() in r["answer"].lower() for t in g) for g in r["grading"]["must_any"])]
    print(f"kept {len(rows)} dropped {len(dropped)}; must_any self-check failures: {bad or 'none'}")
    print("sha256", hashlib.sha256(open(OUT, "rb").read()).hexdigest())


if __name__ == "__main__":
    main()
