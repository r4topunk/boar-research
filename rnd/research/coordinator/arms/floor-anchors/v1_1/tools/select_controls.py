#!/usr/bin/env python3
"""JUDGE-V1_1 control selection (0 LLM). From the 97 cached mini K0 MAIN control answers (lp-screens/control lpctl-K0-main-s42) and their three
existing judge.v1-low judgments (repeat 1 = lp-screens/control/judgments, repeats 2-3 = judge-v2/v1/rep{2,3}):
  v1 CE per repeat = correctness averaged over both orders <= 1.5 (judge-v2 analyze.py); WRONG = v1 CE in >= 2 of 3 repeats;
  CORRECT = not WRONG and mean correctness over the 3 repeats >= 3.5.
  Take the first 20 of each by sha256(id) hex order -> data/controls-40.tsv (id, set, group). RETEST = first 10 of each group -> data/retest-20.ids.
Also prints the v1 test-retest reference on the 20 retest ids: mean over items of the sample SD (ddof 1) of n = (s - 1)/4 over v1 repeats 1-2."""
import json, glob, hashlib, statistics as st, os
A = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))); H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = f"{A}/lp-screens/control"; J = f"{A}/judge-v2"
rd = lambda p: [json.loads(l) for l in open(p) if l.strip()]
def rep(files):
    by = {}
    for f in files:
        u = f.split("lpctl-K0-main-s42-")[-1].split("rep")[-1].split(".judgments")[0]
        for r in rd(f):
            if r.get("ok"): by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]; by[r["queryId"]]["_set"] = u.split("-", 1)[-1] if u.startswith(("2-", "3-")) else u
    out = {}
    for i, v in by.items():
        ms = [v[o] for o in ("boarA", "boarB")]
        s = sum(sum(m["boar"].values()) / 3 for m in ms) / 2
        out[i] = dict(s=s, n=(s - 1) / 4, corr=sum(m["boar"]["correctness"] for m in ms) / 2, set=v["_set"])
    return out
R = [rep(sorted(glob.glob(f"{C}/judgments/lpctl-K0-main-s42-*.judgments.jsonl")))] + [rep(sorted(glob.glob(f"{J}/v1/rep{r}-*.judgments.jsonl"))) for r in (2, 3)]
ids = sorted(R[0]); assert len(ids) == 97 and all(set(Rr) == set(ids) for Rr in R)
h = lambda i: hashlib.sha256(i.encode()).hexdigest()
wrong = sorted([i for i in ids if sum(Rr[i]["corr"] <= 1.5 for Rr in R) >= 2], key=h)
correct = sorted([i for i in ids if i not in wrong and st.mean(Rr[i]["corr"] for Rr in R) >= 3.5], key=h)
print(f"pool wrong {len(wrong)} correct {len(correct)}")
W, Cc = wrong[:20], correct[:20]
with open(f"{H}/data/controls-40.tsv", "w") as f:
    for g, L in (("correct", Cc), ("wrong", W)):
        for i in L: f.write(f"{i}\t{R[0][i]['set']}\t{g}\n")
rt = Cc[:10] + W[:10]
open(f"{H}/data/retest-20.ids", "w").write("".join(i + "\n" for i in rt))
sd12 = st.mean(st.stdev([R[0][i]["n"], R[1][i]["n"]]) for i in rt); sd123 = st.mean(st.stdev([Rr[i]["n"] for Rr in R]) for i in rt)
print(f"v1 retest-20 mean item SD: repeats 1-2 {sd12:.4f}; repeats 1-3 {sd123:.4f}")
print("sets", {s: sum(1 for i in W + Cc if R[0][i]["set"] == s) for s in ("v01", "qa-cooking-se", "qa-money-se")})
