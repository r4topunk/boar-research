#!/usr/bin/env python3
"""Publish a BOAR wave-1 knowledge pack to the HF dataset r4topunk/boar-packs.

Run with the venv:  .venv-hf/bin/python publish_pack.py <id> [--family qa|topics] [--go]
Without --go it only prints the plan (no write call is made to the Hub).
See README-publish.md next to this file.
"""
import argparse, difflib, hashlib, io, json, re, sys
from pathlib import Path

REPO = "r4topunk/boar-packs"
ROOT = Path("<workspace>")
PACK_DIRS = [ROOT / "shared-data/packs/wave3", ROOT / "shared-data/packs/wave2", ROOT / "shared-data/packs/wave1"]  # a pack id is looked up in order
def pack_dir(pid):
    for d in PACK_DIRS:
        if (d / f"{pid}.sqlite").exists(): return d
    raise SystemExit(f"pack {pid} not found under {[str(d) for d in PACK_DIRS]}")
PACKS = ROOT / "shared-data/packs/wave1"  # legacy default; call sites use pack_dir(pid)
CARDS = ROOT / "rnd/research/packs"
SELF = CARDS / "selftest"
SECTION = "Wave 1 (2026-10-12)"  # overridden by --section
SUBDIR = ""     # --subdir: publish a new revision under <family>/<id>/<subdir>/ so earlier files (pinned by kits) are never overwritten
RELNOTE = ""    # --release-note: one line added under the README intro for a revision
INTRO_WAVE1 = 'Seven packs built from the 2024-04-02 Stack Exchange data dump, the 2026-10-10 MedlinePlus Health Topics XML and the preparedness document set. Each folder holds the pack, its manifest, a `README.md` card, a `LICENSE.md` and a 20-item public `selftest.jsonl`. "User-selected only" means the pack passed the licence checks but displaced gold evidence from the default kit in the crowding probe, so the app should offer it as an opt-in, not install it by default. Stack Exchange packs stay CC BY-SA, with the per-post attribution inside each pack\'s `article_meta`.'

# id -> (wave number, release date) for the README line and the commit message; ids not listed are wave 1
WAVE = {"boar-factbook": (2, "2026-10-13"), "boar-simplewiki-en": (2, "2026-10-13"),
        "qa-cooking-se": (3, "2026-10-13"), "qa-money-se": (3, "2026-10-13")}
wave_of = lambda pid: WAVE.get(pid, (1, "2026-10-12"))

# id -> (domain, eligible, one-line reason from the crowding probe, family)
META = {
 "qa-travel-se":   ("Travel (Stack Exchange Q&A)", False, "its passages displaced gold from the claim kit on 8 benchmark items and 81 % of its slots landed on non-travel questions", "qa"),
 "qa-ethereum-se": ("Ethereum (Stack Exchange Q&A)", False, "it displaced gold from the claim kit on 4 crypto items", "qa"),
 "qa-bitcoin-se":  ("Bitcoin (Stack Exchange Q&A)", False, "it displaced gold from the claim kit on the same 4 crypto items", "qa"),
 "qa-health-se":   ("Medical sciences (Stack Exchange Q&A)", True, "kept-slot share 0.108 / 0.061 on the two benchmark sets, gold unchanged, +18 ms retrieval p50", "qa"),
 "qa-outdoors-se": ("Outdoors (Stack Exchange Q&A)", True, "kept-slot share 0.116 / 0.046, gold unchanged (note: no slots on its matching benchmark items, so it passes without proving in-topic benefit)", "qa"),
 "boar-firstaid-en":     ("First aid and emergency preparedness", True, "kept-slot share 0.101 / 0.060, gold unchanged, +133 ms retrieval p50", "topics"),
 "boar-medlineplus-en":  ("MedlinePlus health topics", True, "kept-slot share 0.043 / 0.026, gold unchanged, +9 ms retrieval p50", "topics"),
 "boar-factbook":        ("CIA World Factbook (CC0 archive)", False, "kept-slot share 0.11 / 0.20 but it displaces the claim kit's own gold passages on 4 benchmark items (its country pages share titles with the travel guides), so it stays user-selected until a quality check", "topics"),
 "qa-cooking-se":  ("Cooking (Seasoned Advice, Stack Exchange Q&A)", True, "kept-slot share 0.022 / 0.018 on the two benchmark sets, gold unchanged, +12 / +26 ms retrieval p50 (it takes almost no slots, so it passes by absence)", "qa"),
 "qa-money-se":    ("Personal finance (Stack Exchange Q&A)", False, "it displaced gold from the claim kit on 2 + 1 benchmark items (7 of its 12 kept slots on the larger set were on non-finance questions)", "qa"),
 "boar-simplewiki-en":   ("Simple English Wikipedia (2026-10-01)", False, "as a peer it takes 0.83 / 0.71 of the kept context slots and displaces gold on 9 / 13 benchmark items (general-knowledge crowding), so it is for users who want broad coverage, not a default", "topics"),
}

