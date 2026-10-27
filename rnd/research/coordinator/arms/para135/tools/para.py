# PARA135 paragraph splitter (frozen with PARA135-criterion.md). paragraphs(text) -> (banner|None, [[sentences of paragraph 1], [paragraph 2], ...])
# Sentence rules = TOPICS27 split.py (banner lines, markdown strip, heading drop, sentence regex, >= 4 words with a letter), applied per paragraph.
# Paragraph boundary: a blank line; or a newline before a prose line (not a bullet, not a heading) when the previous kept line ends in . ! ? or a closing quote/paren;
# a dropped heading also closes the current paragraph. Bullet lines (- * • or 1. 1)) stay in the current paragraph. Paragraphs with 0 sentences are not counted.
import re
from split import BANNER
BUL = re.compile(r"^([-*•]|\d+[.)])\s+")
def _sents(l):
    out = []
    for s in re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"(])', l):
        s = s.strip()
        if len(s.split()) < 4 or not re.search(r"[A-Za-z]", s): continue
        out.append(s)
    return out
def paragraphs(text):
    banner = None; paras = []; cur = []; prev_end = True
    raw = text.replace("\r", "").split("\n")
    lines = [l.strip() for l in raw]
    nz = [i for i, l in enumerate(lines) if l]
    def close():
        nonlocal cur
        if cur: paras.append(cur)
        cur = []
    for j, i in enumerate(nz):
        l = lines[i]
        if j > 0 and i - nz[j - 1] > 1: close()                      # blank line(s) before this line
        if BANNER.match(l):
            banner = (banner + " | " if banner else "") + l; continue
        isbul = bool(BUL.match(l))
        l2 = re.sub(r"^#+\s*", "", l); l2 = BUL.sub("", l2); l2 = l2.replace("**", "").replace("__", "")
        if not l2: continue
        if len(l2.split()) <= 8 and not re.search(r"[.!?:]$", l2) and j < len(nz) - 1:  # heading
            close(); prev_end = True; continue
        if not isbul and cur and prev_end: close()                   # new prose line after a finished sentence
        cur.extend(_sents(l2)); prev_end = bool(re.search(r"[.!?][\"')\]]*$", l2))
    close()
    return banner, paras
