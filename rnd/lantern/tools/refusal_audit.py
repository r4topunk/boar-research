"""False-refusal audit for precheck v2 (`precheck.py --refusals`).

For every refused row, decide whether the sources had the answer:
  false-refusal     a retrieved source has the answer:
                      title  - a retrieved title is one of the item's answer articles, or
                      text   - the retrieved article (read from the local copy of the pack) satisfies the item's
                               must_any/must_k (article-level proxy: rows do not record passage text)
  correct-refusal   the retrieved sources do not have the answer; split by whether the answer article exists
                    in an installed pack:
                      retrieval-miss  - it exists but was not retrieved
                      not-in-pack     - it does not exist in any installed pack
  unknown-dropped   no retrieved titles were recorded (the gate dropped every source before the `sources`
                    event, reason code grounding:off-topic-dropped-N); pack presence still reported.
Mechanism (from reasonCodes): gate-after-draft (all-citations-removed / uncited-with-sources: the model wrote a
draft and the citation gate declined it) vs no-source (no-good-source / declined-compact only)."""
import json, re, sqlite3, urllib.parse
from pathlib import Path
from compression import zstd

SHARED = Path("<workspace>/shared-data")
ALL_PACKS = {
    "boar-crypto": SHARED / "crypto" / "boar-crypto.sqlite",
    "boar-wikivoyage-en": SHARED / "packs" / "boar-wikivoyage-en.sqlite",
    "wiki-vital5": SHARED / "packs" / "wiki-vital5.sqlite",   # format v1 (chunks table, titles without prefix)
}
V1_PACKS = {"wiki-vital5"}
# default = what the vitalik-lantern runs 1-2 installed (--install-assets boar-crypto,boar-wikivoyage-en)
PACKS = {k: ALL_PACKS[k] for k in ("boar-crypto", "boar-wikivoyage-en")}
REFERENCE_ONLY = {"wiki-vital5": ALL_PACKS["wiki-vital5"]}  # not installed: presence is reported separately
# which installed packs could hold an answer article from each source
SOURCE_PACKS = {"wikivoyage": ["boar-wikivoyage-en"], "eip": ["boar-crypto"], "wikipedia": ["boar-crypto", "wiki-vital5"]}

def configure(installed):
    """Set the installed packs for this run (e.g. ["boar-crypto", "boar-wikivoyage-en", "wiki-vital5"])."""
    global PACKS, REFERENCE_ONLY
    unknown = set(installed) - set(ALL_PACKS)
    if unknown:
        raise SystemExit(f"unknown pack(s): {sorted(unknown)}; known: {sorted(ALL_PACKS)}")
    PACKS = {k: ALL_PACKS[k] for k in installed}
    REFERENCE_ONLY = {k: v for k, v in ALL_PACKS.items() if k not in PACKS}
EXTRA_ANSWER_TITLES = {
    "vit-fa-003": ["Japan"], "vit-fa-004": ["Nigeria", "Japan"], "vit-fa-015": ["World population"],
    "vit-fa-016": ["Canada"], "vit-fa-010": ["Measles"], "vit-cry-007": ["d/acc"],
    "vit-fa-014": ["List of countries by population"], "vit-fa-023": ["List of countries by population"],
}

class Packs:
    def __init__(self):
        self.db = {k: sqlite3.connect(f"file:{p}?mode=ro", uri=True) for k, p in ALL_PACKS.items() if p.exists()}
        self._blocks = {}
    def _v2_text(self, name, title):
        c = self.db[name]
        row = c.execute("select block_id, off, len from articles where title = ? collate nocase limit 1", (title,)).fetchone()
        if not row:
            r = c.execute("select a.block_id, a.off, a.len from redirects r join articles a on a.id = r.article_id where r.title = ? collate nocase limit 1", (title,)).fetchone()
            row = r
        if not row:
            return None
        key = (name, row[0])
        if key not in self._blocks:
            self._blocks[key] = zstd.decompress(c.execute("select zdata from blocks where id = ?", (row[0],)).fetchone()[0])
        return self._blocks[key][row[1]:row[1] + row[2]].decode("utf-8", "replace")
    def _v1_text(self, name, title):
        rows = self.db[name].execute("select body from chunks where title = ? collate nocase", (title,)).fetchall()
        return "\n".join(r[0] for r in rows) or None
    def text(self, title, only_installed=False):
        for name in self.db:
            if only_installed and name not in PACKS:
                continue
            t = self._v1_text(name, title) if name in V1_PACKS else self._v2_text(name, title)
            if t:
                return name, t
        return None
    def has(self, title, installed=True):
        names = [n for n in self.db if (n in PACKS) == installed]
        for n in names:
            if n in V1_PACKS:
                if self.db[n].execute("select 1 from chunks where title = ? collate nocase limit 1", (title,)).fetchone():
                    return n
            elif self._v2_text(n, title) is not None:
                return n
        return None

def strip_prefix(t):
    return t.split(": ", 1)[1] if re.match(r"^(Wikivoyage|Ethereum EIPs/ERCs|ethereum\.org|Ethereum specs|Bitcoin BIPs)[^:]*: ", t) else t