LICENSE_SE = """# Licence: {id}

Content: questions and answers from {site}, taken from the public Stack Exchange data dump of 2024-04-02.

- Each post is licensed under **CC BY-SA** (Creative Commons Attribution-ShareAlike). The licence of every document is the one the Stack Exchange dump records for its posts (latest revision): {split}. The licence text is in each document's `article_meta` row.
- **Attribution travels with every document.** The `article_meta.attribution` column of the pack holds, per document, the question author and every answer author as shown on Stack Exchange (display name and profile URL) and the URL of the question. The app shows this next to each answer. Author names are deliberately not repeated in this repository's files.
- **Share-alike:** anything you build from this pack must stay under CC BY-SA, keep the attribution, and indicate changes. Documents whose answers carry a different CC BY-SA version than the question say so in the attribution.
- Licence texts: https://creativecommons.org/licenses/by-sa/4.0/ and https://creativecommons.org/licenses/by-sa/3.0/
- Stack Exchange network content policy: https://stackoverflow.com/legal/terms-of-service/public#licensing
- The pack file itself (index, embeddings, compression) adds no further restriction.
"""

LICENSE_MEDLINE = """# Licence: boar-medlineplus-en

Content: the English MedlinePlus health-topic summaries from the US National Library of Medicine (NLM), snapshot of the MedlinePlus Health Topics XML of 2026-10-10.

- **Public domain (NLM).** MedlinePlus health-topic text is a US government work. NLM asks for this credit line, which the pack stores on every document in `article_meta`: *"Courtesy of MedlinePlus from the National Library of Medicine"* followed by the topic URL. Keep it when you reuse the text.
- Not included, by licence: A.D.A.M. encyclopedia pages, ASHP drug information, and linked external sites.
- NLM terms: https://medlineplus.gov/about/using/usingcontent/
- Not medical advice. The pack is AI-indexed, not clinically reviewed.
"""

LICENSE_FACTBOOK = """# Licence: boar-factbook

Content: the CIA World Factbook, a work of the United States federal government (public domain in the US, 17 U.S.C. §105), taken from a CC0 1.0 archive on GitHub (the live site was discontinued on 2026-02-04). The pack text, the "Key facts" blocks and the aliases are derived from that archive; data as of the archive's last commit (see the pack manifest and README).
- Pack contents: CC0 1.0 (no rights reserved). No attribution is legally required; a courtesy note "Source: CIA World Factbook (archive)" is appreciated.
- The pack format, build scripts and self-test questions: CC BY 4.0 (BOAR).
"""

LICENSE_SIMPLEWIKI = """# Licence: boar-simplewiki-en

Content: Simple English Wikipedia (simple.wikipedia.org), from the Wikimedia dump dated 2026-10-01. Text is available under the Creative Commons Attribution-ShareAlike 4.0 International licence (CC BY-SA 4.0) and the GNU Free Documentation License; each article's URL is stored in the pack and shown in BOAR's citations, which satisfies attribution to the article (authors are listed in the article's history on simple.wikipedia.org).
- Pack contents: CC BY-SA 4.0 (share-alike: derived packs must carry the same licence).
- The pack format, build scripts and self-test questions: CC BY 4.0 (BOAR).
"""

