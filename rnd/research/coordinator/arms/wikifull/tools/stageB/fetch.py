#!/usr/bin/env python3
"""WIKIFULL stage B fetch: HTTP range reads of the enwiki 20261001 multistream dump for the streams in delta.tsv,
coalesced into ranges (gap <= GAP bytes, range <= MAXR bytes), each 100-page bz2 stream decompressed on its own;
keeps delta pages that are ns 0 and not #REDIRECT; writes raw.jsonl {page_id,title,wikitext}. Resumable (done-ranges
file). usage: fetch.py DELTA.tsv OUTDIR [--sample FRACTION]  (2 sequential workers, polite UA)"""
import bz2, json, os, re, sys, time, random, http.client, threading
from concurrent.futures import ThreadPoolExecutor
HOST = "dumps.wikimedia.org"; PATH = "/enwiki/20261001/enwiki-20261001-pages-articles-multistream.xml.bz2"
UA = "boar-research-wikifull/0.1 (offline research; range reads)"
MAXR = 48 << 20
dl, od = sys.argv[1], sys.argv[2]
arg = lambda k, d: type(d)(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
frac = arg("--old-frac", 1.0); FWMAX = arg("--fwmax", 0); GAP = arg("--gap", 256 << 10); W = arg("--workers", 2)
want = {}; ln = {}
for line in open(dl, encoding="utf-8"):
    off, l, pid, t = line.rstrip("\n").split("\t", 3)
    want.setdefault(int(off), set()).add(int(pid)); ln[int(off)] = int(l)
streams = sorted(want)
# stratified: every page with page_id > FWMAX (created after the FineWiki snapshot) + a seed-11 uniform sample
# (fraction --old-frac) of the older-id delta pages
if frac < 1:
    random.seed(11); old = sorted(p for s in want.values() for p in s if p <= FWMAX)
    keep = set(random.sample(old, round(len(old) * frac))) | {p for s in want.values() for p in s if p > FWMAX}
    want = {o: s & keep for o, s in want.items() if s & keep}; streams = sorted(want)
ranges = []; cur = None
for o in streams:
    if cur and o - (cur[1]) <= GAP and (o + ln[o]) - cur[0] <= MAXR: cur[1] = o + ln[o]; cur[2].append(o)
    else:
        cur = [o, o + ln[o], [o]]; ranges.append(cur)
donef = f"{od}/done-ranges.txt"; done = set(open(donef).read().split()) if os.path.exists(donef) else set()
out = open(f"{od}/raw.jsonl", "a", encoding="utf-8"); lk = threading.Lock()
stats = dict(ranges=len(ranges), streams=len(streams), bytes=0, pages_kept=0, redirects=0, other_ns=0, t0=time.time())
stats["pages_wanted"] = sum(len(v) for v in want.values()); stats["planned_bytes"] = sum(r[1] - r[0] for r in ranges); stats["old_frac"] = frac
print(json.dumps({k: v for k, v in stats.items() if k != "t0"}), flush=True)
if "--dry-run" in sys.argv: sys.exit(0)
tl = threading.local()
def get(a, b):
    for attempt in range(8):
        try:
            if not getattr(tl, "c", None): tl.c = http.client.HTTPSConnection(HOST, timeout=120)
            tl.c.request("GET", PATH, headers={"Range": f"bytes={a}-{b-1}", "User-Agent": UA})
            r = tl.c.getresponse(); d = r.read()
            if r.status == 206 and len(d) == b - a: return d
            raise IOError(f"status {r.status} len {len(d)}")
        except Exception as e:
            tl.c = None; time.sleep(min(60, 5 * 2 ** attempt)); last = e
    raise last
PG = re.compile(r"<page>(.*?)</page>", re.S)
def tag(x, n):
    m = re.search(rf"<{n}(?:\s[^>]*)?>(.*?)</{n}>", x, re.S); return m.group(1) if m else ""
def unx(s): return s.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&#039;", "'").replace("&apos;", "'").replace("&amp;", "&")
def work(r):
    key = f"{r[0]}-{r[1]}"
    if key in done: return
    buf = get(r[0], r[1]); recs = []; red = ons = 0
    for o in r[2]:
        xml = bz2.decompress(buf[o - r[0]: o - r[0] + ln[o]]).decode("utf-8")
        for m in PG.finditer(xml):
            x = m.group(1); pid = int(tag(x, "id"))
            if pid not in want[o]: continue
            if tag(x, "ns") != "0": ons += 1; continue
            txt = unx(tag(x, "text"))
            if "<redirect" in x or re.match(r"\s*#redirect", txt, re.I): red += 1; continue
            recs.append(json.dumps(dict(page_id=pid, title=unx(tag(x, "title")), wikitext=txt), ensure_ascii=False))
    with lk:
        for s in recs: out.write(s + "\n")
        out.flush(); open(donef, "a").write(key + "\n")
        stats["bytes"] += r[1] - r[0]; stats["pages_kept"] += len(recs); stats["redirects"] += red; stats["other_ns"] += ons
        stats["n"] = stats.get("n", 0) + 1
        if stats["n"] % 20 == 0 or stats["n"] == len(ranges):
            print(f"{stats['n']}/{len(ranges)} ranges, {stats['bytes']/1e9:.2f} GB, kept {stats['pages_kept']}, redir {stats['redirects']}, {time.time()-stats['t0']:.0f}s", flush=True)
with ThreadPoolExecutor(W) as ex: list(ex.map(work, ranges))
stats.pop("t0"); json.dump(stats, open(f"{od}/fetch-stats.json", "w"), indent=1); print("DONE", json.dumps(stats), flush=True)
