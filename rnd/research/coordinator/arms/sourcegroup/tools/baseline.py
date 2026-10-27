"""SOURCEGROUP step 1 (0 LLM): duplicate pages per trace. Page key = the URL in the source label, else the title
(trimmed, spaces collapsed, lowercased) -- the same rule as src/routing/sourceGroups.ts pageKey."""
import json, re, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from sets import load, A
URL = re.compile(r"https?://[^\s)\]]+")
def key(s):
    m = URL.search(s.get("source") or "")
    return "url:" + m.group(0).rstrip(".,;") if m else "title:" + re.sub(r"\s+", " ", (s.get("title") or "").strip()).lower()
def mk(n): return re.findall(r"\[(\d+)\]", n)
out = {}
for name, rows in load().items():
    w = [r for r in rows if r["sources"]]
    per = []
    for r in w:
        keys = [key(s) for s in r["sources"]]
        before, after = len(keys), len(set(keys))
        # markers that point at two passages of one page (would merge into one number)
        cited = sorted({int(n) for n in mk(r["text"]) if 1 <= int(n) <= before})
        citedPages = {keys[n - 1] for n in cited}
        per.append({"id": r["id"], "before": before, "after": after, "dup": before - after, "citedShown": r["citedShown"],
                    "markers": len(mk(r["text"])), "citedPassages": len(cited), "citedPages": len(citedPages)})
    d = [p for p in per if p["dup"] > 0]
    out[name] = {
        "traces": len(rows), "withSources": len(w), "withDup": len(d),
        "shareWithDup_ofWithSources": round(len(d) / len(w), 3) if w else None,
        "shareWithDup_ofAll": round(len(d) / len(rows), 3) if rows else None,
        "extraEntries": sum(p["dup"] for p in per),
        "meanEntriesBefore": round(sum(p["before"] for p in per) / len(per), 3) if per else None,
        "meanEntriesAfter": round(sum(p["after"] for p in per) / len(per), 3) if per else None,
        "withDupAndCited": sum(1 for p in d if p["citedShown"] or p["citedPassages"] > 0),
        "withMarkers": sum(1 for p in per if p["markers"] > 0),
        "markersHitSamePageTwice": sum(1 for p in per if p["citedPassages"] > p["citedPages"]),
        "maxBefore": max((p["before"] for p in per), default=0), "worst": sorted(d, key=lambda p: -p["dup"])[:3],
    }
json.dump(out, open(f"{A}/sourcegroup/aggregates/sourcegroup-baseline.json", "w"), indent=1)
print(f"{'set':18} {'n':>4} {'src':>4} {'dup':>4} {'share':>6} {'extra':>5} {'before':>6} {'after':>6} {'dup&cited':>9} {'2x-page':>7}")
for k, v in out.items():
    print(f"{k:18} {v['traces']:>4} {v['withSources']:>4} {v['withDup']:>4} {v['shareWithDup_ofWithSources'] or 0:>6} {v['extraEntries']:>5} {v['meanEntriesBefore'] or 0:>6} {v['meanEntriesAfter'] or 0:>6} {v['withDupAndCited']:>9} {v['markersHitSamePageTwice']:>7}")
