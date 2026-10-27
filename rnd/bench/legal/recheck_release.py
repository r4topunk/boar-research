#!/usr/bin/env python3
"""Re-check rnd/bench/release-v0/ after the legal fixes (release-v0-check.md). Read-only.

    python3 rnd/bench/legal/recheck_release.py            # from <workspace>

Checks, each printed as ok/FAIL with evidence:
  1. leak:        no 80-char window of the 60 reference texts or the judge rationales in any package file
  1b. calib-40:   no 40-char window of the references in data/calibration/ (one-line summaries)
  2. excerpts:    every file that carries a BOAR instant-route excerpt (Wikipedia/Wikivoyage/OSM) sits under a
                  CC BY-SA license file or a NOTICE row naming it
  3. dup-safety:  code/safety data files are either gone or covered by a NOTICE "data under code/" row
  4. ogl:         NOTICE carries the OGL v3 statement for the NHS quotations
  5. labels:      no "hand label(s)" / "manual label(s)" wording left; results/hand-labelled/ renamed
  6. authors:     AUTHORS exists; copyright line no longer only "the Offline Research Bench contributors"
  7. manifest:    MANIFEST.sha256 matches the files on disk
Exit 1 if any check fails.
"""
import glob, hashlib, json, os, re, sys

BENCH = "rnd/bench"
PKG = os.environ.get("RELEASE_PKG", f"{BENCH}/release-v0")
# Must never ship: the Jev input carrying the full frozen references (rnd/bench/jev/items.jsonl, 204 rows).
FORBIDDEN_SHA = {"afce4403b5a42dd394e300f92ff49f52f26881419379e43776688d31486e290c": "rnd/bench/jev/items.jsonl (full references)"}
RUNS = ["rnd/plumb/data/qwen2.5-1.5b-instruct-q4km__iphone-14de107-device-vital5.jsonl",
        "rnd/plumb/data/qwen2.5-1.5b-instruct-q4km__iphone-14de107-bench-p3-8.jsonl"]

norm = lambda t: " ".join(t.split())
def wins(t, w, step):
    t = norm(t)
    return [t[i:i + w] for i in range(0, max(1, len(t) - w), step) if len(t[i:i + w]) == w]

def strings(p):
    out = []
    def walk(x):
        if isinstance(x, str): out.append(x)
        elif isinstance(x, dict): [walk(v) for v in x.values()]
        elif isinstance(x, list): [walk(v) for v in x]
    try:
        if p.endswith(".jsonl"):
            for l in open(p, encoding="utf-8"):
                if l.strip(): walk(json.loads(l))
        elif p.endswith(".json"):
            walk(json.load(open(p, encoding="utf-8")))
        else:
            out.append(open(p, encoding="utf-8", errors="ignore").read())
    except Exception:
        out.append(open(p, encoding="utf-8", errors="ignore").read())
    return norm(" ".join(out))

files = sorted(os.path.join(r, f) for r, _, fs in os.walk(PKG) for f in fs)
text = {p: strings(p) for p in files}
rel = lambda p: os.path.relpath(p, PKG)
notice = open(f"{PKG}/NOTICE", encoding="utf-8").read() if os.path.exists(f"{PKG}/NOTICE") else ""
fails = 0
def report(name, ok, detail):
    global fails
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {name}: {detail}")

# 1. leak
W = set()
for l in open(f"{BENCH}/refs/v0/claude-code__opus.jsonl", encoding="utf-8"):
    r = json.loads(l)
    for k in ("answer", "rawResult"):
        if isinstance(r.get(k), str): W |= set(wins(r[k], 80, 150))
for f in glob.glob(f"{BENCH}/judge/v0/*.jsonl"):
    for l in open(f, encoding="utf-8"):
        def walk(x):
            if isinstance(x, str) and len(x) > 120: W.update(wins(x, 80, 150))
            elif isinstance(x, dict): [walk(v) for v in x.values()]
            elif isinstance(x, list): [walk(v) for v in x]
        walk(json.loads(l))
leaks = {rel(p): n for p, s in text.items() if (n := sum(w in s for w in W))}
report("leak", not leaks, f"{len(files)} files x {len(W)} windows, hits: {leaks or 0}")