LICENSE_FIRSTAID = """# Licence: boar-firstaid-en

A mix of sources; the licence of each document is recorded in the pack's `article_meta` table (source URL and licence per document).

- **CC BY-SA 4.0** (1,548 documents): English Wikipedia, Wikivoyage, Wikibooks and Appropedia text. Share-alike: keep the licence and the attribution (each document links to its source page, where the author list is). {extra}
- **Public domain** (294 documents): US Army FM 21-76 *Survival* (1992), US federal government works (17 U.S.C. section 105), and 88 sections of Army Techniques Publication ATP 4-02.11 (March 2026, public release). The ATP rows carry a source credit line in `article_meta.attribution`.
- Licence texts: https://creativecommons.org/licenses/by-sa/4.0/
- Not medical advice. The pack is AI-indexed, not clinically reviewed; the ATP material is written for military medics.
"""

SE_SITE = {"qa-travel-se": "travel.stackexchange.com", "qa-ethereum-se": "ethereum.stackexchange.com",
           "qa-bitcoin-se": "bitcoin.stackexchange.com", "qa-health-se": "medicalsciences.stackexchange.com",
           "qa-outdoors-se": "outdoors.stackexchange.com", "qa-cooking-se": "cooking.stackexchange.com",
           "qa-money-se": "money.stackexchange.com"}

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()

def human(n):
    return f"{n:,} B ({n/1048576:.1f} MiB)"

# ---------- card -> public README ----------
LEAK = re.compile(r"<users-dir>/|\brnd/|~/|\barms/|shared-data|\bmini\b|MacBook|\bT-K\d|\bD-K\d|coordinator|kiln|\bwt/|@[\w.-]+\.\w+|mdm-")

def public_readme(pid, card, man, domain, eligible, reason, family):
    lines = card.splitlines()
    out, skip_files = [], False
    for ln in lines[1:]:
        if ln.startswith("TL;DR:"):
            continue
        if re.match(r"^- (Files|Scripts): ", ln):          # internal locations
            continue
        if ln.lstrip().startswith("Scripts:") or ln.startswith("  Scripts:"):
            continue
        if re.match(r"^- pending", ln):
            ln = "- Not yet measured."
        if ln.strip() == "- pending self-test.":
            ln = "- Self-test not yet scored."
        if ln.startswith("- Fresher alternative"):
            continue
        out.append(ln)
    body = "\n".join(out)
    # internal references -> public wording
    body = re.sub(r"\s*Details: (coordinator/)?arms/packs/[\w.\-]+\.", "", body)
    body = re.sub(r"T-K4a \((\d{4}-\d\d-\d\d), arms/packs/T-K4a\.md\)", r"Crowding probe (\1)", body)
    body = re.sub(r"\(arms/packs/T-K4a\.md\)", "", body)
    body = re.sub(r"\s*\(T-K\d[a-z]?\)", "", body)
    body = body.replace("(D-K2, per row in", "(per row in").replace("(convert.mjs pdf, T-K1;", "(convert.mjs pdf;")
    body = body.replace(", see boar-preparedness.md)", ", the earlier boar-preparedness pack)")
    body = re.sub(r"cd <runner>/kiln/packs && ", "", body)
    body = re.sub(r"\s*#?\s*,?\s*T-K\d[a-z]?\b", "", body)
    body = body.replace("   # MacBook", "").replace(" (D-K5)", "")
    body = re.sub(r"^## ", "\n## ", body, flags=re.M)
    body = re.sub(r"T-K2 engine patch", "BOAR app update that adds the Stack Exchange label and attribution", body)
    body = body.replace("the T-K2 builder (scripts sha = wt/packs)", "the BOAR pack builder")
    body = body.replace("mini M4, ", "").replace("mini M4", "build host")
    body = re.sub(r"\(\s*mini[^)]*\)", "", body)
    body = re.sub(r"<runner>/kiln/packs/", "", body)
    body = re.sub(r"rnd/kiln/packs/convert/convert\.mjs", "convert.mjs", body)
    body = re.sub(r"rnd/kiln/packs/wave\d-scripts/", "scripts/", body)
    body = re.sub(r"\(mini M4;", "(build host Apple M4;", body)
    body = body.replace("the patched engine tree", "the patched engine tree (source labels + attribution)")
    body = re.sub(r"shared-data/preparedness-v2/", "preparedness-v2/", body)
    body = re.sub(r"shared-data/packs/work/", "work/", body)
    body = body.replace("# MacBook, ", "# ").replace("rnd/", "")
    # drop the "Kit entry" bullet detail that refers to private state, keep id+sha elsewhere
    body = re.sub(r"^- Not in any kit\..*$", "", body, flags=re.M)
    body = re.sub(r"^## Kit entry and build", "## Build (reference)", body, flags=re.M)
    body = re.sub(r"\n{3,}", "\n\n", body)
    sha, size = man["sha256"], man["sizeBytes"]
    flag = ("**Default-eligible**: " if eligible else "**User-selected only, not default**: ") + reason + "."
    head = f"""---
pretty_name: {pid}
license: other
license_name: per-document (see LICENSE.md)
language:
  - en
tags:
  - offline
  - rag
  - sqlite
---

# {pid}

{domain}. A BOAR knowledge pack: one SQLite file the BOAR app downloads and searches on the device, with no network. Part of the wave-{wave_of(pid)[0]} release ({wave_of(pid)[1]}) of [r4topunk/boar-packs](https://huggingface.co/datasets/{REPO}).{(chr(10) + chr(10) + RELNOTE) if RELNOTE else ""}

| | |
|---|---|
| Eligibility | {flag} |
| Size | {human(size)} |
| SHA-256 | `{sha}` |
| Articles / chunks | {man.get('articles'):,} / {man.get('chunks'):,} |
| Files | `{pid}.sqlite`, `{pid}.sqlite.json` (manifest), `LICENSE.md`, `selftest.jsonl` |
| Licence | see `LICENSE.md`; per-document licence and attribution are in the pack's `article_meta` table |

## Install

- App catalogue entry: `{{"id": "{pid}", "sha256": "{sha}"}}`. The app pins each file to the commit it was uploaded in (`https://huggingface.co/datasets/{REPO}/resolve/<commit-sha>/{family}/{pid}/{(SUBDIR + "/") if SUBDIR else ""}{pid}.sqlite`) and checks the SHA-256 and size above before use.
- Or import the `.sqlite` file by hand in the app's knowledge-pack screen. Verify with `shasum -a 256 {pid}.sqlite`.

## Self-test

`selftest.jsonl` holds 20 public questions with reference answers, written by an AI model from the pack's own text. They are development material (never benchmark claim items); the Quality section below reports the score when one has been measured.

"""
    return head + body.strip() + "\n"

