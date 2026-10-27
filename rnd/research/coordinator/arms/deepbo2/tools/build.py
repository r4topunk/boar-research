#!/usr/bin/env python3
"""DEEPBO2 build (criterion sha256 c7e2232f...): pairs.jsonl + prompts.jsonl from DT512 arm H traces s42/s43
on runs-cut6/judged.ids. Prompt template imported from select.py (frozen there). Prints numbers/hashes only."""
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:] = [p for p in sys.path if os.path.abspath(p or ".") != _HERE]
import json, re, hashlib, statistics, importlib.util

spec = importlib.util.spec_from_file_location("deepbo2_select", os.path.join(_HERE, "select.py"))
sel = importlib.util.module_from_spec(spec); spec.loader.exec_module(sel)

ROOT = os.path.abspath(os.path.join(_HERE, "../../../../../.."))
B = os.path.join(ROOT, "blind/V-para")
OUT = os.path.join(B, "runs-deepbo2")
CITE = re.compile(r"\[(\d+)\]")


def load(seed):
    with open(os.path.join(B, f"runs-dt512/dh-H-vpara-s{seed}.traces.jsonl")) as f:
        return {r["itemId"]: r for r in (json.loads(l) for l in f if l.strip())}


def toks(tr):
    g = [e for e in tr["events"] if e.get("kind") == "generation"]
    if len(g) != 1:
        raise SystemExit(f"generation events != 1 for {tr['itemId']}: {len(g)}")
    return g[0]["outputTokens"] - (g[0].get("reasoningTokens") or 0)


ids = [l.strip() for l in open(os.path.join(B, "runs-cut6/judged.ids")) if l.strip()]
T42, T43 = load(42), load(43)
os.makedirs(OUT, exist_ok=True)
pairs, prompts = [], []
for i in ids:
    a, b = T42[i], T43[i]
    if a["question"] != b["question"]:
        raise SystemExit(f"question mismatch {i}")
    ta, tb = a["answer"]["text"], b["answer"]["text"]
    pairs.append({"id": i, "question": a["question"], "a": ta, "b": tb, "lenA": toks(a), "lenB": toks(b),
                  "wordsA": len(ta.split()), "wordsB": len(tb.split()),
                  "citesA": len(set(CITE.findall(ta))), "citesB": len(set(CITE.findall(tb)))})
    prompts.append({"id": i, "order": "AB", "A": "s42", "B": "s43", "messages": sel.build_messages(a["question"], ta, tb)})
    prompts.append({"id": i, "order": "BA", "A": "s43", "B": "s42", "messages": sel.build_messages(a["question"], tb, ta)})
sha = {}
for name, rows in (("pairs.jsonl", pairs), ("prompts.jsonl", prompts)):
    p = os.path.join(OUT, name)
    with open(p, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    sha[name] = hashlib.sha256(open(p, "rb").read()).hexdigest()
plen = [sum(len(m["content"]) for m in p["messages"]) for p in prompts]
print(json.dumps({"nIds": len(pairs), "nPrompts": len(prompts), "sha256": sha, "promptCharsMedian": statistics.median(plen),
                  "promptCharsMax": max(plen), "promptCharsMin": min(plen),
                  "selectPySha256": hashlib.sha256(open(os.path.join(_HERE, "select.py"), "rb").read()).hexdigest()}))
