#!/usr/bin/env python3
"""exp-04 side-by-side on the same rows: Jev (frozen v2) vs precheck v2.2 vs claude -p judge, all against Plumb's hand labels.

- precheck v2.1 (rnd/lantern/tools/precheck.py, sha256 checked against lantern/data/precheck-v2.2-freeze.json), run
  unchanged per src/model group. Status -> 4 classes: pass -> correct; confident-wrong -> confident_wrong;
  refused -> refused; fail-missing / empty / missing -> wrong_or_incomplete_hedged.
- claude -p judge: only where it exists (iPhone runs 2-3, pairwise vs Opus+web, both orders). It gives no class, only
  rubric scores: binary correct := mean BOAR correctness over the two orders >= 4 (of 5). Reported on binary only.
Usage: python3 compare.py  (writes results/compare.md)
"""
import hashlib, json, os, subprocess, tempfile
from collections import defaultdict

B = "<workspace>"
LT = f"{B}/rnd/lantern"
freeze = json.load(open(f"{LT}/data/precheck-v2.2-freeze.json"))["sha256"]
for rel, h in freeze.items():
    assert hashlib.sha256(open(f"{LT}/{rel}", "rb").read()).hexdigest() == h, f"{rel} changed since the v2.2 freeze"
MAP = {"pass": "correct", "confident-wrong": "confident_wrong", "refused": "refused"}
C = ["correct", "confident_wrong", "wrong_or_incomplete_hedged", "refused"]


def rows(p):
    return [json.loads(l) for l in open(p)]


def precheck(group_rows):
    with tempfile.TemporaryDirectory() as d:
        runs, sub, js = f"{d}/r.jsonl", f"{d}/s.json", f"{d}/o.json"
        with open(runs, "w") as f:
            for r in group_rows:
                f.write(json.dumps({"queryId": r["queryId"], "answer": r["answer"], "declined": r["app_declined"]}) + "\n")
        json.dump({"ids": [r["queryId"] for r in group_rows]}, open(sub, "w"))
        subprocess.run(["python3", f"{LT}/tools/precheck.py", runs, "--subset", sub, "--json", js], check=True, capture_output=True, cwd=LT)
        return {x["id"]: MAP.get(x["status"], "wrong_or_incomplete_hedged") for x in json.load(open(js))}


def judge_binary():
    out = {}
    for src, f in (("P2", "qwen2.5-1.5b-instruct-q4km__iphone-14de107-device__vs__claude-code__opus.jsonl"),
                   ("P3", "qwen2.5-1.5b-instruct-q4km__iphone-14de107-device-vital5__vs__claude-code__opus.jsonl")):
        acc = defaultdict(list)
        for r in rows(f"{B}/rnd/plumb/data/{f}"):
            if r.get("ok") and r.get("mapped"):
                acc[r["queryId"]].append(r["mapped"]["boar"]["correctness"])
        for q, v in acc.items():
            out[(src, q)] = sum(v) / len(v) >= 4
    return out


def score(pairs):
    n = len(pairs)
    four = sum(h == p for h, p in pairs)
    binr = sum((h == "correct") == (p == "correct") for h, p in pairs)
    tp = sum(h == "confident_wrong" and p == "confident_wrong" for h, p in pairs)
    fp = sum(h != "confident_wrong" and p == "confident_wrong" for h, p in pairs)
    fn = sum(h == "confident_wrong" and p != "confident_wrong" for h, p in pairs)
    pr = f"{tp}/{tp + fp} = {tp / (tp + fp):.0%}" if tp + fp else "0/0"
    rc = f"{tp}/{tp + fn} = {tp / (tp + fn):.0%}" if tp + fn else "—"
    return f"{four}/{n} = {four / n:.0%}", f"{binr}/{n} = {binr / n:.0%}", pr, rc


L = ["# exp-04 side by side: Jev (frozen v2) vs precheck v2.2 vs claude -p judge (hand labels = truth)", ""]
jb = judge_binary()
for split, rp, pp in (("TEST (held out: run 4 Maple + baseline-mix 4B/Ling + 1.5B)", "rows-test.jsonl", "preds/v2-test.jsonl"),
                      ("TUNE (iPhone runs 2-3; Jev wording was tuned here), excluding the app's fixed-message declines", "rows-tune.jsonl", "preds/v2-tune.jsonl")):
    R = [r for r in rows(rp) if not r["app_declined"]]
    J = {(p["src"], p["model"], p["queryId"]): p["jev"] for p in rows(pp)}
    groups = defaultdict(list)
    for r in R:
        groups[(r["src"], r["model"])].append(r)
    pc = {}
    for g, gr in groups.items():
        for q, lab in precheck(gr).items():
            pc[(g[0], g[1], q)] = lab
    key = lambda r: (r["src"], r["model"], r["queryId"])
    L += [f"## {split}: n = {len(R)}", "", "| Instrument | 4-class | binary (correct vs not) | CW precision | CW recall | cost per 1M answers |", "|---|---|---|---|---|---|"]
    a = score([(r["hand4"], J[key(r)]) for r in R])
    L.append(f"| **Jev v2** | {a[0]} | {a[1]} | {a[2]} | {a[3]} | ~[usage detail removed] (measured) |")
    b = score([(r["hand4"], pc[key(r)]) for r in R])
    L.append(f"| precheck v2.2 (frozen; in-sample on run 4 Maple) | {b[0]} | {b[1]} | {b[2]} | {b[3]} | 0 (local regex) |")
    JR = [r for r in R if (r["src"], r["queryId"]) in jb]
    if JR:
        n = len(JR)
        bj = sum((r["hand4"] == "correct") == jb[(r["src"], r["queryId"])] for r in JR)
        bjj = sum((r["hand4"] == "correct") == (J[key(r)] == "correct") for r in JR)
        L.append(f"| claude -p judge (binary only, correctness ≥ 4/5) | — | {bj}/{n} = {bj / n:.0%} | — | — | CLI login (≈ 0.02–[usage detail removed] list price per pair) |")
        L.append(f"| Jev v2 on the same {n} judged rows | — | {bjj}/{n} = {bjj / n:.0%} | | | |")
    L.append("")
text = "\n".join(L)
print(text)
os.makedirs("results", exist_ok=True)
open("results/compare.md", "w").write(text + "\n")
