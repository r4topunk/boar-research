#!/usr/bin/env python3
"""CITEFIX step 1: inventory of citation forms in stored traces (0 LLM).
Usage: python3 -I inventory.py <traces.jsonl>...  Prints per-run counts of citation patterns in (a) the final answer.text,
(b) the stored token stream (complete only when no tokens-elided event), and the CT-1/attribution reason codes."""
import json, re, sys, collections
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
PAT = {
  "[n]": r"\[\d+\]",
  "[n,m]/[n-m] list": r"\[\d+(?:\s*[,;–-]\s*\d+)+\]",
  "[Source n]": r"\[\s*(?:source|src|doc(?:ument)?|passage|ref(?:erence)?|context)\s*#?\d+[^\]]*\]",
  "(Source n)": r"\(\s*(?:source|passage|doc(?:ument)?|ref)\s*#?\d+[^)]*\)",
  "bare Source n": r"(?<![\[(])\b(?:source|passage|document)\s*#?\d+\b",
  "(n) bare": r"\((\d{1,2})\)",
  "superscript": r"[¹²³⁰-⁹]",
  "^n / [^n]": r"\[\^\d+\]|\^\d+",
  "fullwidth 【n】": r"【\d+】",
  "{n}/<n>": r"\{\d+\}|<\d+>",
}
def stream(d):
    ev = d.get("events") or []
    full = not any(e.get("kind") == "tokens-elided" for e in ev)
    return "".join(e.get("text", "") for e in ev if e.get("type") == "token"), full
def run(path):
    C = collections.Counter(); S = collections.Counter(); R = collections.Counter(); n = 0; nfull = 0; titles = 0; ex = collections.defaultdict(list)
    for l in open(path):
        d = json.loads(l); n += 1
        t = d["answer"]["text"] or ""; s, full = stream(d); nfull += full
        rc = d["route"].get("reasonCodes", [])
        for k, p in PAT.items():
            if re.search(p, t, re.I): C[k] += 1; len(ex[k]) < 3 and ex[k].append((d["itemId"], re.search(p, t, re.I).group(0)))
            if re.search(p, s, re.I): S[k] += 1
        if not any(re.search(p, t, re.I) for p in PAT.values()): C["none"] += 1
        if not any(re.search(p, s, re.I) for p in PAT.values()): S["none"] += 1
        for c in rc:
            if c.startswith(("citations:", "grounding:compact-decline-released", "grounding:model-references")): R[re.sub(r"-[\d-]+$", "", c)] += 1
        shown = list(d["answer"].get("shown") or [])
        if any(ti and ti.split(": ", 1)[-1].lower() in t.lower() for ti in shown): titles += 1
    print(f"== {path.split('/')[-1]}  n {n}  full streams {nfull}  answers naming a shown source title {titles}")
    print("  final text :", dict(C)); print("  stream     :", dict(S)); print("  reasonCodes:", dict(R))
    for k, v in ex.items():
        if k != "[n]": print("   ex", k, v)
for p in sys.argv[1:]: run(p)
