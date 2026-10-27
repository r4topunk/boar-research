#!/usr/bin/env python3
"""PACK-VISA converter (2026-10-19): API-rendered HTML of the visa articles -> pack builder JSONL + manifest.json + convert-info.json.
usage: convert.py <fetch/pages.jsonl> <outdir> [--aliases aliases.json]

Text layout (builder input, format 2):
  - headings h2/h3/h4 -> "## " / "### " / "#### " (the FTS section path); boilerplate sections dropped
    (See also, References, Notes, External links, Further reading, Sources, Bibliography, Gallery, ...).
  - paragraphs -> plain text; footnote markers ([12], [citation needed]) removed.
  - lists -> "- item" lines; a list of short items (country lists in visa-policy pages) -> one comma-separated line.
  - wikitable -> one TEXT line per row (never a "|" table row: the builder leaves "|"-row chunks out of the keyword index):
      "<first cell>: <col2 header>: <v2>; <col3 header>: <v3>; ..."  (empty and symbol-only cells dropped,
      rowspans expanded, single-cell group rows become a "<group> / " prefix for the following rows).
    Rows are packed into paragraphs of <= 900 chars, each opened by a context line
      "<Article title>, <section>:"
    so every chunk says whose requirements (nationality) and which table it is, e.g.
      "Visa requirements for Brazilian citizens, Visa requirements:\nJapan: Visa requirement: Visa not required; Allowed stay: 90 days".
  - dropped: figures, maps, legends, navboxes, infoboxes, styles, hatnotes, reference lists, non-wikitable tables.
Rows: source enwiki, page_id = enwiki page id, url = https://en.wikipedia.org/wiki/<title>?oldid=<revid>, license CC BY-SA 4.0,
attribution = '"<title>", Wikipedia contributors, revision <revid> of <timestamp> (<url>), CC BY-SA 4.0'."""
import json, os, re, sys, hashlib, unicodedata
from bs4 import BeautifulSoup, NavigableString, Tag

BOILER = re.compile(r"^(see also|references?( and notes)?|notes( and references)?|footnotes|external links|further reading|sources|bibliography|gallery|citations|notes and citations)$", re.I)
SKIP_CLASSES = {"navbox", "navbox-inner", "references", "reflist", "mw-references-wrap", "shortdescription", "hatnote", "thumb",
                "legend", "noprint", "infobox", "sidebar", "metadata", "ambox", "mw-empty-elt", "gallery", "toc", "mbox-small",
                "navbox-styles", "catlinks", "mw-editsection"}
SYMBOL_ONLY = re.compile(r"^[\W_✓✔✗✘×—–-]*$")
WS = re.compile(r"\s+")
REFMARK = re.compile(r"\[\s*(\d+|[a-z]|note \d+|citation needed|[A-Z][a-z ]+ needed|clarification needed|when\?|which\?|nb \d+)\s*\]", re.I)
PAR_MAX = 900

def clean(t):
    t = unicodedata.normalize("NFC", t.replace("\xa0", " "))
    t = REFMARK.sub("", t)
    t = WS.sub(" ", t).strip()
    t = re.sub(r"\s+([,.;:)])", r"\1", t).replace("( ", "(")
    if t[:1] in "#|": t = "​" + t
    return t

def skip(el):
    cls = set(el.get("class") or [])
    if el.name in ("style", "script", "figure", "meta", "link", "img", "map", "noscript", "sup", "audio", "video"):
        return el.name != "sup" or "reference" in cls or True
    return bool(cls & SKIP_CLASSES) or el.get("role") == "navigation"

def text_of(el):
    el = BeautifulSoup(str(el), "lxml")
    for x in el.select("sup.reference, sup.noprint, span.mw-ref, style, .mw-editsection, .sortkey, span[style*='display:none'], .noprint"):
        x.decompose()
    for br in el.find_all("br"): br.replace_with(", ")
    return clean(el.get_text(" "))

def table_rows(tab):
    """wikitable -> list of rows (list of cell strings), rowspan/colspan expanded; header row(s) detected."""
    grid, carry = [], {}  # carry: col -> (remaining, text)
    for tr in tab.find_all("tr"):
        if tr.find_parent("table") is not tab: continue
        cells = [c for c in tr.find_all(["th", "td"], recursive=False)]
        row, col, ci = [], 0, 0
        while ci < len(cells) or col in carry:
            if col in carry:
                n, t = carry[col]; row.append(t)
                if n <= 1: del carry[col]
                else: carry[col] = (n - 1, t)
                col += 1; continue
            c = cells[ci]; ci += 1; t = text_of(c)
            try: rs = int(re.sub(r"\D", "", c.get("rowspan", "1")) or 1)
            except ValueError: rs = 1
            try: cs = int(re.sub(r"\D", "", c.get("colspan", "1")) or 1)
            except ValueError: cs = 1
            for _ in range(min(cs, 20)):
                if rs > 1: carry[col] = (rs - 1, t)
                row.append(t); col += 1
        grid.append((row, all(c.name == "th" for c in cells) and bool(cells)))
    return grid

