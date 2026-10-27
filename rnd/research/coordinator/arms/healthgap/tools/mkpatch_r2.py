"""Build tools/healthgap-r2.patch (r1 tools/healthgap.patch + review/healthgap-r2.fix.diff) from `git diff` of clean cut 7 vs cut 7 + both: rewrite paths, and trim
the leading context of the detector-hook hunk to its blank line (PR-1 has the NUMGUARD block above it; the 3 trailing
context lines are shared by both trees)."""
import re, sys
raw, out = sys.argv[1:3]
s = open(raw).read()
s = re.sub(r"([ab])/be-0cfd4a77-cut7(?:-healthgap)?/src/routing/", r"\1/src/routing/", s)
lines = s.split("\n"); res = []; i = 0
while i < len(lines):
    l = lines[i]
    m = re.match(r"^@@ -(\d+),(\d+) \+(\d+),(\d+) @@(.*)$", l)
    if not m: res.append(l); i += 1; continue
    j = i + 1; body = []
    while j < len(lines) and not lines[j].startswith(("@@", "diff --git")): body.append(lines[j]); j += 1
    if any("HEALTHGAP (deps.healthgap)" in b for b in body):
        lead = 0
        while body[lead].startswith(" "): lead += 1
        drop = lead - 1
        assert drop >= 0 and body[drop] == " ", body[:lead]
        body = body[drop:]
        o, oc, n, nc = map(int, m.groups()[:4])
        l = f"@@ -{o+drop},{oc-drop} +{n+drop},{nc-drop} @@{m.group(5)}"
    res.append(l); res.extend(body); i = j
open(out, "w").write("\n".join(res))
