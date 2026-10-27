#!/usr/bin/env python3
"""WEB-ACTIONS-B item 5 (T12.1 / W25): OSM diet:vegan yes/only/limited inside our tiles (kit-vgps2 shipped kit; all 8,374 hosted world tiles)
vs worldwide taginfo counts (WEB-LOG tick 12 #1, data until 2026-10-20). Counts distinct OSM refs, source 0 (OSM) only. 0 LLM.
Usage: python3 -I b5_vegan_tiles.py -> ../aggregates/b5-vegan-tiles.json"""
import sqlite3, glob, json, os, hashlib, collections
P = "<workspace>/shared-data/poi"; OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAGINFO = {"yes": 48318, "no": 14648, "only": 3926, "limited": 1336, "on_demand": 56}
def count(files):
    refs = collections.defaultdict(set); dup = 0; total = 0
    for f in files:
        c = sqlite3.connect(f"file:{f}?mode=ro", uri=True)
        for ref, v in c.execute("select ref, vegan from pois where source = 0 and vegan is not null and vegan != ''"):
            if ref in refs[v]: dup += 1
            refs[v].add(ref)
        total += c.execute("select count(*) from pois where source = 0").fetchone()[0]; c.close()
    n = {v: len(s) for v, s in refs.items()}
    return dict(tiles=len(files), osm_pois=total, by_value=dict(sorted(n.items(), key=lambda x: -x[1])), dup_refs_across_tiles=dup,
                share_of_taginfo={v: round(n.get(v, 0) / TAGINFO[v], 4) for v in ("yes", "only", "limited", "no")},
                yes_only_limited=sum(n.get(v, 0) for v in ("yes", "only", "limited")))
res = {"taginfo_worldwide_2026_10_20": TAGINFO, "taginfo_yes_only_limited": sum(TAGINFO[v] for v in ("yes", "only", "limited")),
       "kit_vgps2": count(sorted(glob.glob(f"{P}/kit-vgps2/t-*.sqlite"))),
       "kit_vexact": count(sorted(glob.glob(f"{P}/kit-vexact/t-*.sqlite"))),
       "world_8374": count(sorted(glob.glob(f"{P}/geofabrik/work/tiles/t-*.sqlite")))}
for k in ("kit_vgps2", "kit_vexact", "world_8374"):
    res[k]["share_yes_only_limited_of_taginfo"] = round(res[k]["yes_only_limited"] / res["taginfo_yes_only_limited"], 4)
s = json.dumps(res, indent=1); open(f"{OUT}/aggregates/b5-vegan-tiles.json", "w").write(s); print(s); print("sha256", hashlib.sha256(s.encode()).hexdigest())
