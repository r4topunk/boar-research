#!/usr/bin/env python3
"""Check H2 pool specs: route triggers, kit coverage, answer found in the source page text, and its position.

    python3 rnd/veil/h2-pool-round/check.py        # from <workspace>
"""
import json, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
from specs import S

D = "rnd/veil/h2-pool-round"
CACHE = f"{D}/wiki-cache"
os.makedirs(CACHE, exist_ok=True)
UA = {"User-Agent": "veil-rnd/0.1 (research contact: r4to; low-rate script)"}
START = re.compile(r"^(who|what|when|where|which|quem|o que|qual|quais|quando|onde|quantos|quantas|quanto tempo|is|é|tem|em que ano)\b", re.I)
BAD = re.compile(r"\b(compare|versus|difference between|diferença entre|why|explain|causes|effects|impact|calculate|compute|how much is|summarize|translate|list all|extract)\b|^how\b", re.I)


def extract(title, intro):
    fn = f"{CACHE}/{re.sub(r'[^A-Za-z0-9]+', '_', title)}{'_intro' if intro else ''}.txt"
    if os.path.exists(fn):
        return open(fn, encoding="utf-8").read()
    q = {"action": "query", "prop": "extracts", "explaintext": 1, "redirects": 1, "format": "json", "titles": title}
    if intro:
        q["exintro"] = 1
    for k in range(6):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request("https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(q), headers=UA), timeout=30))
            s = next(iter(d["query"]["pages"].values())).get("extract", "")
            open(fn, "w", encoding="utf-8").write(s)
            time.sleep(1.2)
            return s
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(10 * (k + 1)); continue
            raise


def position(title, toks):
    intro, full = extract(title, True), extract(title, False)
    para = intro.strip().split("\n")[0]
    first = re.split(r"(?<=[.!?])\s", para, maxsplit=1)[0]
    for name, txt in (("first sentence", first), ("first paragraph", para), ("intro (after the first paragraph)", intro), ("body (not in the intro)", full)):
        hit = [t for t in toks if t in txt]
        if hit:
            sent = next((s for s in re.split(r"(?<=[.!?])\s+", full) if hit[0] in s), "")
            return name, hit[0], sent.strip()[:220]
    return None, None, None


def main():
    pages = sorted({p for s in S for p in s[3]})
    open(f"{D}/pages.txt", "w").write("\n".join(pages) + "\n")
    out = subprocess.run([sys.executable, "rnd/kiln/tools/kit_coverage.py", "--file", f"{D}/pages.txt", "--json"], capture_output=True, text=True, check=True).stdout
    open(f"{D}/coverage.raw.jsonl", "w").write(out)
    cov = {json.loads(l)["term"]: json.loads(l)["verdict"] for l in out.splitlines() if l.strip()}
    res = []
    for i, (tpl, lang, q, pg, ans, verify, shape) in enumerate(S, 1):
        words = len(q.rstrip("?").split())
        route_ok = bool(START.match(q)) and words <= 12 and not BAD.search(q)
        checks = []
        for page, toks in verify:
            pos, tok, sent = position(page, toks)
            checks.append({"page": page, "found": tok, "position": pos, "sentence": sent})
        r = {"n": i, "template": tpl, "lang": lang, "question": q, "words": words, "route_ok": route_ok,
             "coverage": {p: cov.get(p) for p in pg}, "all_covered": all(cov.get(p) == "COVERED" for p in pg),
             "verified": all(c["found"] for c in checks), "checks": checks}
        res.append(r)
        flag = "" if (r["route_ok"] and r["all_covered"] and r["verified"]) else "  <-- " + ", ".join(
            x for x, ok in (("route", r["route_ok"]), ("coverage", r["all_covered"]), ("verify", r["verified"])) if not ok)
        print(f"{i:2d} {tpl} {lang} {q[:58]:58s} {[c['position'] for c in checks]}{flag}")
    json.dump(res, open(f"{D}/check.json", "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
