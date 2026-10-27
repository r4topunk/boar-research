#!/usr/bin/env python3
"""Render the per-item section of PACK-TABLE-17B.md from aggregates/pack_table_17b.json (0 calls). python3 -I mk_md.py > per-item.md"""
import json
d = json.load(open("<workspace>/rnd/research/coordinator/arms/cb17/aggregates/pack_table_17b.json"))
f = lambda x: "" if x is None else (f"{x:+.2f}" if isinstance(x, float) and x != abs(x) or False else (f"{x:.2f}" if isinstance(x, float) else str(x)))
sg = lambda x: "" if x is None else f"{x:+.2f}"
yn = lambda x: {True: "yes", False: "no", None: "-"}[x]
fl = lambda r, a: ("W" if r[f"warned_{a}"] else "") + ("D" if r[f"declined_{a}"] else "")
print("| id | set | tag | in-pack | fact in K1 ctx | funnel K1 | H CB | H K0 | H K1 | H K3* | O CB | O K0 | O K1 | ΔH K1−CB | ΔH K0−CB | ΔO K0−CB | flags CB/K0/K1 |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in d["rows"]:
    print(f"| {r['id']}{' ·' if r['cv5_51'] else ''} | {r['set']} | {r['tag'] or '-'} | {r['in_pack'] or '-'} | {yn(r['fact_present_K1'])} | {r['funnel_stage_K1'] or '-'} | "
          + " | ".join("" if r[k] is None else f"{r[k]:.2f}" for k in ("haiku_CB", "haiku_K0", "haiku_K1", "haiku_K3", "opus_CB", "opus_K0", "opus_K1"))
          + f" | {sg(r['d_haiku_K1_CB'])} | {sg(r['d_haiku_K0_CB'])} | {sg(r['d_opus_K0_CB'])} | {fl(r,'CB') or '-'}/{fl(r,'K0') or '-'}/{fl(r,'K1') or '-'} |")