def source_of(retrieved):
    if retrieved.startswith("Wikivoyage: "): return "wikivoyage"
    if retrieved.startswith("Ethereum EIPs/ERCs: "): return "eip"
    if re.match(r"^(ethereum\.org|Ethereum specs|Bitcoin BIPs)[^:]*: ", retrieved): return "other"
    return "wikipedia"

# items whose reference articles only answer part of the question (Tornado Cash alone can't explain Privacy Pools)
ANSWER_TITLES_OVERRIDE = {"vit-cry-005": [("wikipedia", "Privacy Pools")]}

def answer_titles(q):
    """(source, title) pairs of the articles that answer the item."""
    if q["id"] in ANSWER_TITLES_OVERRIDE:
        return list(ANSWER_TITLES_OVERRIDE[q["id"]])
    out = []
    for u in q.get("reference_sources", []):
        if "/wiki/" in u and ("wikipedia.org" in u or "wikivoyage.org" in u):
            out.append(("wikivoyage" if "wikivoyage" in u else "wikipedia", urllib.parse.unquote(u.split("/wiki/")[1]).replace("_", " ")))
        m = re.search(r"eips\.ethereum\.org/EIPS/eip-(\d+)", u)
        if m:
            out.append(("eip", f"EIP-{m.group(1)}"))
    return out + [("wikipedia", t) for t in EXTRA_ANSWER_TITLES.get(q["id"], [])]

def title_match(retrieved, answers):
    src, r = source_of(retrieved), strip_prefix(retrieved).lower()
    for asrc, a in answers:
        a = a.lower()
        if asrc == src and (r == a or (asrc == "eip" and r.startswith(a + ":"))):
            return a
    return None

HEDGE_ITEMS = {"vit-fa-008"}  # must_any lists hedge words, not answer facts: text evidence is meaningless

def text_strength(q):
    g = q.get("grading", {})
    if q["id"] in HEDGE_ITEMS:
        return "na"
    groups = [grp for grp in g.get("must_any", []) if any(not x.startswith("re:^") for x in grp)]
    if g.get("must_k") or len(groups) >= 2:
        return "strong"
    if len(groups) == 1 and all(x.startswith("re:") for x in groups[0]):
        return "strong"
    return "weak" if groups else "na"

def text_has_answer(q, text, hits, is_echo, norm):
    """must_any/must_k on the article text; verdict regexes anchored at the answer start (re:^) are dropped."""
    g = q.get("grading", {}); question = norm(q.get("query") or q.get("question")); t = norm(text)
    groups = [[x for x in grp if not x.startswith("re:^") and not is_echo(x, question)] for grp in g.get("must_any", [])]
    mk = g.get("must_k")
    if not any(groups) and not mk:
        return None  # nothing checkable
    for grp in groups:
        if grp and not any(hits(x, t) for x in grp):
            return False
    if any(not grp for grp in groups) and not mk and all(not grp for grp in groups):
        return None
    if mk:
        live = [x for x in mk["terms"] if not is_echo(x, question)]
        if sum(1 for x in live if hits(x, t)) < mk["k"]:
            return False
    return True

def mechanism(row):
    codes = row.get("reasonCodes", [])
    if any("all-citations-removed" in c or "uncited-with-sources" in c for c in codes):
        return "gate-after-draft"
    return "no-source"

def audit(q, row, packs, hits, is_echo, norm):
    answers = answer_titles(q)
    retrieved = list(dict.fromkeys(row.get("retrievedTitles") or []))
    strength = text_strength(q)
    ev, weak = [], []
    for r in retrieved:
        if title_match(r, answers):
            ev.append(f"title:{r}")
            continue
        if strength == "na":
            continue
        got = packs.text(strip_prefix(r), only_installed=False)
        if got and text_has_answer(q, got[1], hits, is_echo, norm):
            (ev if strength == "strong" else weak).append(f"text:{r}")
    titles = [t for _, t in answers]
    in_pack, in_ref = [], []
    for src, t in answers:
        for pack in list(PACKS) + list(REFERENCE_ONLY):
            if pack not in packs.db:
                continue
            txt = packs._v1_text(pack, t) if pack in V1_PACKS else packs._v2_text(pack, t)
            if not txt:
                continue
            same_source = pack in SOURCE_PACKS.get(src, [])
            confirmed = strength == "strong" and text_has_answer(q, txt, hits, is_echo, norm)
            if same_source or confirmed:
                (in_pack if pack in PACKS else in_ref).append(f"{t} [{pack}{', text-confirmed' if confirmed else ''}]")
    if ev:
        kind, sub = "false-refusal", ", ".join(ev)
    elif weak:
        kind, sub = "possible-false-refusal", ", ".join(weak) + " (weak: single broad must_any group; check by hand)"
    elif not retrieved:
        kind, sub = "unknown-dropped", ""
    else:
        kind, sub = "correct-refusal", "retrieval-miss" if in_pack else "not-in-pack"
    return {"refusal_kind": kind, "evidence": sub, "mechanism": mechanism(row), "retrieved": retrieved,
            "text_check": strength, "answer_titles": titles, "answer_in_installed_pack": in_pack, "answer_in_reference_pack_only": in_ref}
