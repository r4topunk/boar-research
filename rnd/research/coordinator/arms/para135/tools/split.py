# TOPICS27 sentence splitter (frozen with TOPICS27-criterion.md). split(text) -> (banner|None, [sentences])
import re
BANNER = re.compile(r"^(Not found in this phone's offline library\.[^\n]*|From the model's memory[^\n]*)$", re.I)
def split(text):
    banner = None; out = []
    lines = [l.strip() for l in text.replace("\r", "").split("\n")]
    lines = [l for l in lines if l]
    for i, l in enumerate(lines):
        if BANNER.match(l):
            banner = (banner + " | " if banner else "") + l; continue
        l = re.sub(r"^#+\s*", "", l); l = re.sub(r"^([-*•]|\d+[.)])\s+", "", l); l = l.replace("**", "").replace("__", "")
        if not l: continue
        words = l.split()
        if len(words) <= 8 and not re.search(r"[.!?:]$", l) and i < len(lines) - 1: continue  # heading
        for s in re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"(])', l):
            s = s.strip()
            if len(s.split()) < 4 or not re.search(r"[A-Za-z]", s): continue
            out.append(s)
    return banner, out
