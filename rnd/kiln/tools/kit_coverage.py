#!/usr/bin/env python3
"""kit_coverage: is an entity / title in BOAR's kit A? Titles and counts only, never passage text.

Kit A (Plumb D10 / exp-08): the essential corpus bundled in boar-app 611a4b92 (assets/corpus/*.json, read with
`git show`, so the checkout is never touched) + wiki-vital5 + boar-crypto + boar-wikivoyage-en (local copies under
<workspace>/shared-data, the same sha256 as the mini's pins: d3b87d56…, ae9fbd2c…, ff8595e3…).

Per term and per pack it reports:
  exact      article titles equal to the term (case/diacritics-insensitive)
  redirects  redirect titles equal to the term -> the article they point to (format-2 packs only)
  titles     up to --max titles that contain the term as whole words (e.g. "South Holland" for "Holland")
  mentions   number of passages whose text mentions the term as a phrase (FTS count; no text returned)
Verdict per term: COVERED (an exact title or redirect somewhere), TITLE-ONLY (only titles that contain the term,
i.e. probably a look-alike or a sub-topic: check them), MENTION-ONLY, ABSENT.
In the app, Wikivoyage titles show as "Wikivoyage: <title>", crypto as "Ethereum EIPs/ERCs: …", "Bitcoin BIPs: …" etc.

Usage:
  python3 kit_coverage.py "Lake Malawi" "Puerto Rico Trench" "Netherlands"
  python3 kit_coverage.py --file terms.txt          # one term per line
  python3 kit_coverage.py --json "Holland"           # machine-readable
Exit code 0 always; the verdict is in the output.
"""
import argparse, json, os, re, sqlite3, subprocess, unicodedata

B = "<workspace>"
APP, COMMIT = f"{B}/boar-app", "611a4b92"
PACKS = {
    "wiki-vital5": f"{B}/shared-data/packs/wiki-vital5.sqlite",
    "boar-crypto": f"{B}/shared-data/crypto/boar-crypto.sqlite",
    "boar-wikivoyage-en": f"{B}/shared-data/packs/boar-wikivoyage-en.sqlite",
}
ESSENTIAL = ["corpus.json", "corpus-standard.json", "corpus-full.json"]


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def has_words(term_n, title_n):
    return re.search(rf"(?:^| ){re.escape(term_n)}(?: |$)", title_n) is not None


def fts_phrase(term):
    words = [w for w in re.split(r"[^\w]+", term, flags=re.UNICODE) if w]
    return '"' + " ".join(words).replace('"', "") + '"' if words else None


def load_essential():
    out = []
    for f in ESSENTIAL:
        try:
            raw = subprocess.run(["git", "-C", APP, "show", f"{COMMIT}:assets/corpus/{f}"], capture_output=True, check=True).stdout
            out += [(f, d.get("title", ""), norm(d.get("body", ""))) for d in json.loads(raw)]
        except Exception:
            pass
    return out


def check(term, ess, conns, mx):
    tn = norm(term)
    res = {"term": term, "packs": {}}
    # essential corpus (JSON): titles + phrase mentions in bodies (count only)
    titles = {}
    for f, t, body in ess:
        titles.setdefault(t, f)
    e = {"exact": sorted({t for t in titles if norm(t) == tn}),
         "titles": sorted({t for t in titles if norm(t) != tn and has_words(tn, norm(t))})[:mx],
         "mentions": sum(1 for _, _, body in ess if tn and has_words(tn, body))}
    res["packs"]["essential(app " + COMMIT + ")"] = e
    phrase = fts_phrase(term)
    for name, c in conns.items():
        fmt2 = c.execute("select count(*) from sqlite_master where name='articles'").fetchone()[0] == 1
        tab = "articles" if fmt2 else "chunks"
        ts = [r[0] for r in c.execute(f"select distinct title from {tab}")] if name not in TITLE_CACHE else TITLE_CACHE[name]
        TITLE_CACHE[name] = ts
        p = {"exact": sorted({t for t in ts if norm(t) == tn}),
             "titles": sorted({t for t in ts if norm(t) != tn and has_words(tn, norm(t))})[:mx]}
        if fmt2:
            p["redirects"] = [f"{r} -> {a}" for r, a in c.execute(
                "select r.title, a.title from redirects r join articles a on a.id = r.article_id where r.title = ? collate nocase limit 10", (term,))]
        try:
            p["mentions"] = c.execute(f"select count(*) from {'fts' if fmt2 else 'chunks_fts'} where {'fts' if fmt2 else 'chunks_fts'} match ?",
                                      (phrase,)).fetchone()[0] if phrase else 0
        except sqlite3.OperationalError:
            p["mentions"] = None
        res["packs"][name] = p
    ex = any(v["exact"] or v.get("redirects") for v in res["packs"].values())
    ti = any(v["titles"] for v in res["packs"].values())
    me = any(v.get("mentions") for v in res["packs"].values())
    res["verdict"] = "COVERED" if ex else "TITLE-ONLY" if ti else "MENTION-ONLY" if me else "ABSENT"
    return res


TITLE_CACHE = {}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("terms", nargs="*")
    ap.add_argument("--file")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--max", type=int, default=12)
    a = ap.parse_args()
    terms = a.terms + ([l.strip() for l in open(a.file) if l.strip()] if a.file else [])
    ess = load_essential()
    conns = {n: sqlite3.connect(f"file:{p}?mode=ro", uri=True) for n, p in PACKS.items() if os.path.exists(p)}
    for t in terms:
        r = check(t, ess, conns, a.max)
        if a.json:
            print(json.dumps(r, ensure_ascii=False))
            continue
        print(f"== {t}: {r['verdict']}")
        for n, p in r["packs"].items():
            bits = []
            if p["exact"]: bits.append(f"exact {p['exact']}")
            if p.get("redirects"): bits.append(f"redirects {p['redirects']}")
            if p["titles"]: bits.append(f"titles {p['titles']}")
            if p.get("mentions"): bits.append(f"mentions {p['mentions']}")
            if bits: print(f"   {n}: " + "; ".join(bits))
