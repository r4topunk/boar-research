#!/usr/bin/env python3
"""PACK-NIST converter: NIST PDFs (pdftotext -layout) + CSRC glossary export -> builder JSONL + manifest.json.
Sections come from each PDF's outline (qpdf --json outlines): numbered depth <= 2 (and Abstract, Appendix X) open a doc,
deeper entries become '## ' headings inside it. Front matter before the first kept heading, Contents/Lists, References
and Index are dropped. Running headers (lines repeated on >= 15 % of pages), page numbers, the draft's line numbers
and 'available free of charge' lines are removed; runs of >= 3 spaces (layout columns) become ' · '.
Usage: python3 -I nist_to_jsonl.py <raw dir with PDFs + glossary-export.zip> <out dir>
"""
import collections, json, os, re, subprocess, sys, zipfile, hashlib

RAW, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
LIC = "Public domain in the US (work of the US government, 17 U.S.C. 105; NIST: foreign rights licensed royalty-free for reprint and derivative works). Source: NIST"
DOCS = [  # file, short id, full title, date, url
    ("NIST.FIPS.203.pdf", "FIPS 203", "Module-Lattice-Based Key-Encapsulation Mechanism Standard (ML-KEM)", "2024-08-13", "https://doi.org/10.6028/NIST.FIPS.203"),
    ("NIST.FIPS.204.pdf", "FIPS 204", "Module-Lattice-Based Digital Signature Standard (ML-DSA)", "2024-08-13", "https://doi.org/10.6028/NIST.FIPS.204"),
    ("NIST.FIPS.205.pdf", "FIPS 205", "Stateless Hash-Based Digital Signature Standard (SLH-DSA)", "2024-08-13", "https://doi.org/10.6028/NIST.FIPS.205"),
    ("NIST.FIPS.186-5.pdf", "FIPS 186-5", "Digital Signature Standard (DSS: RSA, ECDSA, EdDSA)", "2023-02-03", "https://doi.org/10.6028/NIST.FIPS.186-5"),
    ("NIST.SP.800-208.pdf", "NIST SP 800-208", "Recommendation for Stateful Hash-Based Signature Schemes (LMS, HSS, XMSS)", "2020-10-29", "https://doi.org/10.6028/NIST.SP.800-208"),
    ("NIST.IR.8547.ipd.pdf", "NIST IR 8547 (Initial Public Draft)", "Transition to Post-Quantum Cryptography Standards (draft)", "2024-11-12", "https://doi.org/10.6028/NIST.IR.8547.ipd"),
]
BASE = 16_000_000_000  # page_id = BASE + doc# * 1e6 + seq ; glossary = BASE + 9e6 + seq
DROP = re.compile(r"^(?:appendix\s+[A-Z][\s.:—–-]*)?(preamble|foreword|contents|table of contents|list of .*|references|index|bibliography|acknowledg.*|errata.*|document history.*|change log.*)$", re.I)
NUM = re.compile(r"^((?:\d+)(?:\.\d+)*)\.?\s+(.*)$")
APPX = re.compile(r"^appendix\s+([A-Z])\b[\s.:—–-]*(.*)$", re.I)
SUBAPPX = re.compile(r"^([A-Z](?:\.\d+)+)\.?\s+(.*)$")
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())


def outline(pdf):
    j = json.loads(subprocess.run(["qpdf", "--json", "--json-key=outlines", pdf], capture_output=True, text=True).stdout)
    flat = []
    def walk(o):
        for x in o:
            flat.append((x["title"].strip(), x.get("destpageposfrom1"))); walk(x.get("kids", []))
    walk(j["outlines"]); return flat


def classify(title):
    t = re.sub(r"\s+", " ", title).strip()
    if DROP.match(t): return ("drop", 1, t)
    m = NUM.match(t)
    if m: return ("keep", len(m.group(1).split(".")), t)
    m = APPX.match(t)
    if m: return ("keep", 1, t)
    m = SUBAPPX.match(t)
    if m: return ("keep", len(m.group(1).split(".")), t)
    if t.lower() == "abstract": return ("keep", 1, "Abstract and announcement")
    if t.lower() == "keywords": return ("cont", 9, t)
    return ("root", 0, t)  # document title roots and other unnumbered entries: boundary only


