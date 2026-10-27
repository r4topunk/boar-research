# Parse Wikipedia "List of emergency telephone numbers" (raw wikitext, rev 1377218654, 2026-09-28) → police/ambulance/fire/notes.
import re, json
t = open("wiki.txt").read()
out = {}
for r in t.split("\n|-"):
    m = re.search(r"\{\{[Ff]lag(?:country)?\|([^}|]+)", r)
    if not m: continue
    name = m.group(1).strip()
    cells = [l[1:].strip() for l in r.strip().split("\n") if l.startswith("|") and not l.startswith("|}")]
    if not cells or "lag" not in cells[0]: continue
    vals = []
    for c in cells[1:]:
        span = re.search(r'colspan="?(\d)', c); n = int(span.group(1)) if span else 1
        txt = c.split("|", 1)[1] if re.match(r'\s*(align|colspan|style|rowspan)', c) and "|" in c else c
        txt = re.sub(r"'''|''|\[\[(?:[^|\]]*\|)?([^\]]*)\]\]|<ref[^>]*?/>|<ref.*?</ref>|\{\{[^}]*\}\}", lambda x: x.group(1) or "", txt).strip()
        vals += [txt] * n
    vals += [""] * (4 - len(vals))
    out[name] = {"police": vals[0], "ambulance": vals[1], "fire": vals[2], "notes": " ".join(vals[3:])[:300]}
json.dump(out, open("wiki-numbers.json", "w"), ensure_ascii=False, indent=0)
print(len(out))
for c in ["Thailand","Brazil","Portugal","Spain","France","Germany","Italy","United Kingdom","United States","Canada","Mexico","Argentina","Japan","China","South Korea","India","Australia","New Zealand","Vietnam","Philippines","Turkey","Peru","Indonesia","Sri Lanka","Chile","Greece"]:
    print(f"{c:15}", out.get(c, "NOT FOUND"))
