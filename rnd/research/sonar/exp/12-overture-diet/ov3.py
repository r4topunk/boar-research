import duckdb, sqlite3, math, json, re, unicodedata
con = duckdb.connect(); con.execute("INSTALL httpfs; LOAD httpfs; SET s3_region='us-west-2';")
src = "s3://overturemaps-us-west-2/release/2026-09-23.1/theme=places/type=place/*.parquet"
boxes = {"edmonton": (53.3724, 53.7128, -113.7660, -113.1715), "bien-hoa": (10.7600, 11.1149, 106.6403, 107.0084), "queens": (40.5567, 40.8599, -74.0700, -73.6001)}
def norm(s): return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower())
def dist(a, b): return 6371000 * math.hypot(math.radians(b[1] - a[1]) * math.cos(math.radians(a[0])), math.radians(b[0] - a[0]))
res = {}
for city, (y0, y1, x0, x1) in boxes.items():
    ov = con.execute(f"""SELECT names.primary, (bbox.ymin+bbox.ymax)/2, (bbox.xmin+bbox.xmax)/2, taxonomy.primary, confidence, operating_status
        FROM read_parquet('{src}', hive_partitioning=1)
        WHERE bbox.xmin BETWEEN {x0} AND {x1} AND bbox.ymin BETWEEN {y0} AND {y1}
          AND taxonomy.primary IN ('vegan_restaurant','vegetarian_restaurant') AND confidence >= 0.7""").fetchall()
    db = sqlite3.connect(f"file:<workspace>/shared-data/poi/drawn/{city}.sqlite?mode=ro", uri=True)
    osm = db.execute("SELECT name, lat, lon, vegan, vegetarian FROM pois WHERE ref LIKE 'osm%'").fetchall()
    c = {"overture": len(ov), "in_osm_with_diet": 0, "in_osm_no_diet": 0, "not_in_osm": 0, "closed": 0}
    for name, lat, lon, cat, conf, status in ov:
        if status and status != "open": c["closed"] += 1
        n = norm(name); m = [o for o in osm if (n and (norm(o[0]) == n or (len(n) > 5 and (n in norm(o[0]) or norm(o[0]) in n)))) and dist((lat, lon), (o[1], o[2])) < 150]
        if not m: c["not_in_osm"] += 1
        elif any(o[3] or o[4] for o in m): c["in_osm_with_diet"] += 1
        else: c["in_osm_no_diet"] += 1
    res[city] = c; print(city, c, flush=True)
json.dump(res, open("overture-osm-overlap.json", "w"), indent=1)