def pages_of(pdf, is_draft):
    txt = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout
    pages = [p.split("\n") for p in txt.split("\f")]
    if is_draft:  # IR ipd: strip the review line numbers
        pages = [[re.sub(r"^\s{0,6}\d{1,4}(\s{2,}|$)", "", l) for l in p] for p in pages]
    key = lambda l: re.sub(r"\d+", "#", re.sub(r"\s+", " ", l.strip()))
    cnt = collections.Counter(k for p in pages for k in {key(l) for l in p if l.strip()})
    rep = {k for k, c in cnt.items() if c >= max(3, 0.15 * len(pages))}
    out = []
    for p in pages:
        q = []
        for l in p:
            s = l.strip()
            if not s: q.append(""); continue
            if key(l) in rep: continue
            if re.fullmatch(r"[ivxlc]+|\d{1,3}", s): continue
            if "available free of charge from" in s or s.startswith("https://doi.org/10.6028/") and len(s) < 60: continue
            s = re.sub(r"\s{3,}", " · ", s); s = re.sub(r"\s{2}", " ", s)
            s = re.sub(r"^[•▪]\s*(· )?", "- ", s)
            if s[0] in "#|": s = "​" + s
            q.append(s)
        out.append(q)
    return out


def find_line(page, title):
    m = re.match(r"^(appendix\s+[a-z]|[a-z0-9]+(?:\.\d+)*)\.?\s*(.*)$", title, flags=re.I)
    if m:
        full = norm(m.group(1)) + norm(m.group(2))[:20]
        for i, l in enumerate(page):
            if norm(l).startswith(full): return i
    t = norm(re.sub(r"^(appendix\s+[a-z]|[a-z0-9]+(\.\d+)*)\.?\s*", "", title, flags=re.I))[:30]
    for i, l in enumerate(page):
        n = norm(l)
        if t and t in n[:len(t) + 12]: return i
    return None


def clean_body(lines):
    s = "\n".join(lines)
    s = re.sub(r"\n{3,}", "\n\n", s).strip()
    return s


rows, man = [], []
stats = {"docs": {}}
for di, (fn, short, full, date, url) in enumerate(DOCS):
    pdf = os.path.join(RAW, fn)
    pages = pages_of(pdf, "ipd" in fn)
    ents = []
    for title, pg in outline(pdf):
        kind, depth, t = classify(title)
        if pg is None: continue
        i = find_line(pages[pg - 1], t)
        ents.append([kind, depth, t, pg - 1, 0 if i is None else i, i is not None])
    # sort by position; boundaries are every entry
    ents.sort(key=lambda e: (e[3], e[4]))
    seq, cur, n_found = 0, None, sum(e[5] for e in ents)
    def flush():
        global seq
        if not cur: return
        body = clean_body(cur["lines"])
        if len(body) < 120: return
        seq_id = BASE + di * 1_000_000 + len(stats["docs"].setdefault(short, []))
        title = f"{short} — {cur['title']}"
        text = f"{short}: {full}. NIST, {date}.\n\n{body}"
        rows.append({"page_id": seq_id, "title": title, "text": text, "source": "usgov", "url": url, "license": LIC,
                     "attribution": f"Source: NIST. {short}, {full}, {date}; {url}", "aliases": [], "views": 0, "infoboxes": None})
        stats["docs"][short].append(title)
    for k, e in enumerate(ents):
        kind, depth, t, pg, li, _ = e
        nxt = ents[k + 1] if k + 1 < len(ents) else None
        # gather lines from (pg, li+1) to next boundary
        seg = []
        endp, endl = (nxt[3], nxt[4]) if nxt else (len(pages) - 1, len(pages[-1]))
        for p in range(pg, endp + 1):
            a = li + 1 if p == pg else 0
            b = endl if p == endp else len(pages[p])
            seg.extend(pages[p][a:b])
        if kind == "cont":
            if cur: cur["lines"] += seg
            continue
        if kind in ("drop", "root"):
            if kind == "drop" and cur: flush(); cur = None
            elif kind == "root" and cur and seg and any(x.strip() for x in seg): cur["lines"] += seg
            continue
        if depth <= 2:
            flush()
            cur = {"title": t, "lines": seg[:]}
        else:
            if cur is None: cur = {"title": t, "lines": []}
            cur["lines"] += ["", f"## {t}", ""] + seg
    flush()
    stats["docs"][short] = {"n": len(stats["docs"][short]), "outline_entries": len(ents), "headings_found": n_found}

