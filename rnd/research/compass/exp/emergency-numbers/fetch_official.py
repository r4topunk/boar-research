#!/usr/bin/env python3
"""Fetch an official page RAW (curl, browser UA) and save raw + text snapshot.

usage: fetch_official.py <slug> <url>
writes snapshots-official/<slug>.raw.(html|pdf) and snapshots-official/<slug>.txt
Text = stdlib HTMLParser visible text (script/style dropped), entities unescaped,
whitespace collapsed to single spaces per block, one block per line. PDFs via pdftotext.
"""
import subprocess, sys, re, html
from html.parser import HTMLParser
from pathlib import Path

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
SNAP = Path(__file__).parent / "snapshots-official"
BLOCK = {"p", "div", "li", "br", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "td", "th",
         "section", "article", "header", "footer", "ul", "ol", "table", "dt", "dd", "nav", "span_block"}


class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "template", "svg"):
            self.skip += 1
        if tag in BLOCK:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "template", "svg") and self.skip:
            self.skip -= 1
        if tag in BLOCK:
            self.out.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def to_text(raw: str) -> str:
    p = Text()
    p.feed(raw)
    t = html.unescape("".join(p.out)).replace(" ", " ")
    lines = [re.sub(r"[ \t\r\f\v]+", " ", l).strip() for l in t.split("\n")]
    return "\n".join(l for l in lines if l) + "\n"


def main():
    slug, url = sys.argv[1], sys.argv[2]
    SNAP.mkdir(exist_ok=True)
    tmp = SNAP / f"{slug}.raw"
    r = subprocess.run(["curl", "-sSL", "--compressed", "-m", "60", "-A", UA,
                        "-H", "Accept-Language: es,pt;q=0.9,en;q=0.8",
                        "-o", str(tmp), "-w", "%{http_code} %{content_type}", url],
                       capture_output=True, text=True)
    print(slug, r.stdout, r.stderr.strip())
    code = r.stdout.split(" ")[0]
    if not tmp.exists() or not code.startswith(("2", "3")):
        tmp.unlink(missing_ok=True)
        sys.exit(f"  FAILED {slug} (HTTP {code})")
    data = tmp.read_bytes()
    if data[:5] == b"%PDF-":
        raw = tmp.with_suffix(".raw.pdf"); tmp.rename(raw)
        txt = subprocess.run(["pdftotext", "-layout", str(raw), "-"], capture_output=True, text=True).stdout
        txt = "\n".join(re.sub(r"[ \t]+", " ", l).strip() for l in txt.splitlines() if l.strip()) + "\n"
    else:
        raw = tmp.with_suffix(".raw.html"); tmp.rename(raw)
        txt = to_text(data.decode("utf-8", errors="replace"))
    (SNAP / f"{slug}.txt").write_text(txt)
    print(f"  -> {raw.name} ({len(data)} B), {slug}.txt ({len(txt)} chars)")


if __name__ == "__main__":
    main()
