"""CHATFAIL S1 statistics (python3 -I; numpy). Usage: stats.py <model m4|m1> [tag]  -> markdown tables on stdout + out/stats-<model>.json
Primary: fulfilled on capability turns per arm (+ split code/format/translate), refusal (capability turns / non-capability turns), snowball P(refuse_t | refuse_t-1),
deltas A1-C0, A2-C0, A3-A2 with chat-cluster bootstrap CIs (2000 resamples, seed 1), and the criterion's verdict clauses for fulfilled / refusal / L4."""
import json, sys, collections, numpy as np
model = sys.argv[1]; tag = ("-" + sys.argv[2]) if len(sys.argv) > 2 else ""
D = __file__.rsplit("/", 1)[0] + "/out/"
rows = [json.loads(l) for l in open(D + f"scored-{model}{tag}.jsonl") if l.strip()]
ARMS = [a for a in ("C0", "A1", "A2", "A3") if any(r["arm"] == a for r in rows)]
chats = sorted({r["chat"] for r in rows}); by = {a: {c: [r for r in rows if r["arm"] == a and r["chat"] == c] for c in chats} for a in ARMS}
def rate(a, cs, f, sel):
    num = den = 0
    for c in cs:
        for r in by[a][c]:
            if sel(r): den += 1; num += 1 if f(r) else 0
    return num / den if den else float("nan")
def snow(a, cs):
    num = den = 0
    for c in cs:
        rs = by[a][c]
        for i in range(1, len(rs)):
            if rs[i - 1]["refusal"]: den += 1; num += 1 if rs[i]["refusal"] else 0
    return num / den if den else float("nan"), den
def boot(fn, B=2000, seed=1):
    rng = np.random.default_rng(seed); n = len(chats); v = []
    for _ in range(B):
        cs = [chats[i] for i in rng.integers(0, n, n)]; x = fn(cs)
        if x == x: v.append(x)
    lo, hi = np.percentile(v, [2.5, 97.5]); return round(float(lo), 3), round(float(hi), 3)
cap = lambda r: r["cap"]; ful = lambda r: r["fulfilled"]; ref = lambda r: r["refusal"]
SPL = {"all capability": cap, "code": lambda r: r["cap"] and r["expected_intent"] == "code", "format": lambda r: r["cap"] and r["expected_intent"] == "format", "translate": lambda r: r["cap"] and r["expected_intent"] == "translate"}
out = {"model": model, "chats": len(chats), "arms": ARMS, "fulfilled": {}, "refusal": {}, "snowball": {}, "delta": {}}
print(f"### {model.upper()} (chat-cluster bootstrap 2000, seed 1; {len(chats)} chats)\n")
print("| arm | fulfilled all (n=" + str(sum(1 for r in rows if r['arm']==ARMS[0] and r['cap'])) + ") | code | format | translate | refusal on capability | refusal on other turns | snowball P(ref_t \\| ref_t-1) |\n|---|---|---|---|---|---|---|---|")
for a in ARMS:
    cells = []
    for name, sel in SPL.items():
        p = rate(a, chats, ful, sel); ci = boot(lambda cs: rate(a, cs, ful, sel)); out["fulfilled"].setdefault(a, {})[name] = [round(p, 3), *ci]
        n = sum(1 for c in chats for r in by[a][c] if sel(r)); cells.append(f"{p:.3f} ({ci[0]:.3f}-{ci[1]:.3f})" + ("" if name == "all capability" else f" n={n}"))
    pr = rate(a, chats, ref, cap); cr = boot(lambda cs: rate(a, cs, ref, cap)); po = rate(a, chats, ref, lambda r: not r["cap"]); co = boot(lambda cs: rate(a, cs, ref, lambda r: not r["cap"]))
    ps, nd = snow(a, chats); cs_ = boot(lambda cs: snow(a, cs)[0])
    out["refusal"][a] = {"capability": [round(pr, 3), *cr], "other": [round(po, 3), *co]}; out["snowball"][a] = [round(ps, 3), *cs_, nd]
    print(f"| {a} | " + " | ".join(cells) + f" | {pr:.3f} ({cr[0]:.3f}-{cr[1]:.3f}) | {po:.3f} ({co[0]:.3f}-{co[1]:.3f}) | {ps:.3f} ({cs_[0]:.3f}-{cs_[1]:.3f}) n={nd} |")
print("\n| delta (same chats) | fulfilled all | code | format | translate | refusal on capability | snowball |\n|---|---|---|---|---|---|---|")
for hi, lo in (("A1", "C0"), ("A2", "C0"), ("A3", "A2")):
    if hi not in ARMS or lo not in ARMS: continue
    cells = []
    for name, sel in SPL.items():
        f = lambda cs: rate(hi, cs, ful, sel) - rate(lo, cs, ful, sel); d = f(chats); ci = boot(f); out["delta"].setdefault(f"{hi}-{lo}", {})[name] = [round(d, 3), *ci]; cells.append(f"{d:+.3f} ({ci[0]:+.3f}..{ci[1]:+.3f})")
    f = lambda cs: rate(hi, cs, ref, cap) - rate(lo, cs, ref, cap); d = f(chats); ci = boot(f); out["delta"][f"{hi}-{lo}"]["refusal"] = [round(d, 3), *ci]; cells.append(f"{d:+.3f} ({ci[0]:+.3f}..{ci[1]:+.3f})")
    f = lambda cs: snow(hi, cs)[0] - snow(lo, cs)[0]; d = f(chats); ci = boot(f); out["delta"][f"{hi}-{lo}"]["snowball"] = [round(d, 3), *ci]; cells.append(f"{d:+.3f} ({ci[0]:+.3f}..{ci[1]:+.3f})")
    print(f"| {hi} - {lo} | " + " | ".join(cells) + " |")
tot = {a: sum(r["tokens"] for r in rows if r["arm"] == a) for a in ARMS}; cut = {a: sum(1 for r in rows if r["arm"] == a and r["finish_reason"] == "length") for a in ARMS}
emp = {a: sum(1 for r in rows if r["arm"] == a and not r["answer"].strip()) for a in ARMS}
print(f"\ngenerated tokens {tot}; answers cut at 512 {cut}; empty answers {emp}")
json.dump(out, open(D + f"stats-{model}{tag}.json", "w"), indent=1)
