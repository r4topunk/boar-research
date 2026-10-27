#!/usr/bin/env python3
"""SEEDGEN standing field for paired runs (0 LLM calls). Usage: python3 -I same_answer.py <tracesA.jsonl> <tracesB.jsonl> [--ids file] [--label x]
Pairs by itemId. kept_unchanged = kept (title, section) sets equal (order-insensitive). same answer = exact string after whitespace
normalisation; first50 = first 50 whitespace tokens equal. prompt_same = timing.promptTokens equal AND not None (audit F8: None = no LLM call,
e.g. instant tier, is reported apart as kept_unchanged_no_llm, never as "same prompt"); kept compares the (title, section) multiset (Counter):
kept (title, section) equal does NOT mean the same context text (DENSECHUNK-ST2), so read same-answer among kept_unchanged & prompt_same
as the generation-determinism number and same-answer among kept_unchanged as the paired-run noise floor. Prints one JSON line + a summary."""
import json, sys, argparse, collections
ap = argparse.ArgumentParser(); ap.add_argument("a"); ap.add_argument("b"); ap.add_argument("--ids"); ap.add_argument("--label", default="")
x = ap.parse_args()
def tr(p): return {(t := json.loads(l))["itemId"]: t for l in open(p) if l.strip()}
A, B = tr(x.a), tr(x.b)
ids = sorted(set(A) & set(B))
if x.ids: keep = {l.strip() for l in open(x.ids) if l.strip()}; ids = [i for i in ids if i in keep]
norm = lambda s: " ".join((s or "").split())
kept = lambda t: collections.Counter((s.get("title"), s.get("section")) for s in (t.get("retrieval") or {}).get("kept") or [])
ans = lambda t: norm((t.get("answer") or {}).get("text"))
pt = lambda t: (t.get("timing") or {}).get("promptTokens")
def block(sel):
    n = len(sel); same = sum(ans(A[i]) == ans(B[i]) for i in sel); f50 = sum(ans(A[i]).split()[:50] == ans(B[i]).split()[:50] for i in sel)
    return {"n": n, "same_answer": same, "same_answer_share": round(same / n, 3) if n else None, "same_first50": f50, "same_first50_share": round(f50 / n, 3) if n else None}
ku = [i for i in ids if kept(A[i]) == kept(B[i])]
kp = [i for i in ku if pt(A[i]) is not None and pt(A[i]) == pt(B[i])]
kn = [i for i in ku if pt(A[i]) is None and pt(B[i]) is None]
out = {"label": x.label, "a": x.a, "b": x.b, "n_paired": len(ids), "only_a": len(set(A) - set(B)), "only_b": len(set(B) - set(A)),
       "errors": [sum(1 for i in ids if T[i].get("error")) for T in (A, B)],
       "all": block(ids), "kept_unchanged": block(ku), "kept_unchanged_prompt_same": block(kp),
       "kept_unchanged_no_llm": block(kn), "kept_unchanged_prompt_diff_n": len(ku) - len(kp) - len(kn),
       "diff_ids_kept_unchanged_prompt_same": [i for i in kp if ans(A[i]) != ans(B[i])]}
print(json.dumps(out))
k, q, a = out["kept_unchanged"], out["kept_unchanged_prompt_same"], out["all"]
print(f"{x.label or 'pair'}: kept-unchanged same-answer {k['same_answer']}/{k['n']}; of which same prompt length (LLM) {q['same_answer']}/{q['n']}, no LLM {out['kept_unchanged_no_llm']['same_answer']}/{out['kept_unchanged_no_llm']['n']}; "
      f"all items same-answer {a['same_answer']}/{a['n']} (first-50-tokens {a['same_first50']}/{a['n']})", file=sys.stderr)
