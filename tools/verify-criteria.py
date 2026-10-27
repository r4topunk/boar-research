#!/usr/bin/env python3
"""Verify the frozen criteria of the research record.

Usage (from the repository root):  python3 tools/verify-criteria.py [--verbose]

For every `*criterion*.sha256` and `*rule*.sha256` file under rnd/, each line "<sha256>  <file> [(through <marker>)]"
(or a bare sha256, which then refers to the .md file with the same stem) is checked against the released file:
whole file, or the text up to and including the `END FROZEN` marker when the line says "through".
Exits 0 when every pin verifies or is a documented exception (docs/PIN-EXCEPTIONS.md)."""
import hashlib, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXC_DOC = os.path.join(ROOT, "docs", "PIN-EXCEPTIONS.md")
HEX = re.compile(r"\b([0-9a-f]{64})\b")
MARK = re.compile(r"END FROZEN")


def candidates(data):
    yield data
    t = data.decode("utf-8", "replace")
    m = None
    for m in MARK.finditer(t):
        pass
    for m in MARK.finditer(t):
        end = t.find("\n", m.end())
        for cut in (m.start(), m.end(), end if end >= 0 else len(t), end + 1 if end >= 0 else len(t)):
            yield t[:cut].encode("utf-8")
        # the line before the marker
        ls = t.rfind("\n", 0, m.start())
        if ls >= 0:
            yield t[:ls].encode("utf-8"); yield t[:ls + 1].encode("utf-8")


def target(pin_path, line):
    d = os.path.dirname(pin_path)
    rest = HEX.sub("", line, count=1).strip()
    name = rest.split()[0] if rest else ""
    name = re.sub(r"^\*", "", name)
    if name:
        b = os.path.basename(name)
        for c in (os.path.join(d, name), os.path.join(d, b)):
            if os.path.isfile(c):
                return c
        return os.path.join(d, b)
    stem = os.path.basename(pin_path)[: -len(".sha256")]
    for ext in (".md", ""):
        c = os.path.join(d, stem + ext)
        if os.path.isfile(c):
            return c
    return os.path.join(d, stem + ".md")


def exceptions():
    try:
        t = open(EXC_DOC, encoding="utf-8").read()
    except OSError:
        return set()
    return set(re.findall(r"`(rnd/[^`]+\.sha256)`", t))


def main():
    verbose = "--verbose" in sys.argv
    exc = exceptions()
    ok = bad = missing = documented = 0
    for dp, dns, fns in os.walk(os.path.join(ROOT, "rnd")):
        for f in sorted(fns):
            if not f.endswith(".sha256") or not re.search(r"criterion|rule", f, re.I):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, ROOT)
            lines = [l for l in open(p, encoding="utf-8", errors="replace") if HEX.search(l)]
            if not lines:
                continue
            l = lines[-1]  # the last pin is the current one (earlier lines are earlier versions)
            want = HEX.search(l).group(1)
            tp = target(p, l)
            if not os.path.isfile(tp):
                missing += 1
                print("MISSING", rel, "->", os.path.relpath(tp, ROOT)) if verbose else None
                continue
            data = open(tp, "rb").read()
            if any(hashlib.sha256(c).hexdigest() == want for c in candidates(data)):
                ok += 1
            elif rel in exc:
                documented += 1
                print("DOCUMENTED", rel) if verbose else None
            else:
                bad += 1
                print("BAD", rel)
    print(f"criteria pins: ok {ok}, documented exceptions {documented}, bad {bad}, target missing {missing}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