def table_lines(tab):
    grid = table_rows(tab)
    hd = next((r for r, h in grid if h and any(r)), None)
    if hd:  # colspan header ("Territory" over flag + name): drop the duplicated column positions from every row
        dup = {i for i in range(1, len(hd)) if hd[i] == hd[i - 1]}
        if dup: grid = [([v for i, v in enumerate(r) if i not in dup], h) for r, h in grid]
    header, lines, group = None, [], ""
    for row, is_head in grid:
        if not any(row): continue
        if is_head and header is None:
            header = row; continue
        if is_head and header is not None and len(set(row)) == 1:
            group = row[0]; continue
        if is_head and header is not None and row == header: continue
        vals = [v for v in row]
        if len(set(v for v in vals if v)) == 1 and len(vals) > 1 and header and len(header) > 2 and vals.count(vals[0]) == len(vals):
            group = vals[0]; continue  # colspan group row ("China")
        if len(vals) == 1 and header and len(header) > 1:
            group = vals[0]; continue
        while header and len(vals) > len(header) and not vals[-1].strip("\u200b "):
            vals = vals[:-1]  # stray empty trailing cells (malformed rows)
        if header and len(vals) == len(header) + 1 and vals[0]:
            group, vals = vals[0], vals[1:]  # rowspan group cell ("China" spanning Hong Kong, Macau)
        key = vals[0] if vals else ""
        parts = []
        for i, v in enumerate(vals[1:], 1):
            if not v or SYMBOL_ONLY.match(v): continue
            h = header[i] if header and i < len(header) else ""
            if h and h.lower() in ("reciprocity",): continue
            if i == 1 and re.search(r"requirement|conditions of access|status", h, re.I): h = ""  # the status column reads unlabelled
            h = re.sub(r"\s*\(excluding departure fees\)", "", h)
            parts.append(f"{h}: {v}" if h and not SYMBOL_ONLY.match(h) else v)
        if not key and not parts: continue
        name = f"{group} / {key}" if group and key and group != key else (key or group)
        lines.append(f"{name}: " + "; ".join(parts) if parts else name)
    return lines

def pack_rows(lines, ctx):
    pars, cur = [], []
    for l in lines:
        if len(l) > PAR_MAX * 2: l = l[:PAR_MAX * 2].rsplit(" ", 1)[0] + " …"
        if cur and sum(len(x) + 1 for x in cur) + len(l) > PAR_MAX:
            pars.append("\n".join([ctx] + cur)); cur = []
        cur.append(l)
    if cur: pars.append("\n".join([ctx] + cur))
    return pars

def list_block(el):
    items = [text_of(li) for li in el.find_all("li", recursive=False)]
    items = [i for i in items if i]
    if not items: return []
    if len(items) >= 4 and max(len(i) for i in items) <= 60:
        line = ", ".join(items) + "."
        return [line]
    return ["- " + i for i in items]