# 1b. calibration files: stricter 40-char windows (1-line reference summaries live there)
W40 = set()
for l in open(f"{BENCH}/refs/v0/claude-code__opus.jsonl", encoding="utf-8"):
    r = json.loads(l)
    t = norm((r.get("answer") or "") + " " + (r.get("rawResult") or ""))
    W40.update(t[i:i + 40] for i in range(0, max(1, len(t) - 39)))
# Only the reference *summaries* get the strict 40-char test: JSON values under keys mentioning ref/summary, and
# markdown/text lines containing "Reference". System answers and questions coincide with reference phrasing on
# names and plain sentences at 40 chars ("France won the 2018 FIFA World Cup. They"), so they stay on the 80-char scan.
def summaries(p):
    out = []
    def walk(x, key=""):
        if isinstance(x, str):
            if (re.search(r"ref|summary", key, re.I) and not re.search(r"sources|sha|url|path|file", key, re.I)
                    and not x.startswith("http") and not re.fullmatch(r"[0-9a-f]{64}", x)):
                out.append(x)
        elif isinstance(x, dict): [walk(v, k) for k, v in x.items()]
        elif isinstance(x, list): [walk(v, key) for v in x]
    if p.endswith((".json", ".jsonl")):
        try:
            if p.endswith(".jsonl"):
                for l in open(p, encoding="utf-8"):
                    if l.strip(): walk(json.loads(l))
            else: walk(json.load(open(p, encoding="utf-8")))
        except Exception: pass
    else:
        out += [l for l in open(p, encoding="utf-8", errors="ignore") if re.search(r"reference \(1 line\)", l, re.I)]
    return norm(" ".join(out))
# Both summary sets (Lantern's, and the neutral subagent's from PANEL.md O1) may ship in calibration/agent-label/panel
# folders, or as "Reference (1 line)" lines in any markdown file.
in_scope = lambda r: (re.search(r"calibration|agent-label|panel|rater|neutral|jev", r, re.I) or r.endswith(".md")) and "LICENSE" not in r
cal = {rel(p): summaries(p) for p in files if in_scope(rel(p))}
cal_hits = {}
for p, s in cal.items():
    n = sum(1 for i in range(0, max(1, len(s) - 39)) if s[i:i + 40] in W40)
    if n: cal_hits[p] = n
report("calib-40", not cal_hits, f"{len(cal)} files in scope (summary fields/lines only), 40-char reference windows: {cal_hits or 0}")

# 1c. full references must not ship: the Jev items.jsonl by hash or name, or any "reference" field > 400 chars
bad = []
for p in files:
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    if h in FORBIDDEN_SHA:
        bad.append(f"{rel(p)} = {FORBIDDEN_SHA[h]}")
    elif re.search(r"(^|/)items\.jsonl$", rel(p)):
        bad.append(f"{rel(p)} (name)")
    elif p.endswith((".json", ".jsonl")):
        try:
            rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if p.endswith(".jsonl") else [json.load(open(p, encoding="utf-8"))]
        except Exception:
            rows = []
        def walk(x, key=""):
            if isinstance(x, dict): [walk(v, k) for k, v in x.items()]
            elif isinstance(x, list): [walk(v, key) for v in x]
            elif isinstance(x, str) and re.fullmatch(r"ref|ref1|reference|reference_text|ref_answer", key, re.I) and len(x) > 400:
                bad.append(f"{rel(p)} ('{key}' field, {len(x)} chars)")
        for r in rows: walk(r)
report("full-refs", not bad, f"forbidden full-reference files/fields: {sorted(set(bad))[:6] or 'none'}")

# 2. excerpts -> license
ex = {}
for f in RUNS:
    for l in open(f, encoding="utf-8"):
        r = json.loads(l)
        if r.get("tier") == "instant" and r["queryId"] != "dng-001":
            ex[r["queryId"]] = wins(r["answer"], 60, 40)