def license_md(pid, card, man):
    if pid in SE_SITE:
        m = re.search(r"Rows: (?:(CC BY-SA 2\.5 [\d,]+); )?(CC BY-SA 3\.0 [\d,]+); (CC BY-SA 4\.0 [\d,]+)", card)
        split = (", ".join(f"{g} documents" for g in m.groups() if g) if m else "CC BY-SA 3.0 or 4.0 per document")
        txt = LICENSE_SE.format(id=pid, site=SE_SITE[pid], split=split)
        if m and m.group(1):  # sites older than 2011-04-08 carry CC BY-SA 2.5 posts (wave 3: cooking, money)
            txt = txt.replace(" and https://creativecommons.org/licenses/by-sa/3.0/",
                              ", https://creativecommons.org/licenses/by-sa/3.0/ and https://creativecommons.org/licenses/by-sa/2.5/")
        return txt
    if pid == "boar-medlineplus-en":
        return LICENSE_MEDLINE
    if pid == "boar-firstaid-en":
        return LICENSE_FIRSTAID.format(extra="")
    if pid == "boar-factbook":
        return LICENSE_FACTBOOK
    if pid == "boar-simplewiki-en":
        return LICENSE_SIMPLEWIKI
    raise SystemExit(f"no licence template for {pid}")

def sanitized_manifest(path):
    d = json.loads(Path(path).read_text())
    if "file" in d:
        d["file"] = Path(d["file"]).name        # internal absolute path -> basename
    return (json.dumps(d, indent=2) + "\n").encode()