def convert_page(title, html):
    soup = BeautifulSoup(html, "lxml")
    root = soup.select_one("div.mw-parser-output") or soup
    out, sec, drop = [], [title], [False]  # sec: title + heading stack
    lt = next((t for t in (text_of(x) for x in root.find_all("p", recursive=False)) if len(t) > 50), "")
    m = re.search(r"(?:citizens|nationals|holders) of (?:the )?([A-Z][\w'’ -]{1,40}?)(?:[.,;]| who| and |$)", lt)
    demo = [f" (citizens of {m.group(1).strip()})" if m and title.startswith("Visa requirements") else ""]
    stats = {"tables": 0, "rows": 0}
    def heading(level, txt):
        txt = clean(txt)
        while len(sec) > max(level - 1, 1): sec.pop()
        while len(sec) < level - 1: sec.append("")
        sec.append(txt)
        if level == 2: drop[0] = bool(BOILER.match(txt))
        elif drop[0] and level > 2: pass
        if not drop[0]: out.append("#" * level + " " + txt)
    def walk(el):
        for c in el.children:
            if isinstance(c, NavigableString): continue
            if not isinstance(c, Tag) or skip(c): continue
            cls = set(c.get("class") or [])
            if "mw-heading" in cls:
                h = c.find(re.compile(r"^h[2-6]$"))
                if h: heading(int(h.name[1]), h.get_text(" "))
                continue
            if re.fullmatch(r"h[2-6]", c.name or ""):
                heading(int(c.name[1]), c.get_text(" ")); continue
            if drop[0]: continue
            if c.name == "p":
                t = text_of(c)
                if len(t) > 1: out.append(t)
            elif c.name in ("ul", "ol"):
                ls = list_block(c)
                if ls: out.append("\n".join(ls))
            elif c.name == "dl":
                t = text_of(c)
                if t: out.append(t)
            elif c.name == "table":
                ncol = max((len(tr.find_all(["th", "td"], recursive=False)) for tr in c.find_all("tr") if tr.find_parent("table") is c), default=0)
                if "wikitable" not in cls or ncol <= 1:
                    stats["layout_tables"] = stats.get("layout_tables", 0) + 1
                    walk(c)  # layout table (flag lists in columns) or one-column box: walk the cells' paragraphs and lists
                    continue
                if "wikitable" in cls:
                    ls = table_lines(c); stats["tables"] += 1; stats["rows"] += len(ls)
                    ctx = ", ".join([sec[0] + demo[0]] + [x for x in sec[1:] if x]) + ":"
                    out.extend(pack_rows(ls, ctx))
            elif c.name in ("tbody", "thead", "tr"):
                walk(c)
            elif c.name in ("td", "th"):
                if c.find(["p", "ul", "ol", "table", "dl"]): walk(c)
                else:
                    t = text_of(c)
                    if len(t) > 1: out.append(t)
            elif c.name in ("div", "section", "center", "span", "blockquote"):
                walk(c)
    walk(root)
    lv = lambda x: len(x) - len(x.lstrip("#")) if x.startswith("#") else 0
    keep = []
    for i, x in enumerate(out):  # drop headings with no body before the next heading of the same or a higher level
        if lv(x):
            nxt = next((y for y in out[i + 1:] if y.strip()), None)
            if nxt is None or (lv(nxt) and lv(nxt) <= lv(x)): continue
        keep.append(x)
    text = "\n\n".join(x for x in keep if x.strip())
    text = re.sub(r"(^#{2,4} [^\n]*\n\n)(?=#{2,4} |\Z)", lambda m: m.group(1), text)
    return text, stats

def main(src, outdir, aliases_path=None):
    os.makedirs(outdir, exist_ok=True)
    aliases = json.load(open(aliases_path)) if aliases_path else {}
    docs, info = [], {"pages_in": 0, "kept": 0, "skipped_short": [], "tables": 0, "table_rows": 0, "chars": 0,
                      "snapshot": "revisions current at 2026-10-01T00:00:00Z (enwiki-20261001 dump index titles)", "rev_dates": {}}
    for l in open(src):
        p = json.loads(l); info["pages_in"] += 1
        text, st = convert_page(p["title"], p["html"])
        if len(text) < 200:
            info["skipped_short"].append(p["title"]); continue
        url = "https://en.wikipedia.org/wiki/" + p["title"].replace(" ", "_")
        doc = {"page_id": p["pageid"], "title": p["title"], "text": text, "source": "enwiki",
               "url": f"{url}?oldid={p['revid']}", "license": "CC BY-SA 4.0",
               "attribution": f"\"{p['title']}\", Wikipedia contributors, revision {p['revid']} of {p['rev_timestamp'][:10]} ({url}), CC BY-SA 4.0",
               "aliases": sorted(set(aliases.get(p["title"], [])))[:50], "views": 0, "infoboxes": None}
        docs.append(doc); info["kept"] += 1; info["tables"] += st["tables"]; info["table_rows"] += st["rows"]; info["chars"] += len(text)
        m = p["rev_timestamp"][:7]; info["rev_dates"][m] = info["rev_dates"].get(m, 0) + 1
    docs.sort(key=lambda d: d["title"])
    with open(f"{outdir}/visa.jsonl", "w") as f:
        for d in docs: f.write(json.dumps(d, ensure_ascii=False) + "\n")
    json.dump([{"source": d["source"], "title": d["title"], "url": d["url"], "license": d["license"], "chars": len(d["text"])} for d in docs],
              open(f"{outdir}/manifest.json", "w"), indent=1)
    info["requirements_articles"] = sum(d["title"].startswith("Visa requirements for") for d in docs)
    info["policy_articles"] = sum(d["title"].startswith("Visa polic") for d in docs)
    info["input_sha256"] = hashlib.sha256(open(src, "rb").read()).hexdigest()
    info["aliases"] = sum(len(d["aliases"]) for d in docs)
    json.dump(info, open(f"{outdir}/convert-info.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in info.items() if k not in ("rev_dates",)}, ensure_ascii=False)[:1500])

if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], a[1], a[a.index("--aliases") + 1] if "--aliases" in a else None)