carriers = {rel(p): [q for q, ws in ex.items() if any(w in s for w in ws)] for p, s in text.items()}
carriers = {p: q for p, q in carriers.items() if q}
def covered(path):
    d = os.path.dirname(os.path.join(PKG, path))
    while d.startswith(PKG):
        lfs = glob.glob(os.path.join(d, "LICENSE*"))
        if lfs:  # the nearest folder with a LICENSE decides; only its header (first 3 non-empty lines) counts
            head = lambda lf: " ".join([l for l in open(lf, encoding="utf-8", errors="ignore").read().splitlines() if l.strip()][:3])
            return any(re.search(r"BY-SA|ShareAlike", head(lf), re.I) for lf in lfs)
        d = os.path.dirname(d)
    # a NOTICE row naming the path (or its folder) next to CC BY-SA, or a short attributed quotation
    for line in notice.splitlines():
        if re.search(r"BY-SA", line) and (path in line or os.path.dirname(path) + "/" in line):
            return True
    return False
quote_ok = lambda p: p.endswith((".md", ".py")) or "/results/" in "/" + p or p.startswith("results/")
unc = [p for p in carriers if not covered(p) and not quote_ok(p)]
# inline attribution, or a NOTICE paragraph that names the file or its top folder and attributes Wikivoyage CC BY-SA
# (CC BY-SA 4.0 §3(a)(2): attribution "in any reasonable manner based on the medium")
paras = [norm(x) for x in re.split(r"\n\s*\n", notice)]
def notice_attr(path):
    top = path.split("/")[0] + ("/" if "/" in path else "")
    return any(("Wikivoyage" in x and "CC BY-SA" in x and (path in x or top in x)) for x in paras)
attrib = [p for p in carriers if quote_ok(p) and not re.search(r"Wikivoyage[^\n]{0,80}CC BY-SA|CC BY-SA[^\n]{0,80}Wikivoyage", text[os.path.join(PKG, p)]) and not notice_attr(p)]
report("excerpts", not unc, f"{len(carriers)} carrier files; not under CC BY-SA: {unc or 'none'}")
report("excerpt-attribution", not attrib, f"quoting files without a 'Wikivoyage … CC BY-SA' line: {attrib or 'none'}")

# 3. dup safety
dups = []
for f in glob.glob(f"{PKG}/code/safety/*.json*"):
    twin = f"{PKG}/data/safety/{os.path.basename(f)}"
    if os.path.exists(twin) and hashlib.sha256(open(f, "rb").read()).digest() == hashlib.sha256(open(twin, "rb").read()).digest():
        dups.append(rel(f))
row = re.search(r"code/safety", notice) and re.search(r"(CC BY|data)", notice)
report("dup-safety", not dups or bool(row), f"identical copies: {dups or 'none'}; NOTICE row for data under code/: {bool(row)}")

# 4. OGL
report("ogl", "Open Government Licence v3.0" in notice, "NOTICE has the OGL v3 statement" if "Open Government Licence v3.0" in notice else "missing in NOTICE")

# 5. labels
# user-facing text only: docs, report cards, data "_about" fields; not code identifiers, the vendored BOAR code or MANIFEST paths
facing = lambda p: (p.endswith(".md") or p.startswith("results/") or p.startswith("data/")) and not p.startswith("code/vendor/")
hl = {rel(p): len(re.findall(r"\b(hand|manual)[- ]label", s, re.I)) for p, s in text.items() if facing(rel(p))}
hl = {p: n for p, n in hl.items() if n}
dir_old = os.path.isdir(f"{PKG}/results/hand-labelled")
report("labels", not hl and not dir_old, f"wording hits: {hl or 'none'}; results/hand-labelled/ present: {dir_old}")

# 6. authors / copyright
has_authors = any(os.path.exists(f"{PKG}/{n}") for n in ("AUTHORS", "AUTHORS.md"))
only_collective = bool(re.search(r"Copyright 2026 the Offline Research Bench contributors\s*$", notice, re.M))
report("authors", has_authors and not only_collective, f"AUTHORS: {has_authors}; collective-only copyright line: {only_collective}")

# 7. manifest
mf = f"{PKG}/MANIFEST.sha256"
bad = []
if os.path.exists(mf):
    for line in open(mf, encoding="utf-8"):
        parts = line.split()
        if len(parts) >= 2:
            h, p = parts[0], parts[-1].lstrip("*")
            fp = os.path.join(PKG, p)
            if not os.path.exists(fp) or hashlib.sha256(open(fp, "rb").read()).hexdigest() != h:
                bad.append(p)
report("manifest", os.path.exists(mf) and not bad, f"mismatches: {bad[:8] or 'none'}{' …' if len(bad) > 8 else ''}")

sys.exit(1 if fails else 0)
