#!/usr/bin/env python3
"""TILE-PATH helper (0 LLM, read-only): which 1-degree places tiles a location needs, their bytes, and how many
vegan-tagged OSM places lie near it. Mirrors the engine: tileIdOf / tileIdsFor (wt/cut7 src/rag/poiRegions.ts:881-907)
and the vegan filter of PoiPack.within (src/rag/poiPack.ts:160-167, levels yes/only/limited, OSM records only).
Prints ids, tile ids, bytes and counts only: safe for blind/v0.4 location lists (never reads question text).
  python3 -I tilepath.py cities Berlin Lisbon ...          # gazetteer centroid (most populous match, as resolvePlaceIn)
  python3 -I tilepath.py items locs.json [radius_km]        # locs.json = [{"id","lat","lon"}], default radius 25 (RULER-SPEC 5.2)
  python3 -I tilepath.py sweep 1000000                      # all gazetteer places with population >= N
"""
import json, math, sqlite3, sys
G = "<workspace>/shared-data/poi/kit-vgps2/world-places.sqlite"   # sha 215ce466..., carries the tile index
T = "<workspace>/shared-data/poi/geofabrik/work/tiles"             # all 8,374 built tiles (MacBook)
c = sqlite3.connect(f"file:{G}?mode=ro", uri=True)
idx = {r[0]: r[1:] for r in c.execute("select id, size_bytes, pois, vegan from tiles")}

def tid(la, lo):
    la, lo = math.floor(la), math.floor(lo)
    return f"t-{'N' if la >= 0 else 'S'}{abs(la):02d}{'E' if lo >= 0 else 'W'}{abs(lo):03d}"

def ids(lat, lon, km):
    dlat = km / 111.195; dlon = dlat / max(0.01, math.cos(math.radians(lat))); out = []
    for la in range(math.floor(lat - dlat), math.floor(lat + dlat) + 1):
        for lo in range(math.floor(lon - dlon), math.floor(lon + dlon) + 1):
            t = tid(la, ((lo + 180) % 360 + 360) % 360 - 180)
            if t not in out: out.append(t)
    return out

def vegan_near(lat, lon, km, tiles):
    n = only = 0; dl = km / 111.195; dn = dl / max(0.01, math.cos(math.radians(lat)))
    for t in tiles:
        try: d = sqlite3.connect(f"file:{T}/{t}.sqlite?mode=ro", uri=True)
        except sqlite3.Error: continue
        for la, lo, v in d.execute("select lat, lon, vegan from pois where source = 0 and vegan in ('yes','only','limited') "
                                   "and lat between ? and ? and lon between ? and ?", (lat - dl, lat + dl, lon - dn, lon + dn)):
            if math.hypot((la - lat) * 111.195, (lo - lon) * 111.195 * math.cos(math.radians(lat))) <= km:
                n += 1; only += v == "only"
    return n, only

def row(label, lat, lon, km=25):
    want = ids(lat, lon, km); have = [t for t in want if t in idx]; missing = [t for t in want if t not in idx]
    v3, o3 = vegan_near(lat, lon, 3, have); v25, _ = vegan_near(lat, lon, 25, have)
    return {"id": label, "tiles": have, "missing": missing, "bytes": sum(idx[t][0] for t in have), "vegan_3km": v3, "vegan_only_3km": o3, "vegan_25km": v25}

mode = sys.argv[1]
if mode == "cities":
    for name in sys.argv[2:]:
        r = c.execute("select p.name, p.country, p.lat, p.lon from names n join places p on p.id = n.place_id "
                      "where n.name = ? collate nocase order by p.population desc limit 1", (name,)).fetchone()
        print(json.dumps(row(name, r[2], r[3]) | {"resolved": f"{r[0]}, {r[1]}", "lat": round(r[2], 4), "lon": round(r[3], 4)} if r else {"id": name, "resolved": None}, ensure_ascii=False))
elif mode == "items":
    km = float(sys.argv[3]) if len(sys.argv) > 3 else 25
    for it in json.load(open(sys.argv[2])): print(json.dumps(row(it["id"], float(it["lat"]), float(it["lon"]), km)))
elif mode == "sweep":
    rows = c.execute("select lat, lon from places where population >= ?", (int(sys.argv[2]),)).fetchall()
    rs = [row("", la, lo) for la, lo in rows]; mb = sorted(r["bytes"] / 1e6 for r in rs); n = len(rs)
    print(json.dumps({"min_pop": int(sys.argv[2]), "n": n, "no_tile": sum(not r["tiles"] for r in rs),
                      "ge3_vegan_3km": sum(r["vegan_3km"] >= 3 for r in rs), "ge3_vegan_25km": sum(r["vegan_25km"] >= 3 for r in rs),
                      "mb_median": round(mb[n // 2], 2), "mb_p90": round(mb[int(n * .9)], 2), "mb_max": round(mb[-1], 2)}))
