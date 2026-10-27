import sys, random
FWMAX = int(sys.argv[2]); rows = []
for l in open(sys.argv[1], encoding="utf-8"):
    o, ln, p, t = l.rstrip("\n").split("\t", 3); rows.append((int(o), int(ln), int(p)))
def by(rs): d = {o: ln for o, ln, _ in rs}; return len(rs), len(d), sum(d.values())
new = [r for r in rows if r[2] > FWMAX]; old = [r for r in rows if r[2] <= FWMAX]
print("new", by(new)); print("old", by(old))
for f in (0.1, 0.2, 0.3, 0.4, 0.5):
    random.seed(11); s = random.sample(old, round(len(old) * f))
    print("old frac", f, by(s), "new+old", by(new + s))
    random.seed(11); u = random.sample(rows, round(len(rows) * f)); print("  uniform", f, by(u))
