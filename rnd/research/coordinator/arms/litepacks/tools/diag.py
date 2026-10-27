#!/usr/bin/env python3
"""LITEPACKS diagnostic (0 LLM): per arm vs K0 on MAIN, correctness moves (>= +1 / <= -1) split by whether the new pack holds a kept slot;
warned -> unwarned transitions and their correctness. Usage: python3 -I diag.py [set] (MAIN default; st_cand, st_se)."""
import sys, os, runpy
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.argv = [sys.argv[0]]; import io, contextlib
with contextlib.redirect_stdout(io.StringIO()): g = runpy.run_path(f"{H}/tools/agg.py")
S = sys.argv[1] if len(sys.argv) > 1 else "MAIN"
NEW = {"K1": {"simplewiki"}, "K2": {"simplewiki", "factbook"}, "K3": {"simplewiki", "factbook", "medlineplus", "firstaid"}, "K4": {"top100k"}}
J, TR, pack_of, warned = g["J"], g["TR"], g["pack_of"], g["warned"]
for a in ["K1", "K2", "K3", "K4"]:
    for setname in [x for x in ("MAIN", "st_cand", "st_se") if all(i in J[a] and J[a][i] for i in g["SETS"][x])]:
        ids = g["SETS"][setname]; row = {}
        for i in ids:
            hit = any(pack_of(k, a) in NEW[a] for k in TR[a][i]["retrieval"]["kept"])
            d = J[a][i]["corr"] - J["K0"][i]["corr"]; key = "hit" if hit else "nohit"
            r = row.setdefault(key, dict(n=0, up=0, down=0, dsum=0.0)); r["n"] += 1; r["up"] += d >= 1; r["down"] += d <= -1; r["dsum"] += J[a][i]["s"] - J["K0"][i]["s"]
        w2u = [i for i in ids if warned("K0", i) and not warned(a, i)]
        u2w = [i for i in ids if not warned("K0", i) and warned(a, i)]
        print(a, setname, {k: dict(n=v["n"], up=v["up"], down=v["down"], mean_ds=round(v["dsum"] / v["n"], 3)) for k, v in row.items()},
              "| warned->unwarned", len(w2u), "corr K0->K", round(sum(J["K0"][i]["corr"] for i in w2u) / max(1, len(w2u)), 2), "->", round(sum(J[a][i]["corr"] for i in w2u) / max(1, len(w2u)), 2),
              "| unwarned->warned", len(u2w))