# ---- glossary (crypto subset, NIST-sourced definitions only)
CRYPTO_SRC = re.compile(r"^(FIPS \d|NIST SP 800-(38|56|57|67|71|90|106|107|108|131|132|133|135|152|175|185|186|208|227|232)\b|NIST IR 8547|NISTIR 8547|NIST IR 8105|NISTIR 8105|NIST IR 8413|NISTIR 8413)")
with zipfile.ZipFile(os.path.join(RAW, "glossary-export.zip")) as z:
    g = json.loads(z.read(z.namelist()[0]).decode("utf-8-sig"))["parentTerms"]
gl_long, gl_short = [], []
for t in g:
    defs = []
    for d in t.get("definitions") or []:
        srcs = [s["text"] for s in d.get("sources") or []]
        nist = [s for s in srcs if re.match(r"^(FIPS|NIST|NISTIR)", s)]
        if not nist or not d.get("text"): continue
        if not any(CRYPTO_SRC.match(s) for s in nist): continue
        defs.append((d["text"].strip(), "; ".join(nist)))
    if not defs: continue
    t = dict(t, term=re.sub(r"<[^>]+>", "", t["term"]).strip())
    defs = [(re.sub(r"<[^>]+>", "", a).strip(), b) for a, b in defs]
    ab = [re.sub(r"<[^>]+>", "", a["text"]).strip() for a in t.get("abbrSyn") or [] if a.get("text")]
    seen, ds = set(), []
    for tx, sr in defs:
        if norm(tx) in seen: ds.append(None); continue
        seen.add(norm(tx)); ds.append(f"Definition ({sr}): {tx}")
    body = (f"Also: {', '.join(ab)}.\n" if ab else "") + "\n".join(x for x in ds if x)
    item = {"term": t["term"], "link": t["link"], "abbr": ab, "body": body}
    (gl_long if len(body) >= 260 else gl_short).append(item)
GL_URL = "https://csrc.nist.gov/glossary"
for i, it in enumerate(gl_long):
    rows.append({"page_id": BASE + 9_000_000 + i, "title": f"{it['term']} (NIST glossary)",
                 "text": f"NIST CSRC Glossary entry: {it['term']}.\n\n{it['body']}", "source": "usgov", "url": it["link"],
                 "license": LIC, "attribution": f"Source: NIST Computer Security Resource Center Glossary; {it['link']}",
                 "aliases": [a for a in it["abbr"] if len(a) >= 3], "views": 0, "infoboxes": None})
grp, buf, size = [], [], 0
for it in sorted(gl_short, key=lambda x: x["term"].lower()):
    buf.append(it); size += len(it["body"]) + len(it["term"]) + 8
    if size >= 1800: grp.append(buf); buf, size = [], 0
if buf: grp.append(buf)
for j, b in enumerate(grp):
    title = f"NIST glossary (cryptography): {b[0]['term']} – {b[-1]['term']}"
    text = "Short definitions from the NIST CSRC Glossary (cryptography terms).\n\n" + "\n\n".join(f"## {it['term']}\n\n{it['body']}" for it in b)
    rows.append({"page_id": BASE + 9_500_000 + j, "title": title, "text": text, "source": "usgov", "url": GL_URL, "license": LIC,
                 "attribution": f"Source: NIST Computer Security Resource Center Glossary; {GL_URL}", "aliases": [], "views": 0, "infoboxes": None})
stats["glossary"] = {"terms_total": len(g), "crypto_terms_kept": len(gl_long) + len(gl_short), "own_doc": len(gl_long), "grouped": len(gl_short), "group_docs": len(grp)}
stats["rows"] = len(rows); stats["rows_ge200"] = sum(len(r["text"]) >= 200 for r in rows)
with open(os.path.join(OUT, "boar-nist-crypto.jsonl"), "w") as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
json.dump([{"source": r["source"], "title": r["title"], "url": r["url"], "license": r["license"]} for r in rows], open(os.path.join(OUT, "manifest.json"), "w"), indent=0)
stats["inputs"] = {fn: hashlib.sha256(open(os.path.join(RAW, fn), "rb").read()).hexdigest() for fn in sorted(os.listdir(RAW)) if fn.endswith((".pdf", ".zip"))}
json.dump(stats, open(os.path.join(OUT, "convert-info.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in stats.items() if k != "inputs"}, indent=1)[:3000])