# ---------- root README ----------
def root_section(ids=None, intro=None):
    rows = []
    for pid, (dom, el, _, fam) in META.items():
        if ids and pid not in ids: continue
        man = json.loads((pack_dir(pid) / f"{pid}.sqlite.json").read_text())
        lic = (("CC BY-SA 2.5/3.0/4.0 per post" if pid in ("qa-cooking-se", "qa-money-se") else "CC BY-SA 3.0/4.0 per post") if pid in SE_SITE else
               "Public domain (NLM)" if pid == "boar-medlineplus-en" else
               "CC0 (public domain)" if pid == "boar-factbook" else
               "CC BY-SA 4.0 + GFDL" if pid == "boar-simplewiki-en" else "CC BY-SA 4.0 + public domain")
        rows.append(f"| `{fam}/{pid}/` | {dom} | {man['sizeBytes']/1048576:.1f} MiB | {lic} | "
                    f"{'default-eligible' if el else 'user-selected only'} | `{man['sha256'][:8]}` |")
    return f"""
## {SECTION}

{intro or INTRO_WAVE1}

| Path | Domain | Size | Licence | Eligibility | SHA-256 (first 8) |
|---|---|---|---|---|---|
""" + "\n".join(rows) + "\n"

def fetch_root_readme(api):
    p = api.hf_hub_download(REPO, "README.md", repo_type="dataset")
    return Path(p).read_text()

def new_root(old, ids=None, intro=None):
    if f"## {SECTION}" in old:
        return None
    return old.rstrip("\n") + "\n" + root_section(ids, intro)

