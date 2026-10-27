# SFT4B parity analysis. usage:
#   python p_compare.py p0 <a.jsonl> <b.jsonl>                      -> byte-identical count (P0 / determinism baseline)
#   python p_compare.py p2 <M0> <M1> <G0> <G1> [hf_templates.jsonl] -> P2 gate (G1!=G0 >= 8/20; same-sign effect; M1/G1 agree >= M0/G0 - 2)
import json, sys, re, statistics as st
ld = lambda p: {r["pid"]: r for r in map(json.loads, open(p))}
def fdiv(a, b):  # first divergence token index (by whitespace tokens)
    a, b = a.split(), b.split(); n = min(len(a), len(b))
    return next((i for i in range(n) if a[i] != b[i]), n)
mode = sys.argv[1]
if mode == "p0":
    a, b = ld(sys.argv[2]), ld(sys.argv[3]); ids = sorted(a)
    same = [i for i in ids if i in b and a[i]["text"] == b[i]["text"] and a[i].get("tokens") == b[i].get("tokens")]
    tpl = sum(a[i]["template"] == b[i]["template"] for i in ids)
    out = {"n": len(ids), "identical": len(same), "template_identical": tpl, "differ": [i for i in ids if i not in same]}
    out["PASS"] = len(same) == len(ids) == 10 if len(ids) == 10 else len(same) == len(ids)
    print(json.dumps(out)); sys.exit(0 if out["PASS"] else 2)
M0, M1, G0, G1 = (ld(p) for p in sys.argv[2:6]); ids = sorted(G0)
words = lambda t: len(t.split()); cites = lambda t: len(re.findall(r"\[\d+\]", t))
def eff(X0, X1):
    dl = [words(X1[i]["text"]) - words(X0[i]["text"]) for i in ids]; dc = [cites(X1[i]["text"]) - cites(X0[i]["text"]) for i in ids]
    return {"median_len0": st.median(words(X0[i]["text"]) for i in ids), "median_len1": st.median(words(X1[i]["text"]) for i in ids),
            "median_dlen": st.median(dl), "mean_dcites": sum(dc) / len(dc), "changed": sum(X0[i]["text"] != X1[i]["text"] for i in ids)}
eM, eG = eff(M0, M1), eff(G0, G1)
sgn = lambda x: (x > 0) - (x < 0)
same_sign = sgn(eM["median_dlen"]) == sgn(eG["median_dlen"]) and sgn(eM["mean_dcites"]) == sgn(eG["mean_dcites"])
agree0 = sum(M0[i]["text"].strip() == G0[i]["text"].strip() for i in ids); agree1 = sum(M1[i]["text"].strip() == G1[i]["text"].strip() for i in ids)
fd0 = st.median(fdiv(M0[i]["text"], G0[i]["text"]) for i in ids); fd1 = st.median(fdiv(M1[i]["text"], G1[i]["text"]) for i in ids)
tpl_ok = None
if len(sys.argv) > 6:
    H = ld(sys.argv[6]); tpl_ok = sum(H[i]["template"] == G0[i]["template"] for i in ids)
tps = lambda X: st.median(X[i]["timings"]["predicted_per_second"] for i in ids if X[i].get("timings"))
out = {"n": len(ids), "mlx": eM, "gguf": eG, "same_sign": same_sign, "exact_agree_M0G0": agree0, "exact_agree_M1G1": agree1,
       "median_first_div_M0G0": fd0, "median_first_div_M1G1": fd1, "template_match_hf_vs_server": tpl_ok,
       "tok_s_G0": tps(G0), "tok_s_G1": tps(G1)}
c1 = eG["changed"] >= 8; c3 = agree1 >= agree0 - 2 or fd1 >= fd0 - 2
out["checks"] = {"G1_ne_G0_ge8": c1, "same_sign": same_sign, "agreement": c3}
out["PASS"] = c1 and same_sign and c3
out["note"] = "agreement uses exact match; first-divergence median is reported alongside (tie-break only if exact agreement fails)"
print(json.dumps(out, indent=1)); sys.exit(0 if out["PASS"] else 2)
