#!/usr/bin/env python3
"""r11 sanity report (ENGFIX-FACTS 2026-10-23). Usage: python3 -I sanity_r11.py <facts.v1.json> [<previous facts.v1.json>]
Currency: count distribution, every country with 0 or >= 3, the eurozone (+ euro users) must carry the euro, no crypto/obsolete label.
Nobel: laureates per year 1901..max against the rule (1 per year; 2 in 1904, 1917, 1966, 1974; none 1914, 1918, 1935, 1940-1943), one year per person."""
import collections, json, sys
d = json.load(open(sys.argv[1]))
C = [e for e in d["entities"] if e["k"] == "country"]
print("build", d["build"], "countries", len(C))
dist = collections.Counter(len(e.get("cur", [])) for e in C)
print("currency count per country:", dict(sorted(dist.items())))
print("countries with 0 currencies:", [e["n"] for e in C if not e.get("cur")])
print("countries with >= 3 currencies (suspicious):", [(e["n"], e["cur"]) for e in C if len(e.get("cur", [])) >= 3] or "none")
print("countries with 2 currencies:", [(e["n"], e["cur"]) for e in C if len(e.get("cur", [])) == 2])
EZ = ["Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Estonia", "Finland", "France", "Germany", "Greece", "Ireland", "Italy", "Latvia",
      "Lithuania", "Luxembourg", "Malta", "Kingdom of the Netherlands", "Portugal", "Slovakia", "Slovenia", "Spain",
      "Monaco", "San Marino", "Vatican City", "Andorra", "Montenegro", "Kosovo"]
names = {e["n"]: e for e in C}
bad = [(n, names[n].get("cur")) for n in EZ if n in names and "euro" not in names[n].get("cur", [])]
print("euro users checked", len([n for n in EZ if n in names]), "missing", [n for n in EZ if n not in names], "without euro:", bad or "none")
print("euro on", sum("euro" in e.get("cur", []) for e in C), "countries")
print("El Salvador", names["El Salvador"].get("cur"), "| Zimbabwe", names["Zimbabwe"].get("cur"), "| Marshall Islands", names["Marshall Islands"].get("cur"))
wrong = [(e["n"], c) for e in C for c in e.get("cur", []) if any(x in c.lower() for x in ("bitcoin", "sov", "talonas", "deutsche mark", "franc de", "zimbabwean dollar", "q4916"))]
print("crypto/obsolete labels left:", wrong or "none")
win = next(e for e in d["entities"] if e.get("win"))["win"]
SHARED, NONE = {"1904", "1917", "1966", "1974"}, {"1914", "1918", "1935", "1940", "1941", "1942", "1943"}
last = max(int(y) for y in win)
viol = []
for y in range(1901, last + 1):
    n = len(win.get(str(y), []))
    exp = 0 if str(y) in NONE else 2 if str(y) in SHARED else 1
    if n != exp: viol.append((y, n, exp))
print("Nobel Literature years", min(win), "-", max(win), "listed", len(win), "laureates", sum(len(v) for v in win.values()))
print("laureates per year histogram:", dict(sorted(collections.Counter(len(v) for v in win.values()).items())), "| years with 2:", sorted(y for y, v in win.items() if len(v) == 2))
print("years absent:", [y for y in range(1901, last + 1) if str(y) not in win])
print("violations of the per-year rule:", viol or "none")
per = collections.defaultdict(list)
for y, ws in win.items():
    for w in ws: per[w].append(y)
print("people in more than one year:", {w: y for w, y in per.items() if len(y) > 1} or "none")
print("1988:", win["1988"], "| 1999:", win["1999"], "| 2026:", win.get("2026"))