# ---------- main ----------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("id", nargs="?")
    ap.add_argument("--family", choices=["qa", "topics"])
    ap.add_argument("--go", action="store_true", help="really upload (default: print the plan only)")
    ap.add_argument("--list", action="store_true", help="show what the dataset holds under qa/ and topics/")
    ap.add_argument("--root-readme", action="store_true", help="plan/apply only the root README section (no pack id needed)")
    ap.add_argument("--section", default=None, help="root README section title to append (default: the Wave 1 section); the pack table lists the ids given with --ids")
    ap.add_argument("--ids", default=None, help="comma-separated pack ids for the --root-readme table (default: all META ids)")
    ap.add_argument("--subdir", default="", help="publish under <family>/<id>/<subdir>/ (new revision; never overwrites earlier files)")
    ap.add_argument("--pack-dir", default=None, help="directory holding <id>.sqlite + .json (default: wave3/wave2/wave1 lookup)")
    ap.add_argument("--release-note", default="", help="one line for the README intro of a revision")
    ap.add_argument("--intro", default=None, help="one-line intro for the --root-readme section (default: the Wave 1 text)")
    a = ap.parse_args()
    from huggingface_hub import HfApi, CommitOperationAdd
    api = HfApi()

    if a.list:
        for d in ("qa", "topics"):
            print(f"{d}/")
            try:
                for e in api.list_repo_tree(REPO, path_in_repo=d, repo_type="dataset", recursive=True):
                    if hasattr(e, "size"):
                        print(f"  {e.path}  {e.size:,} B")
            except Exception as x:
                print(f"  (empty / not found: {type(x).__name__})")
        return

    global SECTION
    if a.section: SECTION = a.section
    ids = set(a.ids.split(",")) if a.ids else None
    intro = a.intro if getattr(a, 'intro', None) else None
    if a.root_readme and not a.id:
        old = fetch_root_readme(api); new = new_root(old, ids, intro)
        if new is None:
            print("root README already has the section; nothing to do"); return
        print("".join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), "README.md (hub)", "README.md (new)")))
        if a.go:
            ci = api.upload_file(path_or_fileobj=new.encode(), path_in_repo="README.md", repo_id=REPO, repo_type="dataset",
                                 commit_message=f"{SECTION.split(' (')[0].lower()}: root README section")
            print("commit:", ci.commit_url if hasattr(ci, "commit_url") else ci)
        else:
            print("\n[dry run] nothing uploaded")
        return

    if not a.id or a.id not in META:
        ap.error(f"id required, one of: {', '.join(META)}")
    pid = a.id
    domain, eligible, reason, family = META[pid]
    if a.family and a.family != family:
        print(f"note: --family {a.family} overrides the default {family}/ for {pid}")
        family = a.family
    global SUBDIR, RELNOTE
    SUBDIR, RELNOTE = a.subdir.strip("/"), a.release_note
    dest = f"{family}/{pid}" + (f"/{SUBDIR}" if SUBDIR else "")

    pdir = Path(a.pack_dir) if a.pack_dir else pack_dir(pid)
    sq, mj = pdir / f"{pid}.sqlite", pdir / f"{pid}.sqlite.json"
    st = SELF / f"{pid}.jsonl"; card_p = CARDS / f"{pid}.md"
    for p in (sq, mj, st, card_p):
        if not p.exists(): raise SystemExit(f"missing {p}")
    man = json.loads(mj.read_text())
    problems = []
    real_size, real_sha = sq.stat().st_size, sha256(sq)
    if real_size != man["sizeBytes"]: problems.append(f"size {real_size} != manifest {man['sizeBytes']}")
    if real_sha != man["sha256"]: problems.append(f"sha256 {real_sha} != manifest {man['sha256']}")
    nst = sum(1 for l in st.read_text().splitlines() if l.strip())
    if nst != 20: problems.append(f"selftest has {nst} items, expected 20")
    card = card_p.read_text()
    if man["sha256"] not in card: problems.append("card does not contain the manifest sha256")
    if str(man["sizeBytes"]) not in card.replace(",", "") : problems.append("card does not contain the manifest size")
    readme = public_readme(pid, card, man, domain, eligible, reason, family)
    lic = license_md(pid, card, man)
    mbytes = sanitized_manifest(mj)
    stbytes = st.read_bytes()
    for name, txt in (("README.md", readme), ("LICENSE.md", lic), ("manifest", mbytes.decode()), ("selftest", stbytes.decode())):
        hit = LEAK.search(txt)
        if hit: problems.append(f"possible internal/personal string in {name}: {hit.group(0)!r}")

    files = [(f"{dest}/{pid}.sqlite", sq, None), (f"{dest}/{pid}.sqlite.json", None, mbytes),
             (f"{dest}/README.md", None, readme.encode()), (f"{dest}/LICENSE.md", None, lic.encode()),
             (f"{dest}/selftest.jsonl", None, stbytes)]
    print(f"== plan: {pid}  ->  {REPO} : {dest}/  ({'default-eligible' if eligible else 'user-selected only'})")
    total = 0
    for path, src, data in files:
        n = src.stat().st_size if src else len(data); total += n
        print(f"  {path:55s} {n:>14,} B")
    print(f"  {'TOTAL':55s} {total:>14,} B")
    print(f"  verify: sqlite size {real_size:,} == manifest {man['sizeBytes']:,}: {real_size == man['sizeBytes']}; "
          f"sha256 match: {real_sha == man['sha256']}; sha8 {real_sha[:8]}; selftest items {nst}")
    print("  note: the uploaded manifest has its 'file' field reduced to the basename (original is an internal absolute path)")
    old = fetch_root_readme(api); new = new_root(old)
    print("\n-- root README diff (applied separately with: publish_pack.py --root-readme --go) --")
    if new is None: print("(section already present, no change)")
    else: print("".join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), "README.md (hub)", "README.md (new)", n=0)))
    if problems:
        print("\nPROBLEMS:"); [print("  -", p) for p in problems]
        if a.go: raise SystemExit("refusing to upload with problems")
    if not a.go:
        print("\n[dry run] nothing uploaded; add --go to upload"); return
    ops = [CommitOperationAdd(path_in_repo=p, path_or_fileobj=(str(s) if s else io.BytesIO(d))) for p, s, d in files]
    existing = {e.path for e in api.list_repo_tree(REPO, path_in_repo=dest.rsplit("/", 1)[0], repo_type="dataset", recursive=True)}
    clash = [p for p, _, _ in files if p in existing]
    if SUBDIR and clash: raise SystemExit(f"refusing to overwrite existing hub files: {clash}")
    ci = api.create_commit(REPO, ops, repo_type="dataset", commit_message=f"wave {wave_of(pid)[0]}: {pid}" + (f" {SUBDIR}" if SUBDIR else ""))
    print("commit:", ci.commit_url)
    for p, _, _ in files: print("  uploaded", p)

if __name__ == "__main__":
    main()
