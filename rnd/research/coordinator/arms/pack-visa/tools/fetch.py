#!/usr/bin/env python3
"""PACK-VISA fetch (2026-10-19). Targeted MediaWiki API fetch of the visa articles listed in the enwiki-20261001 dump index.
Why the API: the mini holds only the 20261001 multistream *index* (article text was range-fetched for WIKIFULL stage B and
deleted), and the visa articles are template-built tables whose rendered values ({{yes|Visa not required}}, footnotes,
day counts) are lost by the pack builder's wikitext cleaner. So each page is rendered by the API at the revision that was
current on 2026-10-01T00:00:00Z (the dump snapshot), keeping the snapshot date.
Polite: one request at a time, >= 2 s apart, maxlag=5, descriptive User-Agent (no personal data), resumable cache.
usage: fetch.py <index-titles.txt> <outdir>
  out: <outdir>/pages.jsonl (title, pageid, revid, rev_timestamp, html), <outdir>/titles.json (resolution log)
"""
import json, os, sys, time, requests

API = "https://en.wikipedia.org/w/api.php"
UA = "BOAR-pack-builder/0.1 (offline research build; https://www.mediawiki.org/wiki/API:Etiquette)"
SNAP = "2026-10-01T00:00:00Z"
S = requests.Session(); S.headers["User-Agent"] = UA
_last = [0.0]

def get(params):
    for attempt in range(6):
        wait = 2.0 - (time.time() - _last[0])
        if wait > 0: time.sleep(wait)
        _last[0] = time.time()
        try:
            r = S.get(API, params={**params, "format": "json", "formatversion": 2, "maxlag": 5}, timeout=120)
        except requests.RequestException as e:
            print(f"net error {e}; retry", file=sys.stderr); time.sleep(10 * (attempt + 1)); continue
        if r.status_code in (429, 503) or "maxlag" in r.text[:300]:
            print(f"HTTP {r.status_code}; backing off", file=sys.stderr, flush=True)
            time.sleep(int(r.headers.get("Retry-After", 30)) + 30 * attempt); continue
        r.raise_for_status(); j = r.json()
        if "error" in j: raise RuntimeError(j["error"])
        return j
    raise RuntimeError("too many retries")

def main(idx, out):
    os.makedirs(out, exist_ok=True)
    titles = sorted({l.rstrip("\n").split(":", 2)[2] for l in open(idx) if l.count(":") >= 2})
    # 1) redirect filter + page ids (50 per call)
    info = {}
    for i in range(0, len(titles), 50):
        j = get({"action": "query", "prop": "info", "titles": "|".join(titles[i:i + 50])})
        for p in j["query"]["pages"]:
            info[p["title"]] = {"pageid": p.get("pageid"), "redirect": p.get("redirect", False), "missing": p.get("missing", False), "ns": p.get("ns")}
    keep = sorted(t for t, v in info.items() if not v["redirect"] and not v["missing"] and v["ns"] == 0)
    print(f"index titles {len(titles)}; non-redirect articles {len(keep)}", file=sys.stderr)
    done = set()
    pf = f"{out}/pages.jsonl"
    if os.path.exists(pf):
        done = {json.loads(l)["title"] for l in open(pf)}
    log = {"index_titles": len(titles), "non_redirect": len(keep), "snapshot": SNAP, "skipped_no_rev_before_snapshot": []}
    with open(pf, "a") as f:
        for n, t in enumerate(keep):
            if t in done: continue
            j = get({"action": "query", "prop": "revisions", "titles": t, "rvstart": SNAP, "rvdir": "older", "rvlimit": 1, "rvprop": "ids|timestamp"})
            pg = j["query"]["pages"][0]; revs = pg.get("revisions") or []
            if not revs:
                log["skipped_no_rev_before_snapshot"].append(t); continue
            rev = revs[0]
            p = get({"action": "parse", "oldid": rev["revid"], "prop": "text", "disablelimitreport": 1, "disableeditsection": 1})
            f.write(json.dumps({"title": t, "pageid": pg["pageid"], "revid": rev["revid"], "rev_timestamp": rev["timestamp"],
                                "html": p["parse"]["text"]}, ensure_ascii=False) + "\n"); f.flush()
            if n % 25 == 0: print(f"{n}/{len(keep)} {t}", file=sys.stderr)
    json.dump(log, open(f"{out}/titles.json", "w"), indent=1)

if __name__ == "__main__":
    main(*sys.argv[1:3])
